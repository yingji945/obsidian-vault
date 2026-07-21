# 飞书 Feishu Gateway 显示配置修复

## 问题：Terminal 工具输出泄漏到群聊

当 Hermes 运行 `terminal()` 工具时，`💻 terminal` + 命令内容被作为消息发送到飞书群聊。

## 根因

```python
# gateway/run.py 中的逻辑（约 L14268）：
progress_mode = (
    _env_tp
    if _env_tp and not _tool_progress_configured
    else (_resolved_tp or _env_tp or "all")
)

tool_progress_enabled = progress_mode != "off"  # ← 只认 "off"
```

- `tool_progress: none` 不生效，因为检查条件是 `!= "off"`，而 `"none" != "off"` → True，进度提示继续发送
- 正确的值是 `tool_progress: "off"`（**必须加引号**，否则 YAML 解析为布尔值 False → 被 Python `or` 短路 → 回退到 "all"）

## 修复

```yaml
# config.yaml
display:
  tool_progress: "off"      # ✅ 正确：字符串 "off"，带引号
  # tool_progress: off      # ❌ 错误：YAML 解析为布尔 false
  # tool_progress: none     # ❌ 错误：代码不认，等同于启用
  interim_assistant_messages: false  # 辅助关闭中间消息
```

## 注意

- 修改后需要重启网关生效（`docker restart hermes` 或 `s6-svc -r /run/service/gateway-default/`）
- 不能从网关进程内部重启（会杀死自己），需从宿主或 s6 层面操作
