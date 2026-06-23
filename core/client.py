import requests
import json
from typing import List, Dict
from .headers import get_common_headers


class Pocket48ClientError(Exception):
    """Pocket48 API 调用失败。"""


class EncryptedRoomError(Pocket48ClientError):
    """房间需要手动提供 serverId。"""


class Pocket48Client:
    
    API_URL = "https://pocketapi.48.cn"
    
    def __init__(self, auth):
        self.auth = auth

    def get_messages(self, server_id: int, channel_id: int, last_time: int = 0, limit: int = 10) -> List[Dict]:
        if not self.auth.is_authenticated():
            raise Pocket48ClientError("未登录或 Token 无效")
        
        try:
            url = f"{self.API_URL}/im/api/v1/team/message/list/homeowner"
            
            payload_dict = {
                "serverId": str(server_id),
                "channelId": str(channel_id),
                "lastTime": last_time,
                "limit": limit
            }
            data_bytes = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')
            
            headers = get_common_headers(self.auth.get_token())
            response = requests.post(url, data=data_bytes, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 200:
                messages = data.get('content', {}).get('message', [])
                return messages
            else:
                message = data.get('message', '未知错误')
                raise Pocket48ClientError(f"获取消息失败 (channel {channel_id}): {message}")
        
        except Exception as e:
            if isinstance(e, Pocket48ClientError):
                raise
            raise Pocket48ClientError(f"获取消息异常: {e}") from e
    
    def get_room_info(self, channel_id: int) -> Dict:
        if not self.auth.is_authenticated():
            raise Pocket48ClientError("未登录或 Token 无效")
        
        try:
            url = f"{self.API_URL}/im/api/v1/im/team/room/info"
            
            payload_dict = {"channelId": str(channel_id)}
            data_bytes = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')
            
            headers = get_common_headers(self.auth.get_token())
            
            response = requests.post(url, data=data_bytes, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 200:
                if data.get('questionId', '') != '':
                    raise EncryptedRoomError(
                        "这是加密房间，请使用「/关注 channelId serverId」手动关注"
                    )

                content = data.get('content', {})
                channel_info = content.get('channelInfo', {})
                server_id = channel_info.get('serverId')
                channel_name = channel_info.get('channelName')

                return {
                    'channelId': channel_id,
                    'serverId': server_id,
                    'channelName': channel_name or f"房间 {channel_id}"
                }
            else:
                message = data.get('message', '未知错误')
                raise Pocket48ClientError(f"获取房间信息失败：{message}") #房间不存在
        
        except Exception as e:
            if isinstance(e, Pocket48ClientError):
                raise
            raise Pocket48ClientError(f"获取房间信息异常: {e}") from e
