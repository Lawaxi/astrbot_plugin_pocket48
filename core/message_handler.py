import json
import time
from typing import Optional, Dict
from datetime import datetime


class MessageHandler:
    
    MESSAGE_TYPES = {
        'TEXT': '文本',
        'GIFT_TEXT': '礼物',
        'AUDIO': '语音',
        'IMAGE': '图片',
        'VIDEO': '视频',
        'EXPRESSIMAGE': '表情',
        'REPLY': '回复',
        'GIFTREPLY': '礼物回复',
        'LIVEPUSH': '直播',
        'SHARE_LIVE': '分享直播',
        'FLIPCARD': '翻牌',
        'FLIPCARD_AUDIO': '翻牌语音',
        'FLIPCARD_VIDEO': '翻牌视频',
        'PASSWORD_REDPACKAGE': '密码红包',
        'VOTE': '投票',
        'SHARE_POSTS': '分享帖子'
    }
    
    def __init__(self, cfg):
        self.cfg = cfg
    
    def _format_timestamp(self, ts_ms: int) -> str:
        ts = ts_ms / 1000
        return datetime.fromtimestamp(ts).strftime(self.cfg.get('time_format', '\n%Y-%m-%d %H:%M:%S'))
    
    def should_process(self, msg_type: str) -> bool:
        include = self.cfg.get('include_types', '').strip()
        exclude = self.cfg.get('exclude_types', '').strip()
        
        if include:
            types = [t.strip() for t in include.split(',')]
            return msg_type in types
        
        if exclude:
            types = [t.strip() for t in exclude.split(',')]
            return msg_type not in types
        
        return True
    
    def _build_output(self, formatted: str, message: Dict) -> str:
        ts = message.get('msgTime', 0)
        time_str = self._format_timestamp(ts) if ts else ''
        return f"{formatted}{time_str}"
    
    def format_message(self, message: Dict, channel_name: str = '未知房间') -> Optional[str]:
        msg_type = message.get('msgType', 'TEXT')
        
        if not self.should_process(msg_type):
            return None
        
        try:
            ext_info = message.get('extInfo', {})
            if isinstance(ext_info, str):
                ext_info = json.loads(ext_info)
            
            user = ext_info.get('user', {})
            nick_name = user.get('nickName', '') 
            body = message.get('bodys', '')
            
            formatted = None
            
            if msg_type == 'TEXT':
                fmt = self.cfg.get('message_format', '【%s】\n%s: %s')
                formatted = fmt % (channel_name, nick_name, body)
            
            elif msg_type == 'GIFT_TEXT':
                try:
                    body_obj = json.loads(body)
                    gift_info = body_obj.get('giftInfo', {})
                    gift_text = f"送给 {gift_info.get('userName', '未知')} {gift_info.get('giftNum', 1)}个{gift_info.get('giftName', '礼物')}"
                    fmt = self.cfg.get('message_format', '【%s】\n%s: %s')
                    formatted = fmt % (channel_name, nick_name, gift_text)
                except:
                    return None
            
            elif msg_type == 'REPLY':
                try:
                    body_obj = json.loads(body)
                    reply_info = body_obj.get('replyInfo', {})
                    fmt = self.cfg.get('reply_format', '【回复】\n%s 回复 %s: %s')
                    formatted = fmt % (nick_name, reply_info.get('replyName', '未知'), reply_info.get('text', ''))
                except:
                    return None
            
            elif msg_type == 'GIFTREPLY':
                try:
                    body_obj = json.loads(body)
                    reply_info = body_obj.get('giftReplyInfo', {})
                    fmt = self.cfg.get('reply_format', '【回复】\n%s 回复 %s: %s')
                    formatted = fmt % (nick_name, reply_info.get('replyName', '未知'), reply_info.get('text', ''))
                except:
                    return None
            
            elif msg_type == 'LIVEPUSH':
                try:
                    body_obj = json.loads(body)
                    live_info = body_obj.get('livePushInfo', {})
                    fmt = self.cfg.get('live_format', '【直播】\n%s 发起直播：%s')
                    formatted = fmt % (nick_name, live_info.get('liveTitle', '直播'))
                except:
                    return None
            
            elif msg_type in ['FLIPCARD', 'FLIPCARD_AUDIO', 'FLIPCARD_VIDEO']:
                try:
                    body_obj = json.loads(body)
                    card_info = body_obj.get('filpCardInfo', {})
                    fmt = self.cfg.get('flipcard_format', '【翻牌】\n%s\nQ: %s\nA: %s')
                    formatted = fmt % (nick_name, card_info.get('question', ''), card_info.get('answer', ''))
                except:
                    return None
            
            elif msg_type in ['IMAGE', 'VIDEO', 'AUDIO']:
                fmt = self.cfg.get('message_format', '【%s】\n%s: %s')
                type_name = self.MESSAGE_TYPES.get(msg_type, msg_type)
                formatted = fmt % (channel_name, nick_name, f"[{type_name}]")
            
            else:
                fmt = self.cfg.get('message_format', '【%s】\n%s: %s')
                type_name = self.MESSAGE_TYPES.get(msg_type, msg_type)
                formatted = fmt % (channel_name, nick_name, f"[{type_name}]{body[:50]}")
            
            if formatted:
                return self._build_output(formatted, message)
            return None
        
        except Exception as e:
            print(f"格式化消息失败: {e}")
            return None
