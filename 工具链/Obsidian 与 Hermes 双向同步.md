# Obsidian 与 Hermes 双向同步

> 适用场景：Mac 上写 Obsidian 笔记，服务器上跑 Hermes Agent 处理 inbound 内容并回写 vault，两者通过 GitHub 自动双向同步。

---

## 架构全景

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub (远程仓库)                         │
│              https://github.com/yingji945/obsidian-vault         │
└──────────┬──────────────────────────────────┬───────────────────┘
           │ push (每15分钟)                   │ push (写完即推)
           ▼                                  ▼
┌─────────────────────┐          ┌──────────────────────────────┐
│   Mac (Obsidian)     │          │     服务器 (Hermes Agent)    │
│                      │          │                              │
│  Obsidian Git 插件   │          │  ensure-sync.sh (每整点)     │
│  ─ Auto commit+push  │          │  ─ git reset --hard origin   │
│  ─ Auto pull         │          │  ─ 以 GitHub 版本为准        │
│  ─ Pull on commit    │          │                              │
│  ─ 每15分钟一次      │          │  git-pull.sh (每整点)        │
│                      │          │  ─ 自动解决冲突              │
└─────────────────────┘          └──────────────────────────────┘
```

### 核心原则

**以 GitHub 为唯一信源**：两边都不直接同步对方，都只跟 GitHub 交互。GitHub 永远是最新状态，不存在「谁的版本更优先」的歧义。

---

## 一、Mac 端配置（Obsidian Git 插件）

### 1.1 安装插件

`Cmd + ,` → 社区插件 → 搜索 `Obsidian Git` → 安装并启用（绿色）

### 1.2 需要修改的 4 项设置

插件设置页分多个分区，精确路径如下：

#### ①「Automatic」分区 — 前两项

| 设置名（精确） | 操作 |
|:--------------|:----:|
| **Auto commit-and-sync interval (minutes)** | 填 `15` |
| **Auto pull interval (minutes)** | 填 `15` |

> ⚠️ 这个分区还有几个以 "Auto" 开头的其他选项（如 `Auto commit-and-sync after stopping file edits`、`Auto commit-and-sync after latest commit`、`Auto push interval`），**保持默认，不要动**。

#### ②「Commit-and-sync」分区 — 后两项

往下滚动到独立的 **Commit-and-sync** 分区：

| 设置名（精确） | 操作 |
|:--------------|:----:|
| **Pull on commit-and-sync** | 开启 ✅ |
| **Push on commit-and-sync** | 开启 ✅ |

> `Push on commit-and-sync` 开启后，下方会显示一行「Disable push」—— 确认它是 **关闭 ❌** 状态。

### 1.3 首次认证

第一次 commit-and-sync 时会弹出用户名/密码提示：

| 提示 | 填写 |
|:----|:----|
| `Username for 'https://github.com'` | `yingji945` |
| `Password` | Personal Access Token（不是 GitHub 密码） |

可选：让 Mac 记住凭据

```bash
git config --global credential.helper osxkeychain
```

执行一次之后，后续不再需要输密码。

---

## 二、服务器端同步机制

服务器不依赖 Obsidian Git，通过两个脚本保持同步：

### ensure-sync.sh（写前必同步）

每次 Hermes 要写 vault 笔记之前，自动执行 `git reset --hard origin/main`，**以 GitHub 版本为准覆盖本地**。确保不会因为本地缓存的内容过旧导致重复工作。

### git-pull.sh（每整点自动拉取）

每小时拉取一次，带**自动冲突解决**逻辑。如果 Mac 和服务器同时修改了同一个文件，默认以服务器版本覆盖。

> 如果希望 Mac 版本优先，需要调整 `ensure-sync.sh` 的策略：改为 merge（而非 reset），并让 Mac 端 pull 时以 Mac 为准。

### 推送时机

服务器上 Hermes 写完笔记后，通过 `git add → commit → push` 立即推送到 GitHub，Mac 端会在下个 15 分钟周期自动 pull 到本地。

---

## 三、完整工作流时序

```
你 Mac 写笔记
    │
    ├─ [每15分钟] Obsidian Git 自动 commit + push → GitHub
    │
    ▼
GitHub 更新
    │
    ├─ [每整点] 服务器 git-pull.sh 拉取 → ensure-sync.sh 同步
    │
    ▼
服务器读到新笔记
    │
    ├─ [需要时] Hermes 处理 inbound 内容 → 写笔记到 vault
    │  → git push → GitHub
    │
    ▼
GitHub 再次更新
    │
    ├─ [下一个15分钟] Mac Obsidian Git pull → 同步到本地
    │
    ▼
你在 Mac 上看到服务器写的新笔记
```

---

## 四、常见问题

### Q: Obsidian Git 报错 "Authentication failed"
→ 检查 token 是否过期，重新在 GitHub Settings → Developer settings → Personal access tokens 生成新的。

### Q: 服务器端 ensure-sync.sh 发现冲突
→ 自动用服务器版本覆盖，不会阻塞流程。如果想保留 Mac 版本，在服务器上手动解决冲突后重新 commit。

### Q: Mac 上改错了笔记想回退
→ Obsidian Git 提供了 History View，可以用 `Cmd + P` → `Open history view` 查看历史提交，找到改错之前的版本回退。Git 的每一条提交都是可追溯的，多写无害。

### Q: 笔记本电脑休眠后 Obsidian 打开，同步多久生效？
→ Obsidian Git 的 interval 跨会话记录：即使休眠超过 15 分钟再打开，会立刻执行一次 commit-and-sync，不影响频率。

---

## 五、相关资源

- [Obsidian Git 插件文档](https://publish.obsidian.md/git-doc/Start+here)
- [[确保同步工作流说明]]
