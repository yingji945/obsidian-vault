---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 电商DWD]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# fact_dwd_log_c_start_retention_detail_d_inc — 启动留存分析 DWD 主题事实表

**数据库**：`dw_dwd`

## 表结构（47 字段）

### 基础标识

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `rowkey` | string | 主键 |
| 2 | `open_id` | varchar | 微信授权 ID |
| 3 | `union_id` | varchar | 微信小程序唯一 ID |
| 4 | `login_id` | varchar | 登录 ID（手机号/邮箱/员工号等） |
| 5 | `user_id` | bigint | 用户 ID |
| 6 | `distinct_id` | varchar | 设备 ID |

### 时间戳

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 7 | `event_time` | bigint | 事件时间（时间戳） |
| 8 | `server_time_form` | datetime | 数据上报时间 |
| 9 | `server_time` | bigint | 上报时间戳 |
| 10 | `event_time_form` | string | 事件时间（`yyyy-MM-dd` 格式） |

### 设备 & 环境

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 11 | `app_version` | varchar | 版本 |
| 12 | `carrier` | varchar | 运营商 |
| 13 | `longitude` | decimal | 经度 |
| 14 | `latitude` | decimal | 纬度 |
| 15 | `system_language` | varchar | 系统语言 |
| 16 | `os_type` | varchar | 硬件操作系统类别 |
| 17 | `manufacturer` | varchar | 手机生产厂商 |
| 18 | `model` | varchar | 设备型号 |
| 19 | `app_name` | varchar | 应用名 |

### 地理位置

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 20 | `country` | varchar | 国家 |
| 21 | `country_id` | varchar | 国家 ID |
| 22 | `province` | varchar | 省份 |
| 23 | `province_id` | varchar | 省份 ID |
| 24 | `city` | varchar | 城市 |
| 25 | `city_id` | varchar | 城市 ID |
| 26 | `region_code` | varchar | 经营地区编码 |

### 事件 & 页面

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 27 | `event_type` | varchar | 事件类别 |
| 28 | `event_code` | varchar | **事件 code** |
| 29 | `session_id` | varchar | 会话 ID |
| 30 | `current_page_code` | varchar | 页面 code |
| 31 | `prop_referer` | varchar | 前页面页面 ID |
| 32 | `platform` | tinyint | 平台：`1`=iOS, `2`=安卓, `3`=小程序, `5`=支付宝, `6`=抖音 |

### 启动相关（核心差异字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 33 | `prop_launch_type` | varchar | 启动类别：`1`=冷启动, `2`=热启动 |
| 34 | `prop_launch_source` | varchar | 启动场景（如从哪个入口启动） |
| 35 | `prop_path` | varchar | 路径 |
| 36 | `prop_query` | varchar | 扩展属性（URL query 参数对） |
| 37 | `prop_query_source` | varchar | **来源（渠道码）** — 核心渠道分析字段 |
| 38 | `prop_query_invite_code` | varchar | 邀请码 |
| 39 | `prop_query_source_desc` | varchar | 来源描述 |
| 40 | `prop_page_id` | varchar | 页面 ID |
| 41 | `prop_redirect_h5` | varchar | H5 链接 |
| 42 | `prop_data` | string | **扩展字段**（JSON 字符串） |

### 门店 & AB 测试

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 43 | `prop_abtest` | varchar | AB 测试信息 |
| 44 | `prop_dept_id` | varchar | 门店部门 ID |
| 45 | `prop_shop_name` | varchar | 门店部门名称 |
| 46 | `prop_supporttakeout` | varchar | 取餐方式 |
| 47 | `business_language` | varchar | 语言 |

## 使用注意点

- **渠道分析核心表**：`prop_query_source` 是渠道码，分析流量来源时优先用这张表
- **启动类型**：`prop_launch_type = 1` 冷启动（首次启动或从后台被杀后启动），`= 2` 热启动（从后台切回前台）
- **非投放渠道判断**：`prop_query_source IS NULL OR prop_query_source NOT IN (投放渠道码列表)` — 投放渠道码列表见 [[数据字典索引]]
- **`prop_query` 是 URL query 参数**：如 `?source=xxx&channel=yyy` 这种键值对，解析时注意
- **`prop_page_id` 和 `current_page_code` 的区别**：`prop_page_id` 是跳转的目标页面 ID，`current_page_code` 是当前页面 code
- **和 `fact_dwd_log_c_luckinpop_detail_d_inc` 的区别**：这张表聚焦**启动/页面浏览/留存分析**，有启动专属字段（`prop_launch_type`、`prop_launch_source`、`prop_query_source`）；那张表聚焦**电商交易链路**，有商品/优惠/活动字段

## 典型 SQL

```sql
-- 某渠道的启动 UV
select
  date(event_time_form) as event_date,
  count(distinct user_id) as uv,
  count(distinct distinct_id) as device_uv
from dw_dwd.fact_dwd_log_c_start_retention_detail_d_inc
where event_code = 'app_start'
  and prop_query_source = 'DS-GZH17'
  and event_time_form >= '2026-07-01'
  and event_time_form < '2026-07-08'
group by date(event_time_form);

-- 非投放渠道整体量
select
  count(distinct user_id) as non_ad_uv
from dw_dwd.fact_dwd_log_c_start_retention_detail_d_inc
where event_code = 'app_start'
  and event_time_form = '2026-07-23'
  and (prop_query_source is null
    or prop_query_source not in ('DS-GZH17','DS-GZH19' /*...投放列表*/));
```

关联：[[fact_dwd_log_c_luckinpop_detail_d_inc]] · [[数据字典索引]]
