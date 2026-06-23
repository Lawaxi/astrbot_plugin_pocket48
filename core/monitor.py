import json
from pathlib import Path
from typing import Dict


class MonitorState:
    
    STATE_FILE = "pocket48_monitor_state.json"
    
    def __init__(self):
        self.state: Dict[int, int] = {}
        self._load_state()
    
    def _load_state(self):
        if Path(self.STATE_FILE).exists():
            try:
                with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.state = {int(k): v for k, v in data.items()}
            except Exception as e:
                print(f"加载状态失败: {e}")
    
    def get_last_time(self, channel_id: int) -> int:
        return self.state.get(channel_id, 0)

    def has_last_time(self, channel_id: int) -> bool:
        return channel_id in self.state
    
    def set_last_time(self, channel_id: int, timestamp: int):
        self.state[channel_id] = timestamp
        self._save_state()
    
    def _save_state(self):
        try:
            with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f)
        except Exception as e:
            print(f"保存状态失败: {e}")