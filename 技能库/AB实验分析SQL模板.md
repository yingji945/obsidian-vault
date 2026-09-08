---
created: 2026-08-26
updated: 2026-09-03
tags: [SQL, AB实验, 技能库, 数据分析]
---

# AB 实验分析 SQL 模板（真实命中 × 埋点漏斗 × 下单转化）

> 适用场景：统计「当天**真实命中**目标实验的用户」在黄金交易流程各节点的 UV、点击率与下单转化，输出粒度 天 × 实验 × 实验组。
> 来源：用户提供 @ 2026-08-26（即享新项目，vault 首个 AB 实验分析模板）；2026-09-03 修正确认页/支付页取数。

> ⚠️ **2026-09-03 修正记录**（重要，之前踩坑）：
> 1. **确认页/支付完成页取数换表+换字段**：旧版在公共表 `fact_dwd_log_c_start_retention_detail_d_inc` 用 `prop_page_id` 字段匹配 `/pmall/order/confirm`——**匹配不到**，确认页 UV 严重偏低（实测出现过 下单1065 vs 确认页168 的漏斗断裂假象）。实际这些 web 页面事件在**电商表** `fact_dwd_log_c_luckinpop_detail_d_inc` 的 `prop_data.page_id`（JSON）里，用 `GET_JSON_OBJECT(prop_data, '$.page_id')` 取。
> 2. **07/08 关联改跨平台**：确认页/支付页在电商表，`platform` 可能与 AB 命中表不一致，07/08 用会员级命中（天×人）关联；其余节点仍同平台关联（见 `hit_event_member_daily` 的两段 UNION ALL）。

## 完整 SQL

```sql
/*
【即享】真实命中实验用户 - 黄金交易流程埋点指标统计（含下单转化）
目标实验：TM119984592869390337
人群口径：
- 使用 dw_dwm.dwm_mg_log_abtest_user_d_1d；
- 只统计当天、对应平台真实上报过目标实验命中的用户；
- 不使用ADS全量预分配表作为实验人群。
输出粒度：
天 × 实验 × 实验组
指标：
1. 真实命中UV
2. 启动UV
3. 即享首页UV
4. 即享商品详情UV，并拆分新/老埋点
5. 即享订单确认页UV
6. 支付完成页UV
7. 弹窗曝光UV、弹窗点击UV、弹窗点击率
8. 下单人数、订单数、转化金额、下单转化率（关联 dws_eorder_eorder_d_his_combine，2026-08-26 扩展）
使用时只修改 params 中的日期和目标实验编号。
*/
WITH params AS (
SELECT
'${start_date}' AS start_date,
'${end_date}' AS end_date,
'TM119984592869390337' AS target_test_template_no
),
/*
DWM可能按会话产生多行，先收敛到“天 × 人 × 实验组 × 平台”。
平台范围与埋点表保持一致。
*/
hit_member_platform AS (
SELECT
hit.dt,
CAST(hit.mem_id AS STRING) AS mem_id,
hit.test_id,
hit.test_template_no,
hit.test_template_name,
hit.test_scene,
hit.testgroup_id,
hit.test_group_name,
hit.platform,
MIN(hit.first_report_time) AS first_report_time,
MAX(hit.last_report_time) AS last_report_time
FROM dw_dwm.dwm_mg_log_abtest_user_d_1d hit
CROSS JOIN params p
WHERE hit.dt BETWEEN p.start_date AND p.end_date
AND hit.mem_id IS NOT NULL
AND hit.test_template_no = p.target_test_template_no
AND hit.platform IN (1, 2, 3, 5)
GROUP BY
hit.dt,
CAST(hit.mem_id AS STRING),
hit.test_id,
hit.test_template_no,
hit.test_template_name,
hit.test_scene,
hit.testgroup_id,
hit.test_group_name,
hit.platform
),
/* 跨平台再次收敛，真实命中UV按会员去重。 */
hit_member_daily AS (
SELECT DISTINCT
dt,
mem_id,
test_id,
test_template_no,
test_template_name,
test_scene,
testgroup_id,
test_group_name
FROM hit_member_platform
),
daily_dimension AS (
SELECT
dt,
test_id,
test_template_no,
test_template_name,
test_scene,
testgroup_id,
test_group_name,
COUNT(*) AS actual_hit_uv
FROM hit_member_daily
GROUP BY
dt,
test_id,
test_template_no,
test_template_name,
test_scene,
testgroup_id,
test_group_name
),
/* 公共启动留存主题事件：只取启动 + 即享首页曝光（确认页/支付页在电商表，见下） */
public_event_member_daily AS (
SELECT DISTINCT
event.dt,
CAST(event.user_id AS STRING) AS mem_id,
event.platform,
'公共埋点' AS tracking_version,
CASE
WHEN event.event_code = 'app_start'
THEN '00_启动'
WHEN event.event_code = 'page_start'
AND event.prop_page_id = 'pages/index/pmall'
THEN '01_即享首页曝光'
WHEN event.event_code = 'web_page_start'
AND GET_JSON_OBJECT(event.prop_data, '$.web_url')
LIKE 'https://m.lkcoffee.com/pmall?%'
THEN '01_即享首页曝光'
END AS event_node
FROM dw_dwd.fact_dwd_log_c_start_retention_detail_d_inc event
CROSS JOIN params p
WHERE event.dt BETWEEN p.start_date AND p.end_date
AND event.platform IN (1, 2, 3, 5)
AND event.user_id IS NOT NULL
AND event.rowkey IS NOT NULL
AND event.event_code IN (
'app_start',
'page_start',
'web_page_start'
)
AND (
event.event_code = 'app_start'
OR (
event.event_code = 'page_start'
AND event.prop_page_id = 'pages/index/pmall'
)
OR (
event.event_code = 'web_page_start'
AND GET_JSON_OBJECT(event.prop_data, '$.web_url')
LIKE 'https://m.lkcoffee.com/pmall?%'
)
)
),
/*
即享电商主题事件：商详（新老埋点）+ 订单确认页 + 支付完成页 + 弹窗。
确认页/支付页用 web_page_start + prop_data.page_id（JSON）匹配 —— 2026-09-03 修正。
*/
commerce_event_member_daily AS (
SELECT DISTINCT
event.dt,
CAST(event.user_id AS STRING) AS mem_id,
event.platform,
CASE
WHEN event.event_code LIKE 'lkinstant%'
THEN '新埋点'
WHEN event.event_code LIKE 'lucinpop%'
OR event.event_code LIKE 'luckinpop%'
THEN '老埋点'
ELSE '通用活动埋点'
END AS tracking_version,
CASE
WHEN event.event_code IN (
'lkinstant_productdetail_start',
'lucinpop_productdetail_start'
) THEN '02_商详页曝光'
WHEN event.event_code = 'web_page_start'
AND GET_JSON_OBJECT(event.prop_data, '$.page_id') = '/pmall/order/confirm'
THEN '07_订单确认页曝光'
WHEN event.event_code = 'web_page_start'
AND GET_JSON_OBJECT(event.prop_data, '$.page_id') LIKE '/pmall/payResult/success/%'
THEN '08_支付完成页曝光'
WHEN event.event_code = 'ec_home_popup_bw'
THEN '09_弹窗曝光'
WHEN event.event_code = 'ec_home_popup_ck'
THEN '10_弹窗点击'
END AS event_node
FROM dw_dwd.fact_dwd_log_c_luckinpop_detail_d_inc event
CROSS JOIN params p
WHERE event.dt BETWEEN p.start_date AND p.end_date
AND event.platform IN (1, 2, 3, 5)
AND event.user_id IS NOT NULL
AND event.rowkey IS NOT NULL
AND (
event.event_code IN (
'lkinstant_productdetail_start',
'lucinpop_productdetail_start',
'ec_home_popup_bw',
'ec_home_popup_ck'
)
OR (
event.event_code = 'web_page_start'
AND (
GET_JSON_OBJECT(event.prop_data, '$.page_id') = '/pmall/order/confirm'
OR GET_JSON_OBJECT(event.prop_data, '$.page_id') LIKE '/pmall/payResult/success/%'
)
)
)
),
event_member_daily_platform AS (
SELECT
dt,
mem_id,
platform,
tracking_version,
event_node
FROM public_event_member_daily
WHERE event_node IS NOT NULL
UNION ALL
SELECT
dt,
mem_id,
platform,
tracking_version,
event_node
FROM commerce_event_member_daily
WHERE event_node IS NOT NULL
),
/*
确认页/支付完成页在电商表，platform 仍可能与 AB 命中表不一致，按天×人关联。
其余节点仍同平台关联。两段节点互斥（07/08 vs 非07/08），不会重复计数。
*/
hit_event_member_daily AS (
SELECT
dt,
mem_id,
test_id,
test_template_no,
testgroup_id,
event_node,
MAX(CASE WHEN tracking_version = '新埋点' THEN 1 ELSE 0 END) AS has_new_tracking,
MAX(CASE WHEN tracking_version = '老埋点' THEN 1 ELSE 0 END) AS has_old_tracking
FROM (
SELECT
hit.dt,
hit.mem_id,
hit.test_id,
hit.test_template_no,
hit.testgroup_id,
event.event_node,
event.tracking_version
FROM hit_member_daily hit
INNER JOIN event_member_daily_platform event
ON hit.dt = event.dt
AND hit.mem_id = event.mem_id
WHERE event.event_node IN (
'07_订单确认页曝光',
'08_支付完成页曝光'
)
UNION ALL
SELECT
hit.dt,
hit.mem_id,
hit.test_id,
hit.test_template_no,
hit.testgroup_id,
event.event_node,
event.tracking_version
FROM hit_member_platform hit
INNER JOIN event_member_daily_platform event
ON hit.dt = event.dt
AND hit.mem_id = event.mem_id
AND hit.platform = event.platform
WHERE event.event_node NOT IN (
'07_订单确认页曝光',
'08_支付完成页曝光'
)
) hit_event
GROUP BY
dt,
mem_id,
test_id,
test_template_no,
testgroup_id,
event_node
),
event_metric AS (
SELECT
dt,
test_id,
test_template_no,
testgroup_id,
SUM(CASE WHEN event_node = '00_启动' THEN 1 ELSE 0 END)
AS startup_uv,
SUM(CASE WHEN event_node = '01_即享首页曝光' THEN 1 ELSE 0 END)
AS instant_homepage_uv,
SUM(CASE WHEN event_node = '02_商详页曝光' THEN 1 ELSE 0 END)
AS product_detail_uv,
SUM(CASE
WHEN event_node = '02_商详页曝光'
AND has_new_tracking = 1
THEN 1 ELSE 0
END) AS new_product_detail_uv,
SUM(CASE
WHEN event_node = '02_商详页曝光'
AND has_old_tracking = 1
THEN 1 ELSE 0
END) AS old_product_detail_uv,
SUM(CASE WHEN event_node = '07_订单确认页曝光' THEN 1 ELSE 0 END)
AS order_confirm_uv,
SUM(CASE WHEN event_node = '08_支付完成页曝光' THEN 1 ELSE 0 END)
AS payment_success_uv,
SUM(CASE WHEN event_node = '09_弹窗曝光' THEN 1 ELSE 0 END)
AS popup_exposure_uv,
SUM(CASE WHEN event_node = '10_弹窗点击' THEN 1 ELSE 0 END)
AS popup_click_uv
FROM hit_event_member_daily
GROUP BY
dt,
test_id,
test_template_no,
testgroup_id
),
/* ===== 订单明细：天×人×单（全量快照最新分区 + 自营有效订单） ===== */
order_member_daily AS (
SELECT DISTINCT
date(o.eorder_pay_time) AS dt,
CAST(o.mem_id AS STRING) AS mem_id,
o.eorder_id AS oid,
o.eorder_income AS income
FROM dw_dws.dws_eorder_eorder_d_his_combine o
CROSS JOIN params p
WHERE o.dt = date_sub(current_date(), 1)
AND date(o.eorder_pay_time) BETWEEN p.start_date AND p.end_date
AND o.total_ecmdty_payable_money <> 0
AND o.eorder_status IN ('2','3','7','8','9','10')
AND o.merchant_type = 0
),
/* ===== 命中人群 ∩ 订单：天×人×组（订单表无平台，用会员级命中关联） ===== */
hit_order_member_daily AS (
SELECT
hit.dt,
hit.mem_id,
hit.test_id,
hit.test_template_no,
hit.testgroup_id,
COUNT(DISTINCT o.oid) AS order_cnt,
SUM(o.income) AS order_income
FROM hit_member_daily hit
INNER JOIN order_member_daily o
ON hit.dt = o.dt
AND hit.mem_id = o.mem_id
GROUP BY hit.dt, hit.mem_id, hit.test_id, hit.test_template_no, hit.testgroup_id
),
/* ===== 订单指标：天×组 ===== */
order_metric AS (
SELECT
dt, test_id, test_template_no, testgroup_id,
COUNT(*) AS order_user_cnt,
SUM(order_cnt) AS order_cnt,
SUM(order_income) AS order_income
FROM hit_order_member_daily
GROUP BY dt, test_id, test_template_no, testgroup_id
)
SELECT
dim.dt AS `日期`,
dim.test_id AS `实验ID`,
dim.test_template_no AS `实验编号`,
dim.test_template_name AS `实验名称`,
dim.test_scene AS `实验场景编码`,
dim.testgroup_id AS `实验组ID`,
dim.test_group_name AS `实验组名称`,
dim.actual_hit_uv AS `真实命中UV`,
COALESCE(event.startup_uv, 0) AS `启动UV`,
COALESCE(event.instant_homepage_uv, 0) AS `即享首页UV`,
COALESCE(event.product_detail_uv, 0) AS `即享商品详情UV`,
COALESCE(event.new_product_detail_uv, 0) AS `新埋点商品详情UV`,
COALESCE(event.old_product_detail_uv, 0) AS `老埋点商品详情UV`,
COALESCE(event.order_confirm_uv, 0) AS `即享订单确认页UV`,
COALESCE(event.payment_success_uv, 0) AS `支付完成页UV`,
COALESCE(event.popup_exposure_uv, 0) AS `弹窗曝光UV`,
COALESCE(event.popup_click_uv, 0) AS `弹窗点击UV`,
CASE
WHEN COALESCE(event.popup_exposure_uv, 0) > 0
THEN COALESCE(event.popup_click_uv, 0) * 1.0
/ event.popup_exposure_uv
ELSE NULL
END AS `弹窗点击率`,
COALESCE(ord.order_user_cnt, 0) AS `下单人数`,
COALESCE(ord.order_cnt, 0) AS `订单数`,
COALESCE(ord.order_income, 0) AS `转化金额`,
CASE WHEN dim.actual_hit_uv > 0
THEN COALESCE(ord.order_user_cnt, 0) * 1.0 / dim.actual_hit_uv
ELSE NULL
END AS `下单转化率`
FROM daily_dimension dim
LEFT JOIN event_metric event
ON dim.dt = event.dt
AND dim.test_id = event.test_id
AND dim.test_template_no = event.test_template_no
AND dim.testgroup_id = event.testgroup_id
LEFT JOIN order_metric ord
ON dim.dt = ord.dt
AND dim.test_id = ord.test_id
AND dim.test_template_no = ord.test_template_no
AND dim.testgroup_id = ord.testgroup_id
/*
不写ORDER BY和结尾分号，避免全局排序并兼容查询平台自动追加LIMIT。
本SQL统计“当天真实命中目标实验用户的当日行为”，不强制要求所有事件发生在
first_report_time之后，以保留通常早于AB命中上报的“启动”等基线指标。
*/
```

## 使用说明

只改 `params` 三处：

| 参数 | 说明 |
|:--|:--|
| `start_date` / `end_date` | 统计日期范围 |
| `target_test_template_no` | 目标实验编号 |

⚠️ 若查询平台不自动替换 `${start_date}`，需硬编码成具体日期（跑数时的实际版本可硬编码，模板保留变量形态）。

## 数据流

1. **真实命中人群**：`dwm_mg_log_abtest_user_d_1d` → 天×人×组×平台 收敛 → 跨平台按会员去重 → 天×组 真实命中UV
2. **行为事件**：公共埋点（启动/首页曝光）+ 电商埋点（商详新老/**订单确认页/支付完成页**/弹窗）→ 天×人×平台×节点 去重合并
3. **关联**：`07_确认页`/`08_支付页` 用会员级命中（天×人，跨平台）；其余节点用同平台命中（天×人×平台）→ 天×人×组×节点，标记新老埋点
4. **下单转化**：命中人群 ∩ 全量快照订单（天×人）→ 下单人数/订单数/金额
5. **输出**：LEFT JOIN 补 0，弹窗点击率、下单转化率防除零

## 节点定义

| 节点 | 含义 | 埋点来源 |
|:--|:--|:--|
| `00_启动` | app_start | 公共埋点 |
| `01_即享首页曝光` | 小程序 `pages/index/pmall` 或 H5 `m.lkcoffee.com/pmall?` | 公共埋点 |
| `02_商详页曝光` | `lkinstant_`(新) / `lucinpop_`(老) productdetail_start | 电商埋点 |
| `07_订单确认页曝光` | `web_page_start` + `prop_data.page_id = '/pmall/order/confirm'` | **电商埋点**（2026-09-03 修正，勿用公共表 prop_page_id） |
| `08_支付完成页曝光` | `web_page_start` + `prop_data.page_id LIKE '/pmall/payResult/success/%'` | **电商埋点**（同上） |
| `09_弹窗曝光` / `10_弹窗点击` | `ec_home_popup_bw` / `ec_home_popup_ck` | 电商埋点 |

## 口径要点

| 点 | 说明 |
|:--|:--|
| 人群口径 | 只用 DWM **真实上报命中**（不用 ADS 全量预分配表——预分配含"分配了但没真实命中"的用户） |
| UV 口径 | 全部按**会员去重**（人UV 非 PV）；跨平台触发同一节点只算一次 |
| 新老埋点拆分 | 同一用户新旧埋点都触发时，两个拆分都计 → **新UV+老UV 可能 > 商详总UV**，是拆分口径不是 bug，别加总对比 |
| 弹窗点击率 | **人点击率** = 点击UV ÷ 曝光UV（非次数 CTR），曝光=0 时返回 NULL 防除零 |
| 07/08 跨平台 | 确认页/支付页用会员级命中关联（不要求同平台），其余节点同平台——因电商表 platform 可能与命中表不一致 |
| 下单口径 | 命中用户中**当天支付有效订单**的人数/单量/`eorder_income` 金额；`merchant_type = 0` 自营、`total_ecmdty_payable_money <> 0` 剔0元、状态 2/3/7/8/9/10；订单表无 platform，与命中按 天+人 关联 |
| 下单转化率 | 下单人数 ÷ 真实命中UV（口径一致，可直接比） |
| 事件时间 | 不强制事件晚于 `first_report_time`，保留早于 AB 命中上报的"启动"等基线指标 |

## 注意事项

- **确认页/支付页匹配必须用电商表 `prop_data.page_id`（JSON）**——公共表 `prop_page_id` 字段匹配不到 `/pmall/order/confirm`，曾导致确认页 UV 严重偏低（下单 1065 vs 确认页 168 的假断裂）。详见本文档顶部修正记录
- 性能：公共埋点 WHERE 里 OR 带 `get_json_object` 可能阻止谓词下推；跑得慢可拆成独立 UNION ALL 分支
- `first_report_time` / `last_report_time` 当前未在下游使用（预留字段）
- 拆单：按 `eorder_id` 计单，拆单会算成多单——若线上模型按父单口径需改

## 关联表

| 表 | 说明 |
|:--|:--|
| `dw_dwm.dwm_mg_log_abtest_user_d_1d` | 命中人群（字典：[[企业沉淀/数据字典/dwm_mg_log_abtest_user_d_1d]]） |
| `dw_dwd.fact_dwd_log_c_start_retention_detail_d_inc` | 公共埋点：启动/首页曝光（[[企业沉淀/数据字典/fact_dwd_log_c_start_retention_detail_d_inc]]） |
| `dw_dwd.fact_dwd_log_c_luckinpop_detail_d_inc` | 电商埋点：商详/确认页/支付页/弹窗（[[企业沉淀/数据字典/fact_dwd_log_c_luckinpop_detail_d_inc]]） |
| `dw_dws.dws_eorder_eorder_d_his_combine` | 订单表（[[企业沉淀/数据字典/dws_eorder_eorder_d_his_combine]]） |
| `dw_dim.dim_con_test_template_d_his` | 实验模板维度（字典待补全） |

关联：[[技能库索引]] · [[企业沉淀/数据字典/数据字典索引]] · [[业务分析/03-日常SQL/SQL分析模式参考]] · [[技能库/SQL经验库]]
