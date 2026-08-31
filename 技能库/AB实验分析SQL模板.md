---
created: 2026-08-26
updated: 2026-08-26
tags: [SQL, AB实验, 技能库, 数据分析]
---

# AB 实验分析 SQL 模板（真实命中 × 埋点漏斗）

> 适用场景：统计「当天**真实命中**目标实验的用户」在黄金交易流程各节点的 UV 与点击率，输出粒度 天 × 实验 × 实验组。
> 来源：用户提供 @ 2026-08-26（即享新项目，vault 首个 AB 实验分析模板）

## 完整 SQL

```sql
/*
【即享】真实命中实验用户 - 黄金交易流程埋点指标统计
目标实验：TM119933085071438848
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
/* 公共启动留存主题事件，收敛到“天 × 人 × 平台 × 指标节点”。 */
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
WHEN event.event_code = 'web_page_start'
AND event.prop_page_id = '/pmall/order/confirm'
THEN '07_订单确认页曝光'
WHEN event.event_code = 'web_page_start'
AND event.prop_page_id LIKE '/pmall/payResult/success/%'
THEN '08_支付完成页曝光'
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
AND (
GET_JSON_OBJECT(event.prop_data, '$.web_url')
LIKE 'https://m.lkcoffee.com/pmall?%'
OR event.prop_page_id = '/pmall/order/confirm'
OR event.prop_page_id LIKE '/pmall/payResult/success/%'
)
)
)
),
/* 即享电商主题事件，保留新旧埋点版本。 */
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
AND event.event_code IN (
'lkinstant_productdetail_start',
'lucinpop_productdetail_start',
'ec_home_popup_bw',
'ec_home_popup_ck'
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
先按真实命中的同平台关联，再收敛到“天 × 人 × 实验组 × 指标节点”。
同一用户跨平台触发同一节点，实验组UV只计算一次。
*/
hit_event_member_daily AS (
SELECT
hit.dt,
hit.mem_id,
hit.test_id,
hit.test_template_no,
hit.testgroup_id,
event.event_node,
MAX(
CASE WHEN event.tracking_version = '新埋点' THEN 1 ELSE 0 END
) AS has_new_tracking,
MAX(
CASE WHEN event.tracking_version = '老埋点' THEN 1 ELSE 0 END
) AS has_old_tracking
FROM hit_member_platform hit
INNER JOIN event_member_daily_platform event
ON hit.dt = event.dt
AND hit.mem_id = event.mem_id
AND hit.platform = event.platform
GROUP BY
hit.dt,
hit.mem_id,
hit.test_id,
hit.test_template_no,
hit.testgroup_id,
event.event_node
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
END AS `弹窗点击率`
FROM daily_dimension dim
LEFT JOIN event_metric event
ON dim.dt = event.dt
AND dim.test_id = event.test_id
AND dim.test_template_no = event.test_template_no
AND dim.testgroup_id = event.testgroup_id
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

⚠️ **头部注释里的旧实验号（TM119933085071438848）与 params（TM119984592869390337）不一致，是历史残留**——每次使用时改 params，并同步改头部注释，避免误读。

## 数据流

1. **真实命中人群**：`dwm_mg_log_abtest_user_d_1d` → 天×人×组×平台 收敛 → 跨平台按会员去重 → 天×组 真实命中UV
2. **行为事件**：公共埋点（启动/首页/确认页/支付页）+ 电商埋点（商详新老/弹窗）→ 天×人×平台×节点 去重合并
3. **关联**：命中人群 ∩ 事件池（同天+同人+同平台 INNER JOIN）→ 天×人×组×节点，标记新老埋点
4. **输出**：LEFT JOIN 补 0，弹窗点击率防除零

## 节点定义

| 节点 | 含义 | 埋点来源 |
|:--|:--|:--|
| `00_启动` | app_start | 公共埋点 |
| `01_即享首页曝光` | 小程序 `pages/index/pmall` 或 H5 `m.lkcoffee.com/pmall?` | 公共埋点 |
| `02_商详页曝光` | `lkinstant_`(新) / `lucinpop_`(老) productdetail_start | 电商埋点 |
| `07_订单确认页曝光` | `/pmall/order/confirm` | 公共埋点 |
| `08_支付完成页曝光` | `/pmall/payResult/success/%` | 公共埋点 |
| `09_弹窗曝光` / `10_弹窗点击` | `ec_home_popup_bw` / `ec_home_popup_ck` | 电商埋点 |

## 口径要点

| 点 | 说明 |
|:--|:--|
| 人群口径 | 只用 DWM **真实上报命中**（不用 ADS 全量预分配表——预分配含"分配了但没真实命中"的用户） |
| UV 口径 | 全部按**会员去重**（人UV 非 PV）；跨平台触发同一节点只算一次 |
| 新老埋点拆分 | 同一用户新旧埋点都触发时，两个拆分都计 → **新UV+老UV 可能 > 商详总UV**，是拆分口径不是 bug，别加总对比 |
| 弹窗点击率 | **人点击率** = 点击UV ÷ 曝光UV（非次数 CTR），曝光=0 时返回 NULL 防除零 |
| 事件时间 | 不强制事件晚于 `first_report_time`，保留早于 AB 命中上报的"启动"等基线指标 |

## 注意事项

- `${start_date}` / `${end_date}`：若查询平台不自动替换模板变量，需硬编码成具体日期
- 性能：公共埋点 WHERE 里 OR 带 `get_json_object` 可能阻止谓词下推；跑得慢可拆成独立 UNION ALL 分支
- `first_report_time` / `last_report_time` 当前未在下游使用（预留字段）

## 关联表

| 表 | 说明 |
|:--|:--|
| `dw_dwm.dwm_mg_log_abtest_user_d_1d` | 命中人群（字典：[[企业沉淀/数据字典/dwm_mg_log_abtest_user_d_1d]]） |
| `dw_dwd.fact_dwd_log_c_start_retention_detail_d_inc` | 公共埋点（[[企业沉淀/数据字典/fact_dwd_log_c_start_retention_detail_d_inc]]） |
| `dw_dwd.fact_dwd_log_c_luckinpop_detail_d_inc` | 电商埋点（[[企业沉淀/数据字典/fact_dwd_log_c_luckinpop_detail_d_inc]]） |
| `dw_dim.dim_con_test_template_d_his` | 实验模板维度（字典待补全） |

关联：[[技能库索引]] · [[企业沉淀/数据字典/数据字典索引]] · [[业务分析/03-日常SQL/SQL分析模式参考]] · [[技能库/SQL经验库]]
