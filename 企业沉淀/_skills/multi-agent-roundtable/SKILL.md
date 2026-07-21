---
name: multi-agent-roundtable
description: "多Agent协作（三省六部圆桌/飞书多Bot协作/知识库自动化）：AutoGen辩论、角色定义、飞书bot协作协议、GitHub知识库沉淀"
version: 1.5.0
---

# 多Agent圆桌讨论（三省六部模式）

## 适用场景
- 复杂决策需要多方交叉验证（活动方案评审、策略评估）
- 单个Agent视角不够，需要运营+财务+法务等多角度
- 用户希望看到不同观点的辩论和分歧，而不是单一结论
- 需要实时在 Web 上观看辩论过程

## 架构

```
用户 → Hermes（我）→ AutoGen 圆桌
                         ├── 运营大臣 🏪
                         ├── 财务大臣 💰
                         ├── 法务大臣 ⚖️
                         ├── 数据大臣 📊
                         └── 情报大臣 🔍
                   讨论结果 → 三通道分发
                         ├── 🎥 飞书卡片（实时文字直播）
                         ├── 📋 Hermes Kanban（任务进度追踪）
                         └── 🌐 Web 辩论看板（自动刷新聊天界面）
```

## 三省六部角色定义（针对瑞幸运营负责人的定制方案）

### 三省（决策层）

| 省 | 角色 | 职责 |
|:--|:-----|:------|
| 中书省 | 用户本人 | 最终决策，拍板 |
| 门下省 | 审核大臣 | 方案复核、风险把关、数据验证 |
| 尚书省 | 调度大臣 | 任务协调、进度跟踪、资源分配 |

### 六部（执行层）

| 部 | 大臣 | 专长 |
|:--|:-----|:------|
| 📊 户部 | 数据大臣 | SQL取数、漏斗分析、AB实验、埋点校验 |
| 🎯 礼部 | 运营大臣 | 活动策划、积分商城、用户触达、扫码活动 |
| 🧬 吏部 | 分层大臣 | 用户生命周期、留存分析、沉睡预警、用户分群 |
| 🔬 工部 | 算法大臣 | 标签体系、预测模型、ML落地、算法评估 |
| ⚖️ 刑部 | 法务大臣 | 合规审查、备案、个税、隐私、反作弊 |
| 🔍 兵部 | 情报大臣 | 竞品研究、行业动态、市场分析、新机会 |

### 分阶段上线计划

### Phase 1（本周）：3部先跑通
1. 数据大臣 📊 — 日常SQL查询、数据看板
2. 运营大臣 🎯 — 活动方案分析、策略评估
3. 法务大臣 ⚖️ — 新活动的合规审查

### Phase 2（下周）：加到5部
4. 分层大臣 🧬 — 生命周期自动化分析
5. 情报大臣 🔍 — 每周竞品动态

### Phase 3（规划中）：全军出击
6. 算法大臣 🔬 — 标签模型评估
7. 审核大臣 — 门下省把关
8. 调度大臣 — 尚书省协调

## 层级式多Agent架构（大脑+手脚模式）

### 核心思想

Hermes 不是万能的。三省六部的大脑能力很强，但 IM 通道、文件存储、特定 API 对接这些脏活，应该交给更成熟的工具去干。

```
用户 → 飞书/CLI
  │
  ▼
Hermes（三省六部 ← 大脑：编排、工具链、多Agent辩论）
  │
  ├── Tool: terminal / browser / web_search
  ├── Tool: 开放工具（← 手脚：IM收发、消息路由）
  └── Tool: ...
```

### 技术方案

**Hermes 通过 Tool 控制外部工具**
```
三省六部 → 调 hermes kanban create/comment/complete → Kanban 看板
三省六部 → 调 terminal("python3 debate_server.py") → Web 辩论看板
三省六部 → 调 Feishu API PATCH → 飞书实时卡片
```

### AutoGen 配置
- DashScope API 是 OpenAI 兼容接口，AutoGen 可直接对接
- 每个 Agent 用 `AssistantAgent`，配上独立的 `system_message`
- 用 `GroupChat` 做圆桌会议室
- 不同角色可配不同模型（如法务用更严谨的模型）

### 圆桌 vs 并行

| | 并行（delegate_task） | 真圆桌（AutoGen） |
|:----|:-------------------|:-----------------|
| Agent能否看到彼此 | ❌ 不能 | ✅ 能，实时看到 |
| 能否互相反驳 | ❌ 不能 | ✅ 能辩论 |
| 能否达成共识 | ❌ 我强行汇总 | ✅ 自然讨论出结论 |

---

## 部署实战记录（2026-07-06，已验证可运行）

### 环境
- Python 3.13.5, uv 0.11.6, Docker s6-overlay
- 网络：国内网络，使用 Tsinghua PyPI 镜像
- DashScope API（通义千问 qwen-max），OpenAI兼容接口
- Hermes Agent + Feishu 飞书网关

### 安装
```bash
uv pip install pyautogen -i https://pypi.tuna.tsinghua.edu.cn/simple
uv pip install "autogen-ext[openai]" -i https://pypi.tuna.tsinghua.edu.cn/simple
```
安装包：pyautogen==0.10.0, autogen-agentchat==0.7.5, autogen-ext==0.7.5, autogen-core==0.7.5

### 初始化 Kanban（首次运行前必须执行）
```bash
hermes kanban init
```

### 已知坑和修复

#### 坑1：非OpenAI模型需要传 model_info
```python
# ❌ 会报错
model_client = OpenAIChatCompletionClient(model="qwen-max", ...)

# ✅ 必须传 model_info 参数
model_client = OpenAIChatCompletionClient(
    model="qwen-max", api_key=..., base_url=..., temperature=0.5,
    model_info={"vision": False, "function_calling": True, "json_output": True, "structured_output": False, "family": "unknown"},
)
```

#### 坑2：Agent名称只能用ASCII
```python
# ❌ ValueError
AssistantAgent(name="数据大臣", ...)

# ✅ 英文名 + system_message 自我介绍
AssistantAgent(name="data_minister", system_message="你是瑞幸即享咖啡的「户部尚书·数据大臣」...")
```

#### 坑3：SelectorGroupChat 模板变量
```python
# ❌ KeyError: 'input'
selector_prompt="讨论话题：{input}..."

# ✅ 有效变量只有 {roles}, {participants}, {history}
selector_prompt="话题：{history}。大臣：{participants}。从{roles}中选下一个。"
```

#### 坑4：Selector 容易重复选同一人（✅ 已修复）
- `temperature` 从 0.7 降低到 **0.5**
- selector_prompt 中增加指令 **「不要连续选同一个人」**

#### 坑5：终止条件有时不触发（✅ 已修复）
- 用 `TextMentionTermination("同意") | TextMentionTermination("结论") | MaxMessageTermination(10)` 兜底

#### 坑6：给用户的命令在复制粘贴时被截断（⚠️ 常见陷阱）

**问题：** 多行 Python 命令、sed heredoc、nano 编辑等操作在通过 IM/聊天框复制到终端时，常因换行、缩进、引号嵌套等原因被截断，导致报错或失败。用户会认为你给了错误的命令。

**根因：** 聊天框到终端的复制过程会破坏多行结构，尤其是有缩进的 Python 代码和含特殊字符的 sed 命令。

**修复方案（不依赖用户终端设置）：**
1. 用 `write_file` 把脚本写到共享卷 `/opt/data/`（宿主映射为 `/home/ubuntu/hermes/data/`）
2. 给用户一条单行命令：`python3 /home/ubuntu/hermes/data/<script_name>.py`
3. 避免：heredoc、nano 编辑、多行 Python `-c` 代码、sed 替换含 `\n` 的字符串

```python
# ✅ 正确做法
write_file(path="/opt/data/add_port.py", content="...")
# → 用户跑：python3 /home/ubuntu/hermes/data/add_port.py

# ❌ 错误做法
# 给用户多行：python3 -c "c=open('...').read();c=c.replace(..."
# 复制到终端时大概率断行
```

---

## 三通道方案：辩论过程实时可视化

这是三省六部圆桌的核心体验升级。三个通道互补，用户可以根据场景选用。

### 通道对比

| 通道 | 传输方式 | 实时性 | 用户打开方式 | 适合场景 |
|:----|:--------|:------|:------------|:--------|
| 🎥 **飞书实时卡片** | Feishu API PATCH | 每轮发言即时 | 飞书群内 | 移动端快速查看 |
| 📋 **Kanban 任务看板** | Hermes Kanban (SQLite) | 秒级（需点刷新） | `http://<ip>:9119/kanban` | 任务进度追踪 |
| 🌐 **Web 辩论看板** | HTTP轮询 2s间隔 | 准实时自动刷新 | `http://<ip>:8899` | 沉浸式观看辩论 |

### 通道一：飞书实时卡片（内置在 roundtable_live.py）

`roundtable_live.py` 自动执行：
1. 创建飞书 `interactive` 卡片，发送到指定 open_id
2. 每轮大臣发言后，PATCH 更新卡片，追加最新发言
3. 讨论结束后更新状态为 "✅ 讨论完成"

卡片尾部附带看板链接，方便用户跳转到 Web 页面。

### 通道二：Hermes Kanban 任务看板（内置在 roundtable_live.py）

**无需额外服务器**，直接使用 Hermes Dashboard 的内置 Kanban 插件。

用户访问：`http://<宿主机公网IP>:9119/kanban`

`roundtable_live.py` 自动执行：
1. **创建任务** — 圆桌开始时，调用 `hermes kanban create --triage "🏛️ 圆桌：{议题}"`
2. **追加评论** — 每位大臣发言后，调用 `hermes kanban comment <task_id> "{发言者}：{内容摘要}" --author "{大臣名}"`
3. **完成任务** — 讨论结束后，调用 `hermes kanban complete <task_id>`

看板用法：
| 操作 | 命令 |
|:----|:-----|
| 初始化 | `hermes kanban init` |
| 创建任务 | `hermes kanban create "标题" --body "描述"` |
| 添加评论 | `hermes kanban comment <task_id> "内容"` |
| 完成任务 | `hermes kanban complete <task_id>` |
| 查看看板 | `hermes kanban list` |
| 查看详情 | `hermes kanban show <task_id>` |

### 通道三：Web 辩论看板（需额外端口映射）

**自动刷新的聊天式辩论页面**，每 2 秒轮询 `dashboard_status.json`，新增发言自动追加到聊天流。

#### 所需文件（已部署在共享卷 `/opt/data/dashboard/`）
- `debate.html` — 辩论看板页面，自动轮询/深色主题/发言人颜色区分/自动滚动
- `debate_server.py` — Python HTTP 服务器，监听 8899 端口，提供静态文件服务
- `dashboard_status.json` — 数据源文件（由 `roundtable_live.py` 每轮写入）

#### 部署步骤

1. **启动辩论服务器**（在 Hermes 容器内）：
```bash
cd /opt/data/dashboard && python3 debate_server.py &
```

2. **开放端口**：
   - ⚠️ **如果容器使用 `network_mode: host`**（此部署的默认配置），端口已直接暴露在宿主机网络上。**不需要**在 docker-compose.yml 添加 `ports:` 映射（host 模式下 Docker 忽略端口映射）。
   - ✅ **需要的操作**：在云服务商控制台的安全组/防火墙放行 TCP 8899 端口，来源 `0.0.0.0/0`

3. **用户访问**：`http://<宿主机公网IP>:8899/`

#### 故障排查：辩论页面无法访问

从 Hermes 容器内按以下顺序诊断：

```bash
# Step 1 — 服务进程是否活着？
ps aux | grep debate_server | grep -v grep

# Step 2 — 容器本地能否访问？
curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8899/
# → 200 ✅: 服务正常   → 跳 Step 3
# → 失败 ❌: 服务没启动，切回 Step 1 重启

# Step 3 — Docker 网关（宿主机）能否访问？
python3 -c "import socket;s=socket.socket();s.settimeout(3);s.connect(('172.18.0.1',8899));print('✅');s.close()"
# → ✅: 端口已暴露到宿主机网络   → 跳 Step 4
# → ❌: 容器网络问题，检查 `network_mode`

# Step 4 — 公网 IP 能否访问？
python3 -c "import socket;s=socket.socket();s.settimeout(3);s.connect(('<公网IP>',8899));print('✅');s.close()"
# → ✅: 全链路通   → 检查浏览器、DNS、代理
# → ❌: 云安全组/防火墙没有放行 8899 端口，去云控制台添加规则

# 对比诊断法 — 如果有一个已知可访问的端口（如 9119），对比测试：
python3 -c "
import socket
for port in [8899, 9119]:
    s=socket.socket();s.settimeout(3)
    try:
        s.connect(('<公网IP>', port));print(f'{port}: ✅ OPEN')
    except Exception as e: print(f'{port}: ❌ {e}')
    s.close()
"
# 9119 ✅ + 8899 ❌ = 确认是安全组只放行了 9119 未放行 8899
```

**注意：** Web 辩论看板依赖 `dashboard_status.json` 文件（由 `roundtable_live.py` 每轮写入）。未启动圆桌时页面显示"三省六部尚未开议"的空白状态，不报错。

#### 页面功能
- 🎨 **发言人颜色区分**：数据🔵 / 运营🟢 / 法务🟣 / 分层🟡 / 算法🩷 / 情报🩵
- 🔄 **自动轮询**：2秒间隔，新发言直接追加，无需手动刷新
- 📜 **自动滚动**：新消息到来时自动滚到底部
- ✅ **完成态**：讨论结束时状态标签变绿

### 🔧 s6 finish 脚本（解决 Gateway 被反复 SIGTERM 杀死的问题）
在 `/run/service/gateway-default/finish` 创建：
```bash
#!/command/with-contenv sh
if [ "$1" -ne 0 ]; then
    rm -f "/run/service/gateway-default/down"
fi
exit 0
```
作用：非正常退出时自动删除 down 文件，s6-supervise 自动重启。
> ⚠️ 该文件在 tmpfs 上，容器重启后需重新创建。

---

## 运行

```bash
PYTHONPATH=~/.local/lib/python3.13/site-packages \
  python3 /opt/data/skills/multi-agent-roundtable/scripts/roundtable_live.py "你的议题"
```

结果自动保存到 `/opt/data/roundtable_result.json`。
同时在以下位置实时可看：
- 飞书群卡片（自动更新）
- Kanban 看板 → `http://<ip>:9119/kanban`（点任务看评论）
- 辩论网页 → `http://<ip>:8899/`（自动刷新的聊天界面）

### 记忆进化
- Level 1：每次圆桌后存结论到记忆，下次"会前简报"
- Level 2：每个Agent配专属知识库，加载历史决策
- Level 3：Agent用memory工具自动读写，自我进化

---

## 参考文件
- `references/three-six-departments.md` — 三省六部详细设计方案
- `references/web-dashboard-deployment.md` — 历史看板部署指南（旧版 aiohttp 看板，已被 debate_server.py 替代）
- `references/feishu-multi-bot-collaboration.md` — 飞书群聊多Bot协作：bot看不到bot消息的机制、权限配置、API拉取方案、协作协议（含方案B绝对静默模式）
- `references/feishu-gateway-display-config.md` — Feishu Gateway 显示配置修复：`tool_progress: "off"` 解决 terminal 输出泄漏到群聊
- `references/obsidian-vault-automation.md` — 飞书群聊→Obsidian Vault 知识库自动化：Jacob沉淀拉取、归类、写入、Git push
- `scripts/roundtable.py` — 基础圆桌讨论脚本（安装完AutoGen后可直接使用）
- `scripts/roundtable_live.py` — 三通道版：飞书实时卡片 + Kanban 任务追踪 + dashboard_status.json 数据源
- `templates/debate.html` — Web 辩论看板 HTML（每 2 秒自动刷新，深色主题，发言人颜色区分）
- `scripts/debate_server.py` — 辩论看板 HTTP 服务器（监听 8899 端口）

---

## 知识库自动化（飞书→Obsidian Vault）

见 `references/obsidian-vault-automation.md` 详细配置。

### 一句话流程

```
Jacob 23:06 沉淀飞书云文档 → 23:08 群发5字段通知
→ 刘小白 cron 23:15 拉消息 → 归类 → 写 vault → git push
→ 老板 Obsidian 验证（23:15-24:00 否决窗口）
```

### 快速设置

```bash
# 创建 cron（已创建，job_id: 82e221175075）
hermes cron create "15 23 * * *" \
  --name "知识库沉淀-入库" \
  --prompt "拉取群聊中Jacob的最新沉淀通知，归类写入obsidian-vault并git push" \
  --skills multi-agent-roundtable \
  --deliver local
```

### 注意事项
- vault 路径：`/opt/data/obsidian-vault/`，GitHub: `yingji945/obsidian-vault`
- Jacob bot ID：`cli_aa9fe0a4fa781cb6`，通过 sender_id 过滤
- 群聊 ID：`oc_c6ddf1d0311516aaa9866cf5db70d043`
- 无法直接读飞书云文档（缺 drive:drive 权限）
