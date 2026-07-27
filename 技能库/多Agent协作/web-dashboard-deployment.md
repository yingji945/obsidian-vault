# 三省六部圆桌看板 — 部署与远程访问指南

> ⚠️ **2026-07-11 更新：** 自定义网页看板（8899端口方案）已弃用。
> Hermes Dashboard 内置 Kanban 为官方推荐方案，见下方 **方案 B**。

---

## 方案 A（已弃用）：自定义网页看板（8899端口）

**不再使用。** 原因：
- Docker 内网环境下用户无法访问 172.18.0.x 的端口
- 云服务器额外开放 8899 端口增加安全风险
- Hermes Dashboard 已有内置 Kanban 看板

旧架构仅供参考：
```
AutoGen 圆桌 → dashboard_status.json → HTTP Server :8899 → HTML看板
```

## 方案 B（推荐）：Hermes Dashboard 内置 Kanban

### 访问地址
```
http://<宿主机公网IP>:9119/kanban
```

### 前置步骤
```bash
hermes kanban init
```
（只需执行一次，Kanban DB 创建于 `/opt/data/kanban.db`）

### 看板列说明
| 列 | 含义 |
|:--|:------|
| Triage | 原始想法，待整理 |
| Todo | 等待依赖或未分配 |
| Ready | 可被领走执行 |
| In Progress | 正在执行 |
| Blocked | 需要人类介入 |
| Done | 已完成 |

### Kanban CLI
```bash
hermes kanban create "标题" --body "描述"           # 创建任务
hermes kanban list                                  # 列所有任务
hermes kanban show <task_id>                        # 查看详情+评论
hermes kanban comment <task_id> "评论"              # 添加评论
hermes kanban complete <task_id> --summary "总结"   # 完成任务
hermes kanban tail <task_id>                        # 实时跟踪
```

## 云服务器防火墙配置

### 腾讯云轻量应用服务器
1. 控制台 → 轻量应用服务器 → 实例详情 → **防火墙**
2. 添加规则：TCP 9119，来源 0.0.0.0/0

### 阿里云 ECS
1. 控制台 → ECS → 实例 → **安全组**
2. 入方向规则：TCP 9119/9119，授权对象 0.0.0.0/0

## 飞书实时卡片（无需网页）

网页看板不是必须的 — 飞书实时卡片每轮发言自动更新，无需配置任何网络。

## 故障排查

| 症状 | 原因 | 解决 |
|:----|:-----|:-----|
| Dashboard 能打开但 Kanban 页无内容 | Kanban DB 未初始化 | `hermes kanban init` |
| Kanban 页显示 0 个任务 | 尚未创建任务 | `hermes kanban create` |
| 9119 端口无法访问 | 云防火墙未开放 | 检查安全组 TCP 9119 |
| Dashboard 容器未启动 | 服务挂了 | `docker compose up -d hermes-dashboard` |
| 浏览器连不上 82.156.210.39 | 公网 IP 变了或容器重启 | 检查宿主机 IP + docker ps |
