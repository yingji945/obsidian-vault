---
created: 2026-10-13
tags: [企业, 数据架构, 数据字典, 原始DDL]
---

# 原始 DDL 归档

> 用户在对话里提供的 `SHOW CREATE TABLE` / 字段列表**原文**，逐字节留存（已 md5 校验）。
>
> **为什么必须留**：① 类型核对的 **ground truth**——数据字典文档里的字段表由这些原文**程序化解析**而来，出现分歧时以此为准；② 表结构变更时可 diff；③ 对话里贴的原文**不落库**，临时目录 24 小时即清，不留就等于永久丢失。

## 命名规则

| 形态 | 命名 | 说明 |
|:--|:--|:--|
| 完整建表语句 | `{库}.{表名}.sql` | 用户给的 `CREATE TABLE ...` 原文 |
| 只有字段列表 | `{库}.{表名}.字段列表.sql` | 用户给的是 `SELECT col, -- 注释` 形式（**无类型**） |

## 清单

| 文件 | 表 | 形态 | 字段数 | 归档日 |
|:--|:--|:--|:-:|:--|
| `dw_dwd.fact_dwd_log_c_menu_cmdty_detail_d_inc.sql` | 商品分析埋点（门店） | 完整 DDL | 55 | 2026-10-13 |
| `dw_dwd.fact_dwd_log_c_menu_cmdty_detail_d_inc.字段列表.sql` | 同上（首版） | 字段列表 | 55 | 2026-10-12 |
| `dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc.sql` | 订单商品基础表 | 完整 DDL | 159 | 2026-10-12 |
| `dw_dwm.dwm_mg_order_cmdty_market_wide_d_view.字段列表.sql` | 订单商品渠道归因视图 | 字段列表 | 164 | 2026-10-12 |
| `dw_dim.dim_channel_level_d_his.sql` | 渠道归因维 | 完整 DDL | 13 | 2026-10-12 |
| `dw_dim.dim_sku_ord_rmk_d_a.sql` | 订单商品属性维 | 完整 DDL | 44 | 2026-10-12 |

### ⏳ 已知未归档

| 表 | 原因 | 补法 |
|:--|:--|:--|
| `dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc` | 用户提供时未落盘（解析后直接写了文档），原文只在聊天记录中 | 请用户重发一次即可补齐 |

## 关联

- [[数据字典索引]] · [[数据字典维护规范]]
