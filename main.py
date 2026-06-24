import asyncio
import requests
from astrbot.api.star import Star, Context
from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent
import astrbot.api.message_components as Comp
from astrbot.api.event.filter import PlatformAdapterType

from .core.auth import Pocket48Auth
from .core.client import Pocket48Client
from .core.message_handler import MessageHandler
from .core.monitor import MonitorState
from .core.follow import FollowManager

class Pocket48MonitorPlugin(Star):
    
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.cfg = config

        self.target_groups = [
            g.strip() for g in str(config.get('target_groups', '')).split(',')
            if g.strip()
        ]

        self.group_map = {}

        self.auth = Pocket48Auth(config)
        self.client = Pocket48Client(self.auth)
        self.handler = MessageHandler(config)
        self.follow_manager = FollowManager(self.auth, self.client)
        self.monitor_state = MonitorState()

        self._init_auth()

        self.check_interval = config.get('check_interval', 60)
        asyncio.create_task(self._monitor_loop())

        logger.info("Pocket48 Monitor 插件已加载")

    def _init_auth(self):
        login_type = self.cfg.get('login_type', 'token')

        if login_type == 'account':
            account = self.cfg.get('account', '')
            password = self.cfg.get('password', '')
            if account and password:
                if self.auth.login_with_account(account, password):
                    logger.info("账号密码登录成功")
                else:
                    logger.error("账号密码登录失败")
            else:
                logger.error("未配置账号密码")
        else:
            if self.auth.reload_token():
                logger.info("Token已加载")
            else:
                logger.warning("未找到有效Token")

    # ======================
    # 指令
    # ======================

    @filter.command("关注")
    async def follow(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        args = self._parse_command_args(event, "关注")

        if len(args) not in (1, 2):
            msg = "用法：关注 channelId 或 关注 channelId serverId"
        else:
            channel_id = args[0]
            server_id = args[1] if len(args) == 2 else None

            success, msg = await self.follow_manager.follow_channel(channel_id, server_id)

        # ⭐ 绑定群 origin（关键修复）
        group_id = str(getattr(event.message_obj, "group_id", ""))
        self.group_map[group_id] = event.unified_msg_origin

        yield event.chain_result([
            Comp.At(qq=user_id),
            Comp.Plain(f"\n{msg}")
        ])

    def _parse_command_args(self, event: AstrMessageEvent, command_name: str) -> list[str]:
        text = str(getattr(event, "message_str", "") or "").strip()
        parts = text.split()

        if parts and parts[0].lstrip("/") == command_name:
            return parts[1:]
        return parts

    @filter.command("取消关注")
    async def unfollow(self, event: AstrMessageEvent, channel_id: str):
        user_id = str(event.get_sender_id())

        success, msg = await self.follow_manager.unfollow_channel(channel_id)

        yield event.chain_result([
            Comp.At(qq=user_id),
            Comp.Plain(f"\n{msg}")
        ])

    # ======================
    # 监控循环
    # ======================

    async def _monitor_loop(self):
        await asyncio.sleep(5)

        while True:
            try:
                if self.auth.is_authenticated():
                    channels = self.auth.get_channels()
                    if channels:
                        await self._check_messages(channels)

            except Exception as e:
                logger.error(f"监控异常: {e}")

            await asyncio.sleep(self.check_interval)

    async def _check_messages(self, channels):
        for channel_info in channels:
            try:
                channel_id = channel_info.get('channelId')
                server_id = channel_info.get('serverId')
                channel_name = channel_info.get('channelName', '未知房间')

                has_last_time = self.monitor_state.has_last_time(channel_id)
                last_time = self.monitor_state.get_last_time(channel_id)
                max_messages = self.cfg.get('max_messages', 10)

                messages = self.client.get_messages(
                    server_id, channel_id, last_time, max_messages
                )

                if messages:
                    latest_time = 0

                    for msg in messages:
                        latest_time = max(latest_time, msg.get('msgTime', 0))

                    if not has_last_time:
                        self.monitor_state.set_last_time(channel_id, latest_time)
                        logger.info(f"初始化房间 {channel_name} 当前最晚一条消息时间: {latest_time}")
                        continue

                    new_messages = []
                    for msg in messages:
                        msg_id = msg.get('msgId', '')
                        msg_time = msg.get('msgTime', 0)

                        if msg_time <= last_time:
                            continue
                        
                        formatted = self.handler.format_message(msg, channel_name)
                        if formatted:
                            new_messages.append(formatted)

                    if new_messages:
                        try:
                            new_messages.reverse()
                            await self._send_to_groups(new_messages)
                            if latest_time > last_time:
                                self.monitor_state.set_last_time(channel_id, latest_time)
                        except Exception as e:
                            logger.warning(f"房间 {channel_name} 消息发送失败: {e}，本次不更新lasttime")

            except Exception as e:
                logger.error(f"检查房间 {channel_info.get('channelName')} 消息失败: {e}")

    # ======================
    # 发送
    # ======================

    async def _get_client(self):
        for adapter_name in ("AIOCQHTTP", "QQ_OFFICIAL", "SATORI"):
            adapter_type = getattr(PlatformAdapterType, adapter_name, None)
            if not adapter_type:
                continue

            platform = self.context.get_platform(adapter_type)
            if platform and hasattr(platform, "get_client"):
                return platform.get_client()

        return None

    def _download_image(self, image_url: str) -> bytes | None:
        if not image_url:
            return None
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.snh48.com/"
            }
            resp = requests.get(image_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.content
            else:
                logger.info(f"【图片下载提示】状态码异常: {resp.status_code}，本次不插入图片")
                return None
        except Exception as img_err:
            logger.info(f"【图片下载失败】: {img_err}，已自动跳过图片展示")
            return None

    def _build_message_components(self, msg_dict: dict) -> list | None:
        msg_type = msg_dict.get('msg_type')
        text = msg_dict.get('text')
        
        # 纯视频/音频消息，只发送URL
        if msg_type == 'VIDEO' and msg_dict.get('video_url'):
            return [Comp.Video(msg_dict['video_url'])]
        
        if msg_type == 'AUDIO' and msg_dict.get('audio_url'):
            return [Comp.Audio(msg_dict['audio_url'])]
        
        # 有图片的消息
        if msg_dict.get('image_url') and '[image]' in (text or ''):
            image_url = msg_dict['image_url']
            image_data = self._download_image(image_url)
            
            if image_data:
                parts = text.split('[image]')
                components = []
                
                for i, part in enumerate(parts):
                    if part:
                        components.append(Comp.Plain(part))
                    if i < len(parts) - 1:
                        components.append(Comp.Image.fromBytes(image_data))
                
                return components if components else None
            else:
                return [Comp.Plain(text)] if text else None
        
        # 回复音频消息
        if msg_type in ('AUDIO_REPLY', 'AUDIO_GIFT_REPLY') and msg_dict.get('audio_url'):
            return [
                Comp.Audio(msg_dict['audio_url']),
                Comp.Plain('\n' + text) if text else None
            ]
        
        # 翻牌音频/视频
        if msg_type == 'FLIPCARD_AUDIO' and msg_dict.get('audio_url'):
            return [
                Comp.Audio(msg_dict['audio_url']),
                Comp.Plain('\n' + text) if text else None
            ]
        
        if msg_type == 'FLIPCARD_VIDEO' and msg_dict.get('video_url'):
            return [
                Comp.Video(msg_dict['video_url']),
                Comp.Plain('\n' + text) if text else None
            ]
        
        # 普通文本消息
        if text:
            return [Comp.Plain(text)]
        
        return None

    async def _send_to_groups(self, messages: list[dict]):
        client = await self._get_client()

        if not client:
            raise RuntimeError("未找到可用 platform client")

        for msg_dict in messages:
            components = self._build_message_components(msg_dict)
            
            if not components:
                continue
            
            # 过滤None组件
            components = [c for c in components if c is not None]
            
            if not components:
                continue
            
            for group_id in self.target_groups:
                logger.info(f"发送群消息 {group_id}：{msg_dict.get('msg_type')}")

                try:
                    result = await client.api.call_action(
                        "send_group_msg",
                        group_id=int(group_id),
                        message=components,
                    )

                    if not result:
                        logger.warning(f"发送失败: result为空")
                except Exception as e:
                    logger.error(f"发送消息异常: {e}")
