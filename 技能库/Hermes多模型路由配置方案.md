---
created: 2026-07-29
updated: 2026-11-18
tags: [Hermes, 模型路由, 配置经验, 工具链, dashscope]
---

# Hermes 多模型路由配置方案

> ## 🔍 复核状态（2026-11-18 · Hermes v0.21.5）
>
> ✅ **结论：视觉功能正常工作，但已经不是走本文这套配置了——是被 Hermes 的原生路由接管了。**
> 🔴 **重要：不要照本文恢复 `auxiliary.vision`，那会让视觉能力降级。**
>
> ### 为什么会自动切换
>
> `agent/image_routing.py` 的 `decide_image_input_mode()` 判定顺序：
> 1. `agent.image_input_mode` 若不是 `auto` → 直接用该值；
> 2. **若显式配了 `auxiliary.vision` → 强制返回 `"text"`**（代理视觉：图先转文字）；
> 3. 否则 → 查主模型是否支持视觉，支持则 `"native"`（图直接内联给主模型），不支持才 `"text"`。
>
> 当前 `image_input_mode: auto` 且**没有** `auxiliary.vision`，主模型 `deepseek-v4-flash` 支持视觉 → **走 native**。
>
> ### 日志证据（`/opt/data/logs/gateway.log`）
>
> ```
> 2026-07-29  Image routing: text (mode=text).  Pre-analyzing via vision_analyze.   ← 本文配置生效期
> 2026-10-06  Image routing: native (model supports vision). attached inline.       ← 切换点
> 2026-11-05  Image routing: native ...
> 2026-11-10  Image routing: native ...
> 2026-11-12  Image routing: native ... 3 image(s) will be attached inline.
> ```
>
> 2026-10-06 的 config 重建意外把视觉从「代理模式」升级成了「原生模式」——**效果更好**：文字转述会丢细节（表格数字、界面元素），内联是模型直接看图。
>
> ### 各项状态
>
> | 内容 | 状态 |
> |:--|:--|
> | 主模型 `deepseek-v4-flash` + provider `deepseek` | ✅ 仍一致 |
> | `providers.alibaba` + `auxiliary.vision` 两段配置 | ⚪ **已移除，且不建议恢复**（会强制降级为 text 模式）|
> | 「`auxiliary.vision` 不能显式写空 `api_key`（否则 401）」 | ✅ **经验仍有效**——将来若主模型换成不支持视觉的、需要切回 text 模式时，这条是必读项 |
> | 额度表 | ⚠️ 未复核；见下条 |
> | 故障切换流程 | ⚪ 不再适用（当前不走 DashScope）|
> | 配额检查 cron `04bc8be14a6f` | 🔴 **已于 2026-11-18 暂停**（`no_agent` 脚本空转，DashScope 零调用）|
>
> ### 保留价值
>
> DashScope 凭据（`.env` 的 `DASHSCOPE_API_KEY` / `DASHSCOPE_BASE_URL`）**保留不动**——它是**备用视觉通道**。若哪天主模型换成不支持视觉的、或 native 出问题，照第三节配回即可（注意第 2 条会强制切 text 模式）。
>
> ### 教训
>
> **判断功能是否可用，要看运行日志，不能只看配置文件。** 本次复核曾因 config 里找不到 `auxiliary.vision` 而误判「视觉功能可能已损坏」，实际是 auto 路由选了更优路径。配置缺失 ≠ 功能缺失。

## 背景

Hermes Agent 需要支持图文双通道：
- **文本对话** → `deepseek-v4-flash`（快速、省 token）
- **图片识别** → `qwen3.7-plus`（DashScope 免费额度，支持视觉）

免费额度用完时自动降级到备用视觉模型，不中断服务。

## 架构

```yaml
        用户消息
            │
     ┌──────┴──────┐
     ▼              ▼
 纯文本消息       含图片消息
     │              │
     ▼              ▼
deepseek-v4       auxiliary.vision
(主模型)          └─ qwen3.7-plus (每日额度 250万 tokens)
                        │
                  用完超额?
                        │
                   ┌────┴────┐
                   ▼         ▼
              qwen3.7-flash  通知用户
              (500万额度/60天)
```

## 配置（config.yaml）

### 主模型 + Provider

```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek

providers:
  alibaba:
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key: ${DASHSCOPE_API_KEY}
```

### 看图模型（Auxiliary Vision）

```yaml
auxiliary:
  vision:
    provider: alibaba
    model: qwen3.7-plus
    timeout: 120
    extra_body: {}
```

**⚠️ 关键坑：** `auxiliary.vision` 段里**不能显式写** `api_key: ''` 或 `base_url: ''`。
空字符串会覆盖 provider 级别的继承关系，导致 API 调用返回 401 `Incorrect API key provided`。
正确的做法是只设 `provider: alibaba`，让 Hermes 自动从 `providers.alibaba` 继承 base_url 和 api_key。

## 额度查询

DashScope 的配额查询 API：

```bash
# 查看所有模型的免费额度
curl -X POST https://dashscope.aliyuncs.com/api/v1/quotas \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json"
```

### 视觉模型额度明细

| 模型 | Token 额度 | 周期 | 请求限制 |
|:----|:----------|:---|:--------|
| `qwen3.7-plus` | **250万** | 每30天 | 3000次/6h |
| `qwen3.7-flash` | **500万** | 每60天 | 3000次/6h |
| `qwen3.7-max` | 50万 | 每6天 | 500次/1h |

> ⚠️ 该 API 只返回**总配额**，不返回已消耗量。无法通过 API 得知当前还剩多少。
> 实际消耗情况需要去百炼控制台查看。

## 故障切换流程

1. `qwen3.7-plus` 返回配额错误 → 手动切到 `qwen3.7-flash`
2. 切换方式：修改 `config.yaml` 中 `auxiliary.vision.model` 的值，然后重启网关
3. 如果 `qwen3.7-flash` 也耗尽 → 回退到 `qwen3.7-max`（50万额度，更少但也可用）

## 自动化检查

每 7 天运行一次 `check_dashscope_quota.py` 检查额度余量：
- 仅当任一视觉模型已用超过 80% 时发消息提醒
- 正常状态下不打扰用户

## 未来扩展

如需添加更多模型或供应商，只需：
1. 在 `providers` 段新增 provider 配置（base_url + api_key）
2. 在 `auxiliary.xxx` 段引用该 provider
3. 通过 `model.route` 规则可按任务类型自动分流（如 OCR 走 qwen-vl-ocr）

---

*配置时间：2026-07-29*
*关联文件：`/opt/data/config.yaml`、`/opt/data/scripts/check_dashscope_quota.py`*
