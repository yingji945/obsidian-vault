---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 电商DWD]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# fact_dwd_log_c_luckinpop_detail_d_inc — 电商分析 DWD 主题事实表

**数据库**：`dw_dwd`

## 表结构（45 字段）

### 基础标识

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `rowkey` | string | 主键 |
| 2 | `open_id` | varchar | 微信授权 ID |
| 3 | `union_id` | varchar | 微信小程序唯一 ID（微信全域统一） |
| 4 | `login_id` | varchar | 登录 ID（可能是手机号、邮箱、员工号等） |
| 5 | `user_id` | bigint | 用户 ID（瑞幸侧会员 ID） |
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
| 28 | `event_code` | varchar | **事件 code**（核心字段） |
| 29 | `session_id` | varchar | 会话 ID |
| 30 | `current_page_code` | varchar | 页面 code |
| 31 | `prop_referer` | varchar | 前页面页面 ID |
| 32 | `prop_url` | varchar | 跳转链接 |
| 33 | `platform` | tinyint | 平台：`1`=iOS, `2`=安卓, `3`=小程序, `5`=支付宝小程序, `6`=抖音小程序 |

### 业务属性

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 34 | `prop_abtest` | varchar | AB 测试信息 |
| 35 | `prop_dept_id` | varchar | 门店部门 ID |
| 36 | `prop_shop_name` | varchar | 门店部门名称 |
| 37 | `prop_supporttakeout` | varchar | 取餐方式 |
| 38 | `prop_item_price` | decimal | 面价 |
| 39 | `prop_item_discountprice` | decimal | 划线价（折扣价） |
| 40 | `prop_item_id` | varchar | 商品 ID |
| 41 | `prop_item_name` | varchar | 商品名称 |
| 42 | `prop_item_number` | varchar | 数量 |
| 43 | `prop_location` | varchar | 位置顺序 |
| 44 | `prop_activity` | varchar | 活动信息 |
| 45 | `prop_data` | string | **扩展字段**（JSON 字符串，携带自定义事件参数） |
| 46 | `business_language` | varchar | 语言 |

## 使用注意点

- **mall 入口识别**：`event_code = 'web_page_start'` + `prop_data.web_url LIKE '%pmall%'`
- **商品详情页**：`event_code = 'lucinpop_productdetail_start'`
- **`prop_data` 是 JSON 字符串**，需要用 `get_json_object()` 或类似函数解析，避免不必要的解析
- **`user_id` 是瑞幸侧会员 ID**：可关联 `t_member.id`，空值表示未登录用户
- **`union_id` 是微信全域统一 ID**：不同于 `open_id`（不同公众号/小程序的 open_id 不同），`union_id` 跨所有微信应用统一
- **`platform` 是整数**，`1`=iOS, `2`=安卓, `3`=小程序 — 注意和 `t_third_parent_order` 的字符串 `platform` 类型不同
- **`event_time` 是时间戳（bigint）**，`event_time_form` 是格式化后的日期字符串，取事件日期优先用 `event_time_form`

关联：[[fact_dwd_log_c_start_retention_detail_d_inc]] · [[数据字典索引]]
