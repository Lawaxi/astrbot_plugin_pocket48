# Pocket48 Monitor - AstrBot 插件

实时监控口袋48平台的房间消息，并自动转发到QQ群。

## 🚀 功能

- 📱 实时监控多个口袋48房间
- 💬 自动转发房间消息到QQ群
- 🔑 支持账号密码和Token两种登录方式
- 📝 灵活的消息格式配置
- 🎯 支持消息类型过滤
- 💾 本地文件存储（无数据库）

## 📋 支持的消息类型

| 类型 | 说明 |
|------|------|
| TEXT | 文本消息 |
| GIFT_TEXT | 礼物消息 |
| IMAGE | 图片 |
| VIDEO | 视频 |
| AUDIO | 语音 |
| EXPRESSIMAGE | 表情 |
| REPLY | 回复消息 |
| GIFTREPLY | 礼物回复 |
| LIVEPUSH | 直播推送 |
| FLIPCARD | 翻牌 |
| FLIPCARD_AUDIO | 翻牌语音 |
| FLIPCARD_VIDEO | 翻牌视频 |

## ⚙️ 配置

在 AstrBot 管理面板中配置以下项目：

### 基础配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| target_groups | 目标QQ群号（逗号分隔） | 764687233,123456 |
| room_ids | 口袋48房间号（逗号分隔） | 123456,789012 |

### 登录配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| login_type | 登录方式：account 或 token | token |
| account | 口袋48账号（当login_type为account时） | user@example.com |
| password | 口袋48密码（当login_type为account时） | password123 |

**Token登录说明**：
- 首次自动使用账号密码登录，Token保存在 `pocket48_token.json`
- 后续自动使用本地Token，无需重复登录

### 监控配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| check_interval | 检查间隔（秒） | 60 |
| max_messages | 每次最多获取消息数 | 10 |
| include_types | 包含的消息类型（逗号分隔，留空表示全部） | 空 |
| exclude_types | 排除的消息类型（逗号分隔） | 空 |

### 消息格式配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| message_format | 普通消息格式 | 【%s】%s: %s |
| reply_format | 回复消息格式 | 【回复】%s 回复 %s: %s |
| live_format | 直播消息格式 | 【直播】%s 发起直播：%s |
| flipcard_format | 翻牌消息格式 | 【翻牌】%s\nQ: %s\nA: %s |

**格式说明**：
- `%s` 对应不同参数（房间名/昵称/消息内容等）
- 请按顺序调整 `%s` 的位置

## 📦 安装

```bash
unzip pocket48_monitor.zip
cp -r pocket48_monitor /path/to/astrbot/plugins/
cd pocket48_monitor
pip install -r requirements.txt
```

## 🚀 快速开始

1. **启动 AstrBot**
   ```bash
   astrbot run
   ```

2. **打开管理面板** 
   - http://localhost:6099

3. **配置 Pocket48 Monitor 插件**
   - 填入目标群号：`764687233`
   - 填入房间号：`123456,789012`
   - 选择登录方式：`account` 或 `token`
   - 如果选择 `account`，填入账号密码

4. **保存设置**
   - 插件自动重启并开始监控

## 📝 使用示例

### 消息格式示例

**原始格式**：`message_format: 【%s】%s: %s`
- 房间名：SNH48 剧场
- 昵称：林忆宁
- 消息：今天天气真好

**输出**：`【SNH48 剧场】林忆宁: 今天天气真好`

### 消息类型过滤

**只接收文本和回复消息**：
```
include_types: TEXT,REPLY
exclude_types: 
```

**排除礼物消息**：
```
include_types: 
exclude_types: GIFT_TEXT
```

## 💾 文件说明

| 文件 | 说明 |
|------|------|
| pocket48_token.json | 保存的登录Token |
| pocket48_monitor_state.json | 监控状态（每个房间最后获取的时间） |
| README.md | 本说明文档 |

## 🔧 故障排除

### 登录失败

- 检查账号密码是否正确
- 确保网络连接正常
- 查看 AstrBot 日志获取详细错误信息

### 无法获取消息

- 确认房间号是否正确
- 检查Token是否过期（删除 `pocket48_token.json` 重新登录）
- 确保登录用户有权访问该房间

### 消息未转发到群

- 检查目标群号配置是否正确
- 确认机器人已加入目标群
- 检查机器人是否有群聊权限

## 📊 监控流程

1. 每隔 `check_interval` 秒检查一次
2. 获取每个房间的新消息
3. 检查消息类型是否满足过滤条件
4. 格式化消息内容
5. 转发到所有目标群

## 🔐 安全建议

- 不要在代码中硬编码密码
- 定期更改口袋48密码
- Token会自动保存在 `pocket48_token.json`，请妥善保管
- 不要将Token文件上传到公共代码库

## ⚠️ 注意事项

- 监控间隔不建议设置过短（可能被限流）
- 建议间隔 30-60 秒
- Token有有效期，过期后会自动使用账号密码重新登录
- 房间消息会实时缓存，防止重复转发

## 📞 支持

如遇问题，请：
1. 查看 AstrBot 日志
2. 确认配置是否正确
3. 尝试删除 `pocket48_token.json` 重新登录

## 📄 许可证

MIT License
