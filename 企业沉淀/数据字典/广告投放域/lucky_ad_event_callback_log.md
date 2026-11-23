---
created: 2026-11-23
updated: 2026-11-23
tags: [企业, 数据, 字典, 广告投放, HBase, 转化回调]
field_status: 🟡 0/10 含类型（字段名已实测，类型待 DDL）
source: 用户截图 select * 实测 @ 2026-11-23
---

# hbase.lucky_ad_event_callback_log — 广告转化回调日志

**数据库**：`hbase`

**用途**：记录我们**主动回传腾讯广告**的转化事件。用户下单后，我们把订单信息（含 `click_id`）报给腾讯 API，同时落一份到本表。是广告归因链路的**终点**，也是唯一能拿到 `info_order_no` 的地方。

> ⚠️ 字段类型全部待 DDL 核对。当前基于 `select *` 实测截图，字段名与样本值准确，**类型未知**。

## 表结构（10 字段，实测）

### 主键与分区

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `rowkey` | 🟡 待核 | HBase 主键，`ECL` + 流水号，如 `ECL120481879953436672`。⚠️ 与 `info_order_no` **前 9 位相同**，但**不是同一个数** |
| 10 | `dt` | 🟡 待核 | 分区字段 = **回调日期**，🔴 **不是下单日** |

### 事件（核心）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 2 | `info_callback_time` | 🟡 待核 | 回调时间，如 `2026-11-22 11:58:34` |
| 7 | `info_event` | 🟡 待核 | **事件类型**。实测 `6` = `COMPLETE_ORDER`（**下单，不是支付成功**）|
| 9 | `info_order_no` | 🟡 待核 | **订单号 = 自营 `eorder_no`**（18 位纯数字），如 `120481879559072770`。🔑 **归因落地键** |
| 3 | `info_click_id` | 🟡 待核 | 关联点击的 `click_id`，`wx` + 16 位。🔑 与 [[lucky_ad_click_log]] 关联 |
| 8 | `info_ad_channel` | 🟡 待核 | 广告账户/渠道标识，实测 `coffee-tencentad` |

### 报文（诊断用）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 4 | `info_request_body` | 🟡 待核 | **回传腾讯的请求报文 JSON 全文**（见下方拆解）|
| 6 | `info_response_body` | 🟡 待核 | 腾讯返回的响应，如 `{"code":0,"success":true,"succeed":true,"errCode":"0"}` |
| 5 | `info_result` | 🟡 待核 | **回调结果**，实测 `SUCCESS`（上报腾讯成功）|

## `info_request_body` 报文拆解 🔑

```json
{
  "account_id": 46801847,
  "user_action_set_id": 1205223677,
  "actions": [{
    "action_time": 1795319914,          → 2026-11-22 11:58:34（UTC+8）
    "action_type": "COMPLETE_ORDER",    → 下单，不是支付
    "action_param": {"value": 1090},    → 金额，单位「角」= 109.0 元 ⚠️
    "trace": {"click_id": "wx03xczu7ydki6ls01"}
  }]
}
```

| 字段 | 含义 | 注意 |
|:--|:--|:--|
| `account_id` | 腾讯广告账户 ID | 固定 |
| `user_action_set_id` | 用户行为数据集 ID | 固定 |
| `actions[].action_time` | 事件时间（Unix 秒）| 实测与 `info_callback_time` 完全一致 |
| `actions[].action_type` | 事件类型 | `COMPLETE_ORDER` = 下单 |
| `actions[].action_param.value` | **金额** | 🔴 **单位是「角」，不是「分」**！`1090` 角 = 109.0 元 |
| `actions[].trace.click_id` | 点击标识 | 与 `info_click_id` 一字不差 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:--|:--|:--|
| [[lucky_ad_click_log]] | `info_click_id` = `info_click_id` | 上游，确认点击来源渠道 |
| [[dws_eorder_eorder_d_his_combine]] | `info_order_no` = `eorder_no` | 🔑 拿 `mem_id` / `eorder_income` / `eorder_status`。**2026-11-22 实测命中率 100%** |

## 使用注意点

| # | 注意点 | 说明 |
|:-:|:--|:--|
| 1 | 🔴 **`info_event = '6'` 是下单不是支付** | 腾讯在用户点「提交订单」时就回调，此时**还没付钱**。2026-11-22 实测 1,057 单里 70 单 `eorder_pay_time IS NULL` 且状态 5（订单取消）——从未支付成功 |
| 2 | 🔴 **`dt` 是回调日，不是下单日** | 用 `dt` 框人群 ≠ 用 `eorder_pay_time` 框人群。两者差 70 单，会把取消率从 4.97% 虚高到 11.26% |
| 3 | 🔴 **必须 join 点击表加 `info_source`** | 本表是全渠道回调。2026-11-22 全渠道订单 336,014 条，`tencentad` 仅 1,057 条 |
| 4 | 🔴 **`action_param.value` 单位是「角」** | 除以 10 才是元。按腾讯文档当「分」用会差 10 倍 |
| 5 | 🟡 **`rowkey` 与 `info_order_no` 前缀相同不是线索** | 流水号编码规则巧合，实测两者后 9 位完全不同。验字段要靠 join 命中率，不靠格式推断 |
| 6 | 🟡 **可能有多次回调** | 同一订单可能重复上报。统计时 `distinct info_order_no` |
| 7 | 🟡 **本表无 `mem_id`** | 算「下单人数」必须关联订单表 |

## 典型 SQL

```sql
-- 取某天自营广告的回调订单号（去重）
with click_ids as (
    select distinct info_click_id
    from hbase.lucky_ad_click_log
    where dt = '2026-11-22' and info_source = 'tencentad'
      and info_click_id is not null and info_click_id <> ''
)
select distinct c.info_order_no
from hbase.lucky_ad_event_callback_log c
join click_ids k on c.info_click_id = k.info_click_id
where c.dt = '2026-11-22'
  and c.info_event = '6'
  and c.info_order_no is not null
  and c.info_order_no <> ''
```

```sql
-- 各事件类型的回调量
select info_event
     , count(distinct info_order_no) as 订单数
from hbase.lucky_ad_event_callback_log
where dt = '2026-11-22'
  and info_order_no is not null
  and info_order_no <> ''
group by info_event
```

```sql
-- 回调金额（注意单位是角）
select round(sum(cast(get_json_object(info_request_body, '$.actions[0].action_param.value') as double)) / 10, 2) as 回传金额_元
from hbase.lucky_ad_event_callback_log
where dt = '2026-11-22'
  and info_event = '6'
  and info_result = 'SUCCESS'
```

## 关联

[[数据字典索引]] · [[lucky_ad_click_log]] · [[dws_eorder_eorder_d_his_combine]] · [[广告归因分析SQL模板]]
