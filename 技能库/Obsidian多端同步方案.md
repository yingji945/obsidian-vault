---
created: 2026-07-29
updated: 2026-08-03
tags: [Obsidian, 同步, 多端, 技能库]
---

# Obsidian 多端同步方案

> Mac + GitHub + 服务器 + 手机 四端知识库同步。
>
> 📌 2026-08-03 合并自三篇：本文件（操作手册）+ 个人成长/Obsidian跨设备同步方案（方案选型）+ 技能库/Obsidian工作流说明（工作机制），原文件已归档。

---

## 一、方案选型对比（为什么是现在这套）

| 方案 | 费用 | 体验 | 推荐度 |
|:----|:----|:----|:------|
| **Working Copy (iOS) + Obsidian** | Working Copy 付费（~$20） | ⭐⭐⭐⭐⭐ 完整读写 | ⭐ **首选（当前已实施）** |
| **Obsidian 官方同步** | $4/月 | ⭐⭐⭐⭐⭐ 最简单 | ⭐ 省心（手机端完整体验时考虑） |
| **GitHub 网页编辑** | 免费 | ⭐⭐ 只能看+单文件编辑 | 应急用 |
| **iCloud** | 免费 | ⭐⭐⭐ 有冲突风险 | 备选 |

- **当前已实施**：Obsidian Git（Mac）+ GitHub 私有仓库 + Working Copy（iOS）+ 服务器 cron，免费方案跑通全链路。
- 如果未来想要**手机端完整体验**（图谱/双向链接交互）→ 可升级 Obsidian Sync（$4/月）。

## 二、当前已配置的

| 端 | 同步方式 | 状态 | 最后配置时间 |
|:--|:--------|:----|:-----------|
| 💻 **Mac 本地** | Obsidian Git 插件自动提交/拉取 | ✅ 已使用中 | 2026-07-28 |
| 🖥️ **服务器** | cron 每小时自动 pull + 入库后自动 push | ✅ 已稳定运行 | 2026-07-28 |
| ☁️ **GitHub 远程** | `github.com/yingji945/obsidian-vault.git`（私有） | ✅ 中央仓库 | 2026-07-28 |
| 📱 **手机（iOS）** | Working Copy 手动 clone → Obsidian 打开 | ✅ 已配置 | 2026-07-29 |

## 三、架构

```mermaid
flowchart LR
    Mac["💻 Mac（创作端）\nObsidian Git 插件\n自动提交+拉取 每15分钟"]
    Server["🖥️ 服务器（自动化端）\n定时入库脚本\ncron pull/push"]
    GitHub["☁️ GitHub（中央仓库）\ngithub.com/yingji945\n/obsidian-vault.git"]
    Phone["📱 手机（查看端）\nWorking Copy clone\n手动 push"]

    Mac <--> GitHub
    Server <--> GitHub
    Phone <--> GitHub
```

## 四、Mac 设置（已完成）

### Obsidian Git 插件配置

1. 社区插件市场搜索 **Obsidian Git** 安装
2. 启用后设置：
   - 自动提交间隔：15 分钟
   - 自动拉取间隔：15 分钟
   - 拉取前先提交：✅ 开启
   - 提交说明：`Auto sync {date}`
3. 日常操作：完全自动，无需手动操作

### 手动操作

如需立即同步，在 Obsidian 内按 `Cmd + P`：

| 操作 | 命令 |
|:----|:----|
| **拉取最新** | `Obsidian Git: Pull` |
| **推送** | `Obsidian Git: Push` |
| **查看状态** | `Obsidian Git: Check status` |

## 五、服务器设置（已完成）

### GitHub 远程仓库

```bash
# origin 已指向
git remote add origin https://github.com/yingji945/obsidian-vault.git
```

### 自动 pull cron（每小时）

```bash
hermes cron create "0 * * * *" \
  --name "vault-git-pull" \
  --prompt "执行 cd /opt/data/obsidian-vault && git pull --rebase" \
  --deliver local
```

> 冲突兜底：`git fetch origin main && git reset --hard origin/main`（以远程用户版本为准）。`ensure-sync.sh` 已废弃，不再使用。

### 知识库入库后自动 push（每晚 23:15）

- 自动拉取 Jacob 沉淀通知 → 写 vault → auto push
- 若 push 失败（GitHub 网络超时），跳过不阻塞，每小时 `git-push.sh` 自动重试

## 六、手机端（iOS）设置

### 首次配置

1. **App Store** → 搜索安装 **Obsidian**（免费）
2. **App Store** → 搜索安装 **Working Copy**（免费版够用）
3. **Working Copy**：
   - 登录 GitHub 账号
   - 点击右上角 `+` → Clone Repository
   - 输入：`https://github.com/yingji945/obsidian-vault.git`
   - 克隆完成后，点仓库名 → 点 **"Open in Obsidian"**
4. **Obsidian**：
   - 自动打开 vault，开始浏览笔记
   - 手机上编辑笔记 → 保存后回到 Working Copy
   - Working Copy → commit → push

### 日常同步流程（手机）

```
Obsidian 编辑完 → 保存
  → 切到 Working Copy
  → 点仓库 → 点"Push"
  → 完成 ✅
```

> ⚠️ 手机端没有自动 git 插件，每次编辑后需要手动推一次

## 七、同步机制与冲突处理

### 数据流

```
Mac（Obsidian Git 插件，每15min auto commit & sync）
  ↓
GitHub 私有仓库 ←→ 服务器（每小时 pull；入库后 push，失败由 git-push.sh 重试）
  ↓
新电脑 / iPhone（clone/pull）
```

### 冲突处理原则

| 场景 | 处理方式 |
|:----|:--------|
| **同一个文件两边都改了** | Mac 版本优先，Obsidian Git 会显示冲突标记手动解决 |
| **Mac 上新建的笔记服务器没有** | 自动合并，无需操作 |
| **服务器新建的笔记 Mac 没有** | `git pull` 后自动出现 |
| **手机改完推了，Mac 有冲突** | `git pull` 后手动解决冲突 |

> **Mac 是权威端：** 如果同一个文件两边都改了，以 Mac 上的版本为准。服务器端遇冲突自动以远程（用户）版本为准（`git reset --hard origin/main`），暴力覆盖本地。

### 手动解决冲突（Mac 端）

`Cmd + P` → `Git: Commit all changes` → 再 `Git: Pull`

## 八、首次使用流程（换电脑/重装）

### 新电脑

1. 装 Obsidian → 社区插件装 Obsidian Git
2. 克隆仓库：
   ```
   Cmd + P → "Obsidian Git: Clone an existing remote repo"
   输入：https://github.com/yingji945/obsidian-vault.git
   ```
3. 配好自动提交拉取间隔
4. 打开 vault，全部笔记自动出现

### 新手机

1. 装 Obsidian + Working Copy
2. Working Copy 里 clone 仓库
3. Obsidian 里打开

## 九、vault 目录速览

- `/个人成长/` — 可带走的认知
- `/业务分析/` — 数据分析、活动复盘
- `/企业沉淀/` — 流程规范、数据字典、数仓分层
- `/项目沉淀/` — 按项目分类的专题知识
- `/笔记/` — AI 日报等时效性内容
- `/技能库/` — 系统怎么用（设计文档）
- `/待办/` — 当前任务清单
- `/归档/` — 已过期内容

## 关联 vault 文件

- [[四层记忆架构与AI记忆方案一览]] — 四层记忆架构
- [[技能库/Hermes多模型路由配置方案]]
- [[技能库/SQL经验库]]
- [[技能库/用户分层SQL模板]]
- [[企业沉淀/数据仓库分层说明]]
- [[企业沉淀/数据字典维护规范]]

---

> 📌 2026-07-29 初版 → 2026-08-03 合并三篇为一
