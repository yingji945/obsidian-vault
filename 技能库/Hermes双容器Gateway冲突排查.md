---
created: 2026-08-05
updated: 2026-08-05
tags: [技能库, Hermes运维, 排障, 双容器, gateway]
---

# Hermes 双容器 Gateway 冲突排查（dashboard 容器误启 gateway）

> 现象：cron 投递飞书**间歇性**失败 `delivery error: Feishu dependencies not installed`，
> 但飞书对话（live gateway）一直正常。
> 结论：不是缺包，是**环境变量传播陷阱 + 第二个 Hermes 容器抢 cron** 的双重叠加。

## 一句话总结

服务器上存在**两个 Hermes 容器**共享同一份 `/opt/data`（HERMES_HOME）：
主容器 `hermes`（gateway，服务飞书对话）+ `hermes-dashboard`（看板 Web UI）。
dashboard 容器本应只跑看板，但 Hermes 镜像的 dashboard 检测逻辑在 s6-overlay v3 下失效，
导致它也自动注册并启动了 `gateway-default`（第二个 gateway）——两个 gateway 抢同一个
cron 队列，dashboard 那个没有 PYTHONPATH，抢到任务就投递失败。

## 完整因果链

```
用户最初只装了一个 Hermes（主容器 hermes）
  └→ 后来为了三省六部圆桌看板，在 docker-compose.yml 新增 hermes-dashboard 服务
       （同一镜像，command: dashboard --host 0.0.0.0 --insecure，端口 9119）
  └→ dashboard 容器启动时，s6 的 /etc/cont-init.d/02-reconcile-profiles 运行
       hermes_cli/container_boot.py，本应检测到"这是 dashboard 容器"并跳过 gateway 注册
  └→ 但检测读 /proc/1/cmdline 期望前缀 "init main-wrapper.sh hermes ..."
       实际 s6-overlay v3 的 PID 1 argv 是 "s6-svscan -d4 -- /run/service" → 检测失败
  └→ dashboard 容器被当作普通 gateway 容器 → reconcile 读到共享 gateway_state.json
       (desired_state=running) → 注册 gateway-default 并自动启动
  └→ 两个 gateway 都跑 "In-process cron scheduler"，抢同一 cron/jobs.json
  └→ dashboard 的 gateway 环境 HOME=/root 无 PYTHONPATH → lark_oapi 不可见
       → FEISHU_AVAILABLE=False → 抢到任务投递报 "Feishu dependencies not installed"
```

## 诊断要点

| 信号 | 含义 |
|:-----|:-----|
| `In-process cron scheduler started` 在启动日志出现 **2 次**（间隔~10s） | 两个 gateway 都注册了 cron scheduler |
| 日志出现 `another gateway already holds the dispatcher lock` | 双 gateway 并存 |
| `docker ps` 同时有 `hermes` + `hermes-dashboard` | 第二个容器在跑 |
| `docker exec hermes-dashboard ps aux \| grep gateway` 有进程 | dashboard 容器误启 gateway |
| delivery error 是**间歇性**（同任务有时成功有时失败，无环境变更） | 双 gateway 抢队列的特征 |

## 根治修复（dashboard 容器只需要看板，不需要 gateway）

**核心思路**：让 reconcile 读到 `desired_state=stopped` → 只注册槽、不启动 gateway。

```yaml
# docker-compose.yml → hermes-dashboard 服务 → volumes:
- /home/ubuntu/hermes/data/dashboard-gateway-state.json:/opt/data/gateway_state.json:ro
```

`dashboard-gateway-state.json` 内容：
```json
{"gateway_state": "stopped", "desired_state": "stopped", "reason": "dashboard container: gateway disabled via compose override"}
```

**⚠️ 关键坑**：
1. **必须 `docker compose up -d <service>` 重建容器**，`docker restart` 不应用 compose 改动（会白跑一轮）
2. **`HERMES_GATEWAY_NO_SUPERVISE=1` 无效**（2026-08-05 实测）——它只影响 bare `gateway run` 命令的派发，管不到 s6 reconcile 自动注册
3. 改 compose 用脚本 + 备份，插入 volumes 段时注意**服务段边界**（找下一个 2 空格顶层键），避免 YAML 重复键

## 配套止血（不能少）

即使根治了 gateway，dashboard 容器的 cron 子进程仍可能缺 PYTHONPATH（如果它还在跑），
所以 dashboard 服务 environment 也要加：
```yaml
environment:
  - PYTHONPATH=/opt/data/home/.local/lib/python3.13/site-packages
```

## 验证

```bash
# 1. dashboard 容器 gateway 应消失，只剩看板：
docker exec hermes-dashboard ps aux | grep -E "gateway|dashboard"
#    预期：hermes dashboard 进程在，gateway 进程无

# 2. 主容器 gateway 存活：
pgrep -af "hermes gateway run"

# 3. cron 投递恢复正常（无新 delivery 报错）：
tail -20 /opt/data/logs/errors.log | grep -i delivery

# 4. 实弹验证（手动触发之前必报错的任务）：
#    日志出现 "delivered to feishu:... via live adapter ✅" 即成功
```

## 修复脚本存档

- `fix_dashboard_gateway.py` — 止血：dashboard 服务补 PYTHONPATH + NO_SUPERVISE（v1）
- `fix_dashboard_gateway_root.py` — 根治：创建 stopped state 文件 + 挂载（注意：v1 插入 volumes 有 YAML 重复键 bug）
- `fix_dashboard_gateway_v2.py` — 修正版：恢复备份 + 正确识别服务段边界插入 + `docker compose config` 自检

## 教训

1. 排查 cron 投递失败先看**有没有第二个 Hermes 实例**（共享 HERMES_HOME 的容器），再查环境变量
2. 双容器共享 HERMES_HOME 时，`gateway_state.json` 会被后启动的 gateway **覆盖**——它的 pid 字段可能指向 dashboard 容器的 gateway，不能信这个文件判断 live gateway
3. 改 docker-compose.yml 一律：备份 → 脚本化修改 → `docker compose config -q` 校验 → 重建（不是 restart）
4. 给用户的命令保持单行可粘贴；宿主机操作用写脚本到共享卷的方式

## 相关文件

- Hermes 源码：`/opt/hermes/hermes_cli/container_boot.py`（`_is_dashboard_container`、`_register_service`）
- s6 启动：`/opt/hermes/docker/cont-init.d/02-reconcile-profiles`、`/opt/hermes/docker/s6-rc.d/`
- 知识库关联：`技能库/Cron联网任务脚本化方案.md`、`技能库/Hermes跨平台会话接续规范.md`
