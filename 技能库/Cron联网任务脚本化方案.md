---
created: 2026-08-05
tags: [技能库, Hermes, cron, token, 优化, 脚本化, 多后端路由, 健康体检]
version: 1.1.0
---

# Cron 联网任务脚本化方案（省 token 根治）

> 把 cron 任务里的 agent 联网抓取前置到**零 token 脚本**，根治网络重试导致的 token 翻倍。
> 首发落地：2026-08-05「每日AI简报」改造，实测单次 token 砍 69%。
> v1.1（2026-10-09）补齐「多后端有序路由 + 健康体检」，见第四节 —— 起因是发现 arXiv 主源已静默失效数月。

---

## 一、问题背景：token 为什么会翻倍

### 1.1 症状

「每日AI简报」8/4 消耗 52 万 token，8/5 涨到 110 万——**翻了一倍多**。

### 1.2 根因链条

```
网络波动（GitHub 网页超时）
    → agent 反复重试（API 调用 28 → 36 次）
    → 每次调用都从缓存重读全部上下文（cache_read_tokens 47万 → 104万）
    → token 翻倍
```

**核心原理：cron 任务里，API 调用次数 = token 放大倍数。** 每次 API 调用都要把整个上下文（系统提示 + prompt + 已抓内容）从缓存重读一遍。

**关键认知：网络超时是「稳定状态」不是「暂时抖动」。** GitHub 443 超时重试 10 次也是超时——内容照样没有，只是多烧 10 倍 token。

---

## 二、诊断流程（三步）

### 2.1 看 token 构成

```bash
hermes insights --days 2
```

或直接查 state.db（精确到每次运行）：

```python
import sqlite3
con = sqlite3.connect('/opt/data/state.db')
cur = con.cursor()
cur.execute("""SELECT id, started_at, title, api_call_count,
               input_tokens, output_tokens, cache_read_tokens
               FROM sessions ORDER BY started_at DESC LIMIT 10""")
for r in cur.fetchall(): print(r)
```

**重点看 `api_call_count` 和 `cache_read_tokens`** —— 这两个翻倍就是网络重试的锅。

### 2.2 对比两次运行

同任务前后两天对比：调用次数 28→36、cache_read 47万→104万 = 重试导致。

### 2.3 确认内容没变

输入+输出 token 基本没变（5万 vs 5.3万）→ 内容没变，是调用次数问题，不是任务变重。

---

## 三、根治方案：抓取前置到脚本

### 3.1 架构（三层组合拳）

| 层 | 做法 | 效果 |
|:--|:----|:----|
| 🩸 **止血** | prompt 加「防重试铁律」 | 明天就省一半 |
| 🌱 **根治** | 联网抓取移出 LLM，交给 script（零 token） | 网络波动与 token 彻底解耦 |
| 🛡️ **护栏** | 脚本内自带重试 + 降级源（免费随便重试） | 内容不损失，token 零波动 |

### 3.2 脚本设计原则

1. 每个源独立 `try/except`，失败标记 `[源不可达]` 继续下一个，**绝不阻塞**
2. 脚本内重试 2 次（零 token，随便重试）
3. 主源失败自动切降级源
4. 输出结构化 Markdown 到 stdout，由 cron 注入 agent 上下文

### 3.3 cron 改造三步

1. **挂脚本**：cronjob update 加 `script: fetch_xxx.py`（放 `/opt/data/scripts/` 下，相对路径自动解析）
2. **改 prompt**：

```
## 你的任务
**数据已经由脚本预抓取好了**（脚本输出在本消息的上下文开头...）。
你只需基于脚本抓到的内容做整理和分类，**绝对不要再联网搜索、
不要再访问任何网站、不要再重试任何抓取**。

## 注意事项
【铁律】本次任务禁止任何联网搜索/网页访问/抓取重试，一次成型输出。
```

3. **验证**：cronjob run 手动触发 → 等 tick 执行（1-2 分钟）→ 查 state.db 对比 token → 检查产出文件质量。

### 3.4 实测效果（2026-08-05）

| 指标 | 改造前 | 改造后 | 降幅 |
|:----|:----|:----|:----|
| API 调用次数 | 36 | 7 | **-80%** |
| 输出 token | 22,897 | 7,582 | -67% |
| 缓存读取 | 30,770 | 8,946 | -71% |
| **总 token** | ~53,700 | ~16,500 | **-69%** |

---

## 四、多后端有序路由 + 健康体检（v1.1，2026-10-09）

> 借鉴 [Agent Reach](https://github.com/Panniantong/Agent-Reach) 的「能力层」设计：每个渠道 = **有序后端列表**（首选 ▸ 备选），路由时**真实调用**每个后端而不是只看 URL 是否存在，第一个返回内容者当选。换代时只调列表顺序，不重写代码。

### 4.1 v1 的真实缺陷（两个，都属于"没人发现"型）

1. **备选形同虚设**：除 arXiv 外，每个源只有一条路。源一挂就静默退化成 `[源不可达]`，简报长期少一个板块而无人察觉。
2. **⚠️ 静默失效活教材**：arXiv 主源的正则 `<a href="(/abs/...)">` 从某次 arXiv 改版起就匹配不到了 —— 真实 HTML 早已变成 `<a href ="/abs/2610.12466" ...>`（**等号前多了一个空格**）。于是从改版那天起，arXiv 板块一直在悄悄走备选 API，**几个月无人察觉**：两条路都能出内容，`[源不可达]` 永远不会触发。

**结论：光有"失败标记"不够，还必须能看见"今天走的是哪条路"和"优选路已经死了多久"。**

### 4.2 落地结构（`/opt/data/scripts/fetch_ai_news.py` v2）

| 机制 | 做法 |
|:--|:--|
| 声明式后端链 | `CHANNELS = [{key, label, backends: [(后端名, 函数), ...]}]`，顺序即优先级 |
| 真实探测路由 | `route()` 按序**真调用**每个后端，第一个返回非空者当选，并记录每个后端的成败条数 |
| 降级不静默 | 走了备选时板块标题自动变成 `## 💼 虎嗅（保底源：IT之家 RSS）`，防止把备选源内容当成首选源播报 |
| 链路追踪 | 输出末尾附 HTML 注释 `<!-- health: arxiv=arXiv 列表页(6) qbitai=量子位 RSS(8) … -->`（agent 不会抄进简报，人/脚本可追溯） |
| 健康落盘 | `scripts/.ai_news_health.json`：每渠道 active_backend / last_ok / last_fail / fail_streak / 各后端探测结果 |
| 一键体检 | `python3 fetch_ai_news.py --doctor` → 表格：状态 / 当前选型 / 各后端通断 / 连续失败 / 最近成功；有 ❌⚠️ 时退出码 1 |
| 静默看门狗 | 无问题时只输出"全部正常"；配 `no_agent` cron = 只在挂了时才推送（零 token） |

### 4.3 后端链现状（2026-10-09 实测，备选全部真实出内容）

| 渠道 | 首选 | 备选（实测条数） |
|:--|:--|:--|
| arXiv | 列表页 HTML（已修正 `href =` 空格问题） | export API（6 条） |
| 量子位 | RSS（0.02s） | 首页 HTML（8 条，`<h4><a href=…>标题</a></h4>`） |
| GitHub | Search API（分 topic 单查） | — （暂无可用备选） |
| 虎嗅 | 首页 HTML | IT之家 RSS（5 条，保底，科技视角，会标注） |

### 4.4 教训

**给外部依赖建链路时，"有备选"不等于"备选被验证过"。** 要么定期 `--doctor` 真实探测，要么把 `active_backend` 显式暴露出来 —— 否则首选路悄悄死掉时，你只会看到"内容还在"，看不到"系统已经降级几个月了"。

---

## 五、已验证数据源方案（国内网络实测，2026-08-05 首发 / 2026-10-09 更新）

| 源 | 方案 | 备注 |
|:--|:----|:----|
| arXiv 论文 | 网页 `arxiv.org/list/cs.AI/recent`（慢 8s）→ 降级 `export.arxiv.org/api/query` | 正则 `href="(/abs/[\d.]+)">([^<]+)</a>` |
| 量子位 | **RSS feed** `qbitai.com/feed`（WordPress，秒回）；备选：首页 HTML `<h4><a href=…>标题</a></h4>` | v1 曾误判"HTML 抓不到"；实测 2026-10 首页可正则出 8 条。RSS 第一条 title 是站点名要跳过 |
| GitHub 热门 | **直接 API** `api.github.com/search/repositories?q=topic:ai created:>日期&sort=stars` | ⚠️ 网页 trending 国内 10s 超时（就是它导致 token 翻倍）；⚠️ API 的 OR 组合查询返回 0，必须**分 topic 单独查再合并去重** |
| 36氪 | ❌ 不可用（JS 空壳）—— 2026-10-09 复测 `/feed` 返回的仍是 SPA 首页 | 用**虎嗅**替代：正则 `href="(https://www\.huxiu\.com/article/\d+\.html)"[^>]*>.*?<h3[^>]*>([^<]{10,60})</h3>`；虎嗅备选 = IT之家 RSS `ithome.com/rss/` |
| 机器之心 | ❌ 不可用（`/rss` 实测同为 JS 空壳） | — |
| IT之家 / Solidot / 少数派 | ✅ 标准 RSS，0.1s 内响应 | 可作科技/行业板块的保底源 |
| GitHub API | ✅ Search API（`gh` CLI 本机未装） | api.github.com 稳，github.com 时断（见 `blocked-page-recovery` 技能） |
| 通用反爬 | 必须带 UA 头 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0` |
| 连接测试 | `curl -s -o /dev/null -w "%{http_code} t=%{time_total}s\n" --max-time 8 URL` | 先测再写脚本，别猜 |

---

## 六、坑清单（全部踩过）

1. **GitHub API OR 查询**：`(topic:ai OR topic:llm) created:>date` 返回 0 条。必须分 topic 单查合并。
2. **量子位 HTML**：首页正则抓不到文章，必须走 RSS feed。
3. **36氪 JS 渲染**：HTML 里没有文章链接，urllib 拿到的只是空壳。
4. **datetime.UTC**：老版本 Python 没有 `datetime.UTC`，用 `timezone.utc` 兼容。
5. **脚本相对路径**：cron 的 `script` 相对路径解析到 `/opt/data/scripts/`（HERMES_HOME 下）。
6. **execute_code 被拦**：cron 安全策略下 `execute_code` 会 BLOCKED（approvals.cron_mode），调试脚本用 terminal + read_file 代替。
7. **cronjob run 触发**：手动触发后要等 1-2 分钟 tick，`last_run_at` 更新才算跑完。

---

## 七、版本记录

| 版本 | 日期 | 内容 |
|:----|:----|:----|
| v1.0.0 | 2026-08-05 | 首次沉淀：诊断流程 + 三层根治架构 + 4 源方案 + 坑清单；落地「每日AI简报」改造（token -69%）；对应 Hermes 技能 `cron-network-scripting` v1.0.0 |
| v1.1.0 | 2026-10-09 | 新增第四节「多后端有序路由 + 健康体检」，`fetch_ai_news.py` 升级 v2（声明式后端链 / 真实探测 / 降级标注 / `--doctor` / 健康落盘）；修正 arXiv 主源正则（`href =` 空格导致静默失效数月）与 export API 错位一条；新增备选源：量子位首页 HTML、IT之家 RSS；实测排除 36氪 / 机器之心（JS 空壳） |

---

## 八、相关文件

- 工作脚本：`/opt/data/scripts/fetch_ai_news.py`（v2，可直接复制改源）
- 健康状态：`/opt/data/scripts/.ai_news_health.json`（每次运行落盘，`--doctor` 读它算连续失败）
- 链路体检：`python3 /opt/data/scripts/fetch_ai_news.py --doctor`（真实探测**每一个**后端，不能用 `route()`——它会短路在首个可用后端上，那样「备选死了」永远查不出来；有 ❌/⚠️ 返回退出码 1）
- 看门狗脚本：`/opt/data/scripts/ai_news_doctor.sh`（正常时零输出=不推送）
- 看门狗 cron：`AI简报链路体检`（job `25db9d59ac4c`，no_agent 零 token，每天北京时间 10:00 = UTC `0 2 * * *`，异常才推送到飞书）
- 模板脚本：`/opt/data/skills/devops/cron-network-scripting/scripts/fetch_news_template.py`
- 生效配置：`/opt/data/cron/jobs.json`（每日AI简报 0a9f9d6ee345）
- token 精确记录：`/opt/data/state.db`（sessions 表）
- Hermes 技能：`cron-network-scripting`（devops 分类）
