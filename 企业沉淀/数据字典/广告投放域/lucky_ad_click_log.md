---
created: 2026-11-23
updated: 2026-11-23
tags: [企业, 数据, 字典, 广告投放, HBase]
field_status: 🟡 0/10 含类型（字段名已实测，类型待 DDL）
source: 用户截图 select * 实测 @ 2026-11-23
---

# hbase.lucky_ad_click_log — 广告点击日志

**数据库**：`hbase`

**用途**：记录用户点击广告的原始事件，是广告归因链路的**起点**。通过 `info_click_id` 与 [[lucky_ad_event_callback_log]] 关联，把「点击」和「下单」串起来。

> ⚠️ 字段类型全部待 DDL 核对。当前基于 `select *` 实测截图，字段名与样本值准确，**类型未知**。

## 表结构（10 字段，实测）

### 主键与分区

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `rowkey` | 🟡 待核 | HBase 主键，格式 `{来源前缀}-{click_id片段}`，如 `centad-0b5f5shym6bc` |
| 10 | `dt` | 🟡 待核 | 分区字段，`yyyy-MM-dd` |

### 点击标识（核心）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 2 | `info_create_time` | 🟡 待核 | **点击时间**，如 `2026-11-22 06:34:19` |
| 3 | `info_click_id` | 🟡 待核 | **微信广告 click_id**，`wx` + 16 位 = 18 位，如 `wx0b5f5shym6bcqw00`。🔑 **归因关联键** |
| 5 | `info_source` | 🟡 待核 | **渠道来源**。实测值 `tencentad`。🔑 `= 'tencentad'` 即限定自营广告 |

### 用户与设备

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 4 | `info_openid` | 🟡 待核 | 微信 openid。🔴 **实测为 null，拿不到用户** |
| 7 | `info_union_id` | 🟡 待核 | 微信 union_id。🔴 实测为 null |
| 8 | `info_device_id` | 🟡 待核 | 设备 ID，如 `8765787` |
| 9 | `info_device_type` | 🟡 待核 | 设备类型，如 `1` |

### 落地页

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 6 | `info_url` | 🟡 待核 | **落地页 URL**（URL 编码）。实测含 `source=S-ZY2`、`sessionId`、`mallDetailExp=0`、`shareTitle`。🟡 `source` 疑似广告计划码，含义未确认 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:--|:--|:--|
| [[lucky_ad_event_callback_log]] | `info_click_id` = `info_click_id` | 🔑 **唯一共同字段**，点击 → 转化回调用它串联 |

**注意**：本表**不含 `mem_id`、不含订单号**。要算「下单人数」必须经 [[lucky_ad_event_callback_log]] 的 `info_order_no` 关联 [[dws_eorder_eorder_d_his_combine]] 拿 `mem_id`。

## 使用注意点

| # | 注意点 | 说明 |
|:-:|:--|:--|
| 1 | 🔴 **必须加 `info_source` 过滤** | 不加渠道过滤，回调侧会是**全渠道**汇总。2026-11-22 实测：全渠道回调订单 336,014 条，`tencentad` 只占 1,057 条 |
| 2 | 🔴 **拿不到用户身份** | `info_openid` / `info_union_id` 实测均为 null，只能靠下游订单表拿 `mem_id` |
| 3 | 🟡 **`info_click_id` 来源** | 腾讯（微信广告广点通）**下发**，我们落地页接收存档，回调时原样带回。不是我们生成的 |
| 4 | 🟡 **一个点击可能对应多笔订单** | 归因窗口内多次下单都用同一个 `click_id`，统计订单时要 `distinct info_order_no` |
| 5 | 🟡 **归因窗口未知** | 点击后多少天内的下单还算这次点击，需问投放侧。未确认前不要假设窗口长度 |

## 典型 SQL

```sql
-- 取某天的自营广告点击（去重）
select distinct info_click_id
from hbase.lucky_ad_click_log
where dt = '2026-11-22'
  and info_source = 'tencentad'
  and info_click_id is not null
  and info_click_id <> ''
```

```sql
-- 各渠道点击量对比
select info_source
     , count(distinct info_click_id) as 点击UV
from hbase.lucky_ad_click_log
where dt = '2026-11-22'
  and info_click_id is not null
  and info_click_id <> ''
group by info_source
```

## 关联

[[数据字典索引]] · [[lucky_ad_event_callback_log]] · [[dws_eorder_eorder_d_his_combine]] · [[广告归因分析SQL模板]]
