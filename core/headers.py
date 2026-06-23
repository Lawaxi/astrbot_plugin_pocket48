import json
from typing import Optional


def get_common_headers(token: Optional[str] = None) -> dict:
    """封装官方必需的公共请求头。"""
    headers = {
        "content-type": "application/json;charset=utf-8",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "PocketFans201807/7.1.39 (iPhone; iOS 18.7.1; Scale/3.00)",
        "p-sign-type": "V0",
        "pa": "MTc4MjE4NjQyMjAwMCwzOTIsNkM4NkU1MURFQzczMjg1QzY3N0Y0REIzMTVBOUIyRjgs",
        "appinfo": json.dumps({
            "vendor": "apple",
            "deviceId": "F2BA149C-06DB-9843-31DE-36BF375E36F2",
            "appVersion": "7.1.39",
            "appBuild": "26052601",
            "osVersion": "18.7.1",
            "osType": "ios",
            "deviceName": "iPhone 13",
            "os": "ios"
        }, separators=(',', ':'))
    }

    if token:
        headers["token"] = token

    return headers
