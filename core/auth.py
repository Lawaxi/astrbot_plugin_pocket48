import json
from pathlib import Path
import requests
from .headers import get_common_headers


class Pocket48Auth:
    
    TOKEN_FILE = "pocket48_token.json"
    API_URL = "https://pocketapi.48.cn"
    
    def __init__(self, config):
        self.config = config
        self.token = None
        self.user_id = None
        self.channels = []
        self.reload_token()
    
    def reload_token(self):
        if Path(self.TOKEN_FILE).exists():
            try:
                with open(self.TOKEN_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    self.user_id = data.get('user_id')
                    self.channels = data.get('channels', [])
                    return True
            except Exception as e:
                print(f"读取token失败: {e}")
        return False
    
    def login_with_account(self, account: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{self.API_URL}/user/api/v1/login/app/mobile",
                json={"mobile": account, "pwd": password},
                headers=get_common_headers(),
                timeout=10
            )
            data = response.json()
            
            if data.get('status') == 200:
                result = data.get('data', {})
                self.token = result.get('token')
                self.user_id = result.get('userInfo', {}).get('userId')
                self._save_token()
                return True
            else:
                print(f"登录失败: {data.get('message')}")
                return False
        
        except Exception as e:
            print(f"登录异常: {e}")
            return False
    
    def login_with_token(self, token: str) -> bool:
        try:
            response = requests.post(
                f"{self.API_URL}/user/api/v1/user/info/reload",
                json={},
                headers=get_common_headers(token),
                timeout=10
            )
            data = response.json()
            
            if data.get('status') == 200:
                self.token = token
                self.user_id = data.get('content', {}).get('userId')
                self._save_token()
                return True
            else:
                print(f"Token无效: {data.get('message')}")
                return False
        
        except Exception as e:
            print(f"Token验证异常: {e}")
            return False
    
    def add_channel(self, channel_id: int, server_id: int, channel_name: str) -> bool:
        for ch in self.channels:
            if ch.get('channelId') == channel_id:
                return False
        
        self.channels.append({
            'channelId': channel_id,
            'serverId': server_id,
            'channelName': channel_name
        })
        self._save_token()
        return True
    
    def remove_channel(self, channel_id: int) -> bool:
        original_len = len(self.channels)
        self.channels = [ch for ch in self.channels if ch.get('channelId') != channel_id]
        
        if len(self.channels) < original_len:
            self._save_token()
            return True
        return False
    
    def get_channels(self):
        return self.channels
    
    def _save_token(self):
        try:
            with open(self.TOKEN_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'token': self.token,
                    'user_id': self.user_id,
                    'channels': self.channels
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存token失败: {e}")
    
    def get_token(self) -> str:
        return self.token
    
    def get_user_id(self) -> int:
        return self.user_id
    
    def is_authenticated(self) -> bool:
        return self.token is not None
