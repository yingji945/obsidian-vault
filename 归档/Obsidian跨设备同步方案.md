---
created: 2026-07-28
updated: 2026-07-28
tags: [Obsidian, 工具链, 个人成长]
---

# Obsidian 跨设备同步方案

> 当前状态：知识库在 Mac 本地、服务器、GitHub 三个位置，存在同步链。目标：换电脑不丢数据、手机端能查看/编辑。

## 问题

Obsidian 默认存本地（Mac 的 `~/xxx`），如果换电脑：
- 新电脑上没有这些文件 → 知识库就没了
- 手机（iOS/Android）上也想看到今天构建的知识图谱

## 方案：Git 同步（当前已实现）

我们已经用了 Obsidian Git 插件 + GitHub 私有仓库，就是为这个准备的。流程：

```
Mac（Obsidian + Obsidian Git 插件）
        ↓ Auto commit & sync (15min)
    GitHub 私有仓库 <=== 服务器（每小时 push 重试）
        ↓ clone/pull
    新电脑 / iPhone
```

### 换电脑时

新 Mac 上：
1. 装 Obsidian
2. 装 Obsidian Git 插件（BRAT 或社区市场）
3. Clone 仓库到本地：`git clone https://github.com/yingji945/obsidian-vault.git`
4. Obsidian 打开该目录作为 vault
5. 配置 Auto commit & sync → 之后的编辑自动双向同步

### 手机端

推荐方案排名：

| 方案 | 费用 | 体验 | 推荐度 |
|:----|:----|:----|:------|
| **Working Copy (iOS) + Obsidian** | Working Copy 付费（~$20） | ⭐⭐⭐⭐⭐ 完整读写 | ⭐ 首选 |
| **Obsidian 官方同步** | $4/月 | ⭐⭐⭐⭐⭐ 最简单 | ⭐ 省心 |
| **GitHub 网页编辑** | 免费 | ⭐⭐ 只能看+单文件编辑 | 应急用 |
| **iCloud** | 免费 | ⭐⭐⭐ 有冲突风险 | 备选 |

#### 方案 A：Working Copy（推荐免费方案）

1. iPhone 装 **Working Copy**（App Store）
2. 登录 GitHub 账号，clone 这个仓库
3. 用 Working Copy 的文本编辑器查看/编辑
4. 改完后 commit + push
5. Mac 端的 Obsidian Git 会拉下来

缺点：不是 Obsidian 原生体验，没有图谱/双向链接的交互

#### 方案 B：Obsidian 官方同步

1. 开通 Obsidian Sync（设置 → Core plugins → Sync）
2. 登录账号，同步自动走端到端加密
3. 手机装 Obsidian，登同一账号 → vault 自动出现

优点：最省心、实时、手机端完整体验、换电脑一键恢复
缺点：$4/月

#### 方案 C：纯 GitHub 应急

手机上：
1. 浏览器打开 `https://github.com/yingji945/obsidian-vault`
2. 直接看 `.md` 文件内容（GitHub 渲染 Markdown 很漂亮）
3. 要编辑 → 点 ✏️ 编辑按钮 → 提交
4. 服务器的 `git pull` cron 会拉走你的修改

适合临时查阅，不适合频繁编辑。

## 当前建议

如果只是**偶尔手机查一下** → **方案 C（GitHub 网页）** 就够了，不需要额外花钱。

如果**经常手机写笔记/查知识** → **方案 B（Obsidian Sync）** $4/月，省心省力。

如果**不想花钱但需要频繁编辑** → **方案 A（Working Copy）** 一次性付费。

## 当前同步架构备忘

```
Mac 用户端（权威版本）
  ↓ Obsidian Git Auto commit & sync（15分钟）
GitHub 私有仓库 ← 服务器每小时 git pull + git push 重试（网络不稳定时兜底）
```

> ⚠️ Mac 版本为权威，服务器遇到冲突会自动放弃本地（`git reset --hard origin/main`），以 GitHub（用户版本）为准。
