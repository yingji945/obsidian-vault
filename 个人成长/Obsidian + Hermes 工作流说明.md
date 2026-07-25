---
created: 2026-07-17
updated: 2026-07-25
tags: [Hermes, Obsidian, 工作流]
---

# Obsidian + Hermes 工作流说明

## 同步方式
- 仓库：GitHub 私有仓库
- 工具：Obsidian Git 插件（Mac），Working Copy（手机）
- 自动冲突处理：`git reset --hard origin/main`（远程版本优先）

## 同步机制

### 我（Hermes 服务器）→ GitHub
- 每次修改 vault 前自动执行 `ensure-sync.sh`（先拉远程，重置本地）
- 修改后 `git commit && git push`
- 若 push 因网络失败，每小时 `git-push.sh` 自动重试
- 若有冲突：**自动以远程版本（你的版本）为准**，暴力覆盖本地

### GitHub → 你（Mac Obsidian）
- 建议在 Obsidian Git 插件配置：
  - `Auto commit & sync`: 开启
  - `Auto commit interval`: 15 分钟
  - `Auto pull interval`: 15 分钟
  - `Pull on commit`: 开启

### GitHub → 你（手机 Working Copy）
- 手动拉取（GitHub 是中间桥梁）

## 冲突处理
- **自动修复**：服务器每小时 `git-pull.sh` 检测冲突 → `git reset --hard origin/main` → 修复
- 如果你拉取时遇到冲突 → `Cmd + P` → `Git: Commit all changes` → 再 `Git: Pull`

## 笔记结构
- `/个人成长/` — 可带走的认知
- `/业务分析/` — 数据分析、活动复盘
- `/企业沉淀/` — 流程规范、数据字典、数仓分层
- `/项目沉淀/` — 按项目分类的专题知识
- `/笔记/` — AI 日报等时效性内容

## 四层记忆架构
详见 [[四层记忆架构与AI记忆方案一览]]

关联：[[我的AI观]] · [[我的判断标准]] · [[四层记忆架构与AI记忆方案一览]] · [[数据仓库分层说明]]
