from typing import Optional

from astrbot.api import logger
from .client import EncryptedRoomError, Pocket48ClientError


class FollowManager:
    
    def __init__(self, auth, client):
        self.auth = auth
        self.client = client
    
    async def follow_channel(self, channel_id: int, server_id: Optional[int] = None) -> tuple[bool, str]:
        try:
            channel_id = int(channel_id)
        except (ValueError, TypeError):
            return False, "房间号格式错误"

        if server_id is not None:
            try:
                server_id = int(server_id)
            except (ValueError, TypeError):
                return False, "serverId 格式错误"

            room_info = {
                'channelId': channel_id,
                'serverId': server_id,
                'channelName': f"加密房间 {channel_id}"
            }
        else:
            try:
                room_info = self.client.get_room_info(channel_id)
            except EncryptedRoomError as e:
                return False, str(e)
            except Pocket48ClientError as e:
                return False, str(e)

        channel_name = room_info.get('channelName', '未知房间')
        success = self.auth.add_channel(channel_id, server_id, channel_name)
        
        if success:
            logger.info(f"成功关注房间: {channel_name} (channelId: {channel_id}, serverId: {server_id})")
            return True, f"✅ 成功关注 {channel_name}"
        else:
            return False, f"❌ 已关注过房间：{channel_name}"
    
    async def unfollow_channel(self, channel_id: int) -> tuple[bool, str]:
        try:
            channel_id = int(channel_id)
        except (ValueError, TypeError):
            return False, "房间号格式错误"
        
        channel_name = None
        for ch in self.auth.get_channels():
            if ch.get('channelId') == channel_id:
                channel_name = ch.get('channelName', '未知房间')
                break
        
        if not channel_name:
            return False, f"未找到关注的房间（房间号：{channel_id}）"
        
        success = self.auth.remove_channel(channel_id)
        
        if success:
            logger.info(f"取消关注房间: {channel_name} (channelId: {channel_id})")
            return True, f"✅ 已取消关注 {channel_name}"
        else:
            return False, f"❌ 取消关注失败"
