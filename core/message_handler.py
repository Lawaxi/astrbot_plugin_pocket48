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
        'AUDIO_REPLY': '回复语音',
        'AUDIO_GIFT_REPLY': '礼物回复语音',
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
    
    def _apply_placeholders(self, template: str, replacements: Dict[str, str]) -> str:
        result = template
        for key, value in replacements.items():
            if value is not None:
                result = result.replace(f'[{key}]', str(value))
        return result
    
    def _append_timestamp(self, text: str, message: Dict) -> str:
        ts = message.get('msgTime', 0)
        if ts:
            time_str = self._format_timestamp(ts)
            return f"{text}{time_str}"
        return text
    
    def format_message(self, message: Dict, channel_name: str = '未知房间') -> Optional[Dict]:
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
            
            result = {
                'msg_type': msg_type,
                'text': None,
                'image_url': None,
                'video_url': None,
                'audio_url': None,
            }
            
            if msg_type == 'TEXT':
                fmt = self.cfg.get('message_format', '【[channel]】\n[user]: [content]')
                text = self._apply_placeholders(fmt, {'channel': channel_name, 'user': nick_name, 'content': body})
                result['text'] = self._append_timestamp(text, message)
            
            elif msg_type == 'GIFT_TEXT':
                try:
                    body_obj = json.loads(body)
                    gift_info = body_obj.get('giftInfo', {})
                    fmt = self.cfg.get('gift_format', '【[channel]】\n[user]: 送给 [gift_to] [gift_num]个[gift_name]')
                    text = self._apply_placeholders(fmt, {
                        'channel': channel_name,
                        'user': nick_name,
                        'gift_to': gift_info.get('userName', ''),
                        'gift_num': gift_info.get('giftNum', ''),
                        'gift_name': gift_info.get('giftName', '')
                    })
                    result['text'] = self._append_timestamp(text, message)
                except:
                    return None
            
            elif msg_type == 'REPLY':
                try:
                    body_obj = json.loads(body)
                    reply_info = body_obj.get('replyInfo', {})
                    fmt = self.cfg.get('reply_format', '【[channel]】\n[user]: [content]\n------\n[reply_user]: [reply_content]')
                    text = self._apply_placeholders(fmt, {
                        'channel': channel_name,
                        'user': nick_name,
                        'content': reply_info.get('text', ''),
                        'reply_user': reply_info.get('replyName', ''),
                        'reply_content': reply_info.get('replyText', '')
                    })
                    result['text'] = self._append_timestamp(text, message)
                except:
                    return None
            
            elif msg_type == 'GIFTREPLY':
                try:
                    body_obj = json.loads(body)
                    reply_info = body_obj.get('giftReplyInfo', {})
                    fmt = self.cfg.get('reply_format', '【[channel]】\n[user]: [content]\n------\n[reply_user]: [reply_content]')
                    text = self._apply_placeholders(fmt, {
                        'channel': channel_name,
                        'user': nick_name,
                        'content': reply_info.get('text', ''),
                        'reply_user': reply_info.get('replyName', ''),
                        'reply_content': reply_info.get('replyText', '')
                    })
                    result['text'] = self._append_timestamp(text, message)
                except:
                    return None
            
            elif msg_type == 'LIVEPUSH':
                try:
                    body_obj = json.loads(body)
                    live_info = body_obj.get('livePushInfo', {})
                    result['image_url'] = live_info.get('liveCover')
                    fmt = self.cfg.get('live_format', '【[channel]】\n[user] 发起直播：[image]\n[live_title]')
                    text = self._apply_placeholders(fmt, {
                        'channel': channel_name,
                        'user': nick_name,
                        'image': '[image]',
                        'live_title': live_info.get('liveTitle', '')
                    })
                    result['text'] = self._append_timestamp(text, message)
                except:
                    return None
            
            elif msg_type == 'IMAGE':
                try:
                    body_obj = json.loads(body)
                    result['image_url'] = body_obj.get('url', '')
                    fmt = self.cfg.get('image_format', '【[channel]】\n[user]: [image]')
                    text = self._apply_placeholders(fmt, {
                        'channel': channel_name,
                        'user': nick_name,
                        'image': '[image]'
                    })
                    result['text'] = self._append_timestamp(text, message)
                except:
                    return None
            
            elif msg_type == 'EXPRESSIMAGE':
                try:
                    body_obj = json.loads(body)
                    image_info = body_obj.get('expressImgInfo', {})
                    result['image_url'] = image_info.get('emotionPattern', '')
                    fmt = self.cfg.get('image_format', '【[channel]】\n[user]: [image]')
                    text = self._apply_placeholders(fmt, {
                        'channel': channel_name,
                        'user': nick_name,
                        'image': '[image]'
                    })
                    result['text'] = self._append_timestamp(text, message)
                except:
                    return None

            elif msg_type == 'VIDEO':
                try:
                    body_obj = json.loads(body)
                    result['video_url'] = body_obj.get('url', '')
                except:
                    return None

            elif msg_type == 'AUDIO':
                try:
                    body_obj = json.loads(body)
                    result['audio_url'] = body_obj.get('url', '')
                except:
                    return None
            
            elif msg_type == 'AUDIO_REPLY':
                try:
                    body_obj = json.loads(body)
                    reply_info = body_obj.get('replyInfo', {})
                    result['audio_url'] = reply_info.get('voiceUrl', '')
                    fmt = self.cfg.get('reply_format', '------\n[reply_user]: [reply_content]')
                    text = self._apply_placeholders(fmt, {
                        'reply_user': reply_info.get('replyName', ''),
                        'reply_content': reply_info.get('replyText', '')
                    })
                    result['text'] = self._append_timestamp(text, message)
                except:
                    return None
            
            elif msg_type == 'AUDIO_GIFT_REPLY':
                try:
                    body_obj = json.loads(body)
                    reply_info = body_obj.get('giftReplyInfo', {})
                    result['audio_url'] = reply_info.get('voiceUrl', '')
                    fmt = self.cfg.get('reply_format', '------\n[reply_user]: [reply_content]')
                    text = self._apply_placeholders(fmt, {
                        'reply_user': reply_info.get('replyName', ''),
                        'reply_content': reply_info.get('replyText', '')
                    })
                    result['text'] = self._append_timestamp(text, message)
                except:
                    return None
            
            elif msg_type in ['FLIPCARD', 'FLIPCARD_AUDIO', 'FLIPCARD_VIDEO']:
                try:
                    body_obj = json.loads(body)
                    card_info = body_obj.get('filpCardInfo', {})
                    answer = card_info.get('answer', '')
                    
                    if msg_type == 'FLIPCARD' and isinstance(answer, str):
                        fmt = self.cfg.get('flipcard_format', '【[channel]】翻牌\n[user]: [answer]\n------\nQ: [question]')
                        text = self._apply_placeholders(fmt, {
                            'channel': channel_name,
                            'user': nick_name,
                            'answer': answer,
                            'question': card_info.get('question', '')
                        })
                        result['text'] = self._append_timestamp(text, message)
                    elif msg_type == 'FLIPCARD_AUDIO':
                        result['audio_url'] = answer if isinstance(answer, str) else answer.get('url', '')
                        fmt = self.cfg.get('flipcard_reply_format', '------\nQ: [question]')
                        text = self._apply_placeholders(fmt, {'question': card_info.get('question', '')})
                        result['text'] = self._append_timestamp(text, message)
                    elif msg_type == 'FLIPCARD_VIDEO':
                        result['video_url'] = answer if isinstance(answer, str) else answer.get('url', '')
                        fmt = self.cfg.get('flipcard_reply_format', '------\nQ: [question]')
                        text = self._apply_placeholders(fmt, {'question': card_info.get('question', '')})
                        result['text'] = self._append_timestamp(text, message)
                except:
                    return None
            
            else:
                fmt = self.cfg.get('message_format', '【[channel]】\n[user]: [content]')
                text = self._apply_placeholders(fmt, {'channel': channel_name, 'user': nick_name, 'content': body})
                result['text'] = self._append_timestamp(text, message)
            
            return result
        
        except Exception as e:
            print(f"格式化消息失败: {e}")
            return None
