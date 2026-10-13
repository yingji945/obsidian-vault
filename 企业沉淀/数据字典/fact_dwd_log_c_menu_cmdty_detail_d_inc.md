---
created: 2026-10-12
updated: 2026-10-12
tags: [企业, 数据字典, 门店业务域, DWD, 商品分析, 埋点]
field_status: 🟡 39/55 有类型（继承同族表，待 DDL 核对）；16 个 prop_* 专属字段待补
source: 用户提供字段列表（2026-10-12）；类型参考同族表 fact_dwd_log_c_luckinpop_detail_d_inc / _start_retention_
---

# dw_dwd.fact_dwd_log_c_menu_cmdty_detail_d_inc

> **DWD 主题事实表 · 商品分析** —— 菜单/商品页的行为埋点（曝光、点击、坑位、类目、展示价、推荐规则）
> 粒度：1 行 = 1 条埋点事件 · 库：`dw_dwd` · 字段数：**55**（23 个 `prop_*` 业务属性 + 32 个标准埋点字段）

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `dw_dwd.fact_dwd_log_c_menu_cmdty_detail_d_inc` |
| 库 / 层级 | `dw_dwd` / **DWD 主题事实表**（`_d_inc` 日增量） |
| 业务域 | **门店业务域**（门店侧商品行为埋点；表名属 `fact_dwd_log_c_*` 家族，按**业务线**归域而非数据类型） |
| 角色 | **商品行为埋点明细**：商品在页面上的曝光/点击、位于哪个坑位、展示什么价、由什么规则推荐 |
| 粒度 | 埋点事件（1 行 = 1 次上报事件） |
| 字段数 | 55（10 组，见第三节） |
| 类型完整度 | 🟡 **39/55**（继承同族表；余 16 个 `prop_*` 待 DDL） |
| 数据来源 | `ods_log.t_hmonitor_track_event`（ODS 原始埋点全量） |

---

## 二、它在血缘里的位置

```
ods_log.t_hmonitor_track_event            埋点原始日志（ODS，85 字段，全量上报）
        │  清洗 + 按主题拆分
        ▼
dw_dwd.fact_dwd_log_c_*                    DWD 主题事实表家族
        ├── fact_dwd_log_c_luckinpop_detail_d_inc        电商分析
        ├── fact_dwd_log_c_start_retention_detail_d_inc  启动留存分析
        └── fact_dwd_log_c_menu_cmdty_detail_d_inc       ← 本表（商品分析）🆕
```

---

## 三、字段清单（55 字段 · 10 组）

> **类型标注**：带 `†` = 由**同族表继承**（`fact_dwd_log_c_luckinpop_*` 与 `_start_retention_*` 两张表中该字段**同名同类型、零冲突**，可靠性高）；`⚠️ 待补` = 本表专属字段，同族表无参考。

### A. 主键与用户标识（6 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `rowkey` | `string` † | 主键 |
| 2 | `open_id` | `varchar` † | 微信授权id |
| 3 | `union_id` | `varchar` † | 微信小程序唯一id |
| 4 | `login_id` | `varchar` † | 登录id（可能是手机号、邮箱、员工号等） |
| 5 | `user_id` | `bigint` † | 用户id |
| 6 | `distinct_id` | `varchar` † | 设备id |

### B. 时间戳（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 7 | `event_time` | `bigint` † | 时间时间 时间戳 |
| 8 | `server_time_form` | `datetime` † | 数据上报时间 |
| 9 | `server_time` | `bigint` † | 上报时间戳 |
| 10 | `event_time_form` | `string` † | 事件时间 yyyy-MM-dd |

### C. 设备与环境（10 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 11 | `platform` | `tinyint` † | 平台 1ios 2安卓 3小程序 5支付宝小程序 6抖音小程序 |
| 12 | `app_version` | `varchar` † | 版本 |
| 13 | `carrier` | `varchar` † | 运营商 |
| 14 | `longitude` | `decimal` † | 经度 |
| 15 | `latitude` | `decimal` † | 纬度 |
| 16 | `system_language` | `varchar` † | 系统语言 |
| 17 | `os_type` | `varchar` † | 硬件操作系统类别 |
| 18 | `manufacturer` | `varchar` † | 手机生产厂商 |
| 19 | `model` | `varchar` † | 设备型号 |
| 20 | `app_name` | `varchar` † | 应用名 |

### D. 地理位置（7 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 21 | `country` | `varchar` † | 国家 |
| 22 | `country_id` | `varchar` † | 国家ID |
| 23 | `province` | `varchar` † | 省份 |
| 24 | `province_id` | `varchar` † | 省份ID |
| 25 | `city` | `varchar` † | 城市 |
| 26 | `city_id` | `varchar` † | 城市ID |
| 27 | `region_code` | `varchar` † | 经营地区编码 |

### E. 事件与会话（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 28 | `event_type` | `varchar` † | 事件类别 |
| 29 | `event_code` | `varchar` † | 事件code |
| 30 | `session_id` | `varchar` † | 会话id |
| 31 | `current_page_code` | `varchar` † | 页面code |

### F. AB 与门店（7 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 32 | `prop_abtest` | `varchar` † | ab测试信息 |
| 33 | `prop_dept_id` | `varchar` † | 门店部门id |
| 34 | `prop_shop_name` | `varchar` † | 门店部门名称 |
| 35 | `prop_supporttakeout` | `varchar` † | 取餐方式 |
| 36 | `prop_referer` | `varchar` † | 前页面页面id |
| 37 | `prop_location` | `varchar(?)` † | 全局位置 |
| 38 | `prop_label_location` | ⚠️ 待补 | 一级类目内位置 |

### G. 位置与类目（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 39 | `prop_position_code` | ⚠️ 待补 | 位置code |
| 40 | `prop_position_name` | ⚠️ 待补 | 位置名称 |
| 41 | `prop_first_label_name` | ⚠️ 待补 | 一级类目名称 |
| 42 | `prop_second_label_name` | ⚠️ 待补 | 二级类目名称 |

### H. 商品内容与售卖（9 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 43 | `prop_content_type` | ⚠️ 待补 | 内容类型 1商品 2套餐 |
| 44 | `prop_content_id` | ⚠️ 待补 | 内容id |
| 45 | `prop_content_value` | ⚠️ 待补 | 内容值 |
| 46 | `prop_cmdty_price` | ⚠️ 待补 | 商品原价 |
| 47 | `prop_cmdty_discount_price` | ⚠️ 待补 | 划线价(折扣价) |
| 48 | `prop_cmdty_final_price` | ⚠️ 待补 | 预估到手价 |
| 49 | `prop_sale_state` | ⚠️ 待补 | 售卖状态 |
| 50 | `prop_ck_type` | ⚠️ 待补 | 点击类型 仅限点击事件 |
| 51 | `prop_cmdty_sourcefrom` | ⚠️ 待补 | 商品推荐规则 1-人工 2-算法 3-策略规则 0-无数据 |

### I. 策略与扩展（3 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 52 | `prop_plan_id` | ⚠️ 待补 | 方案id |
| 53 | `prop_tactic_id` | ⚠️ 待补 | 策略id |
| 54 | `prop_data` | `string` † | 扩展字段 |

### J. 其他（1 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 55 | `business_language` | `varchar` † | 语言 |
---

## 四、口径与使用注意点

| # | 注意点 |
|:-:|:--|
| 1 | 🔴 **埋点里的价格不是成交价**：`prop_cmdty_price`（商品原价）、`prop_cmdty_discount_price`（划线价/折扣价）、`prop_cmdty_final_price`（**预估**到手价）都是**页面展示值**。与门店业务域的真实成交金额（`cmdty_pay_amt` 等）**口径不同、不可混用**，只能用于"展示 vs 成交"的漏斗对比 |
| 2 | **`prop_*` 字段是否有值取决于事件类型**：例如 `prop_ck_type`（点击类型）「仅限点击事件」。做分析前**先看 `event_code` 分布**，否则会把"字段为空"误判成"无数据" |
| 3 | **`platform` 枚举缺 4**：1 ios / 2 安卓 / 3 小程序 / 5 支付宝小程序 / 6 抖音小程序 —— **没有 4**，写过滤条件时不要按连续整数假设 |
| 4 | **`prop_content_type`**：1 商品 / 2 套餐 —— 统计商品数时要区分，否则套餐与商品会混算 |
| 5 | **`prop_cmdty_sourcefrom`（推荐规则）**：1 人工 / 2 算法 / 3 策略规则 / **0 无数据** —— 做"算法 vs 人工"效果对比时，**0 要单独处理**（不是"人工"，是没数据） |
| 6 | **门店字段**：`prop_dept_id`（门店部门 id）/ `prop_shop_name`（门店部门名称）/ `prop_supporttakeout`（取餐方式）→ 本表是**门店侧**点单场景的埋点，非电商商城 |
| 7 | `prop_data` 是**扩展字段**（JSON 串），需要 `get_json_object` 解析，且**不是每行都有** |
| 8 | 埋点是**行为数据**：同一用户同一商品会因多次曝光/点击产生多行；去重口径用 `distinct_id`（设备）或 `user_id`（会员），**两者覆盖人群不同**（未登录只有设备） |
| 9 | 时间字段区分：`event_time`（事件发生，时间戳）/ `server_time`（上报到服务器，时间戳）/ `event_time_form`（事件日期 yyyy-MM-dd）。**上报可能延迟**，跨天分析建议用 `event_time` |

---

## 五、典型 SQL

```sql
-- ① 商品曝光 → 点击 漏斗（按页面）
select current_page_code,
       count(if(event_code like '%expose%', 1, null)) as expose_cnt,
       count(if(event_code like '%click%',  1, null)) as click_cnt,
       round(count(if(event_code like '%click%', 1, null)) / count(if(event_code like '%expose%', 1, null)), 4) as ctr
from dw_dwd.fact_dwd_log_c_menu_cmdty_detail_d_inc
where event_time_form = date_sub(current_date(), 1)
group by current_page_code
order by expose_cnt desc

-- ② 推荐规则效果对比（注意 0 = 无数据，不是人工）
select prop_cmdty_sourcefrom,
       case prop_cmdty_sourcefrom when 1 then '人工' when 2 then '算法'
            when 3 then '策略规则' when 0 then '无数据' end as rule_name,
       count(distinct distinct_id) as device_cnt,
       count(1) as event_cnt,
       avg(prop_cmdty_final_price) as avg_final_price
from dw_dwd.fact_dwd_log_c_menu_cmdty_detail_d_inc
where event_time_form = date_sub(current_date(), 1)
  and prop_content_type = 1                      -- 只看商品，排除套餐
group by prop_cmdty_sourcefrom
order by event_cnt desc

-- ③ 门店维度：各门店商品曝光 Top（含套餐需另切 prop_content_type）
select prop_dept_id, prop_shop_name,
       count(distinct prop_content_id) as cmdty_cnt,
       count(1) as expose_cnt
from dw_dwd.fact_dwd_log_c_menu_cmdty_detail_d_inc
where event_time_form between date_sub(current_date(), 7) and date_sub(current_date(), 1)
  and prop_content_type = 1
group by prop_dept_id, prop_shop_name
order by expose_cnt desc
```

---

## 六、关联

- 索引：[[数据字典索引]] · 分层：[[数据仓库分层说明]]
- **同族表**：[[fact_dwd_log_c_luckinpop_detail_d_inc]]（电商分析）· [[fact_dwd_log_c_start_retention_detail_d_inc]]（启动留存分析）
- **数据源**：[[ods_log_t_hmonitor_track_event]]（ODS 埋点原始日志）
- **同属门店业务域**（交易数据，与本表埋点口径不同）：
  - [[dwm_mg_order_cmdty_market_wide_d_inc]] —— 订单商品基础表（**成交**口径）
  - [[dwm_mg_order_cmdty_market_wide_d_view]] —— 订单商品渠道归因视图
  - [[dwm_mg_order_cmdty_channel_bridge_d_inc]] —— 渠道桥
  - [[dim_channel_level_d_his]] —— 渠道归因维
  - [[dim_sku_ord_rmk_d_a]] —— 订单商品属性维

---

## 七、待补

| 对象 | 说明 |
|:--|:--|
| **16 个 `prop_*` 字段类型** | `prop_position_code` / `prop_content_id` / `prop_cmdty_*` / `prop_plan_id` 等本表专属字段，同族表无参考 —— **需 `DESC` 或 DDL** |
| 39 个继承类型**核对** | 继承自同族表，需 DDL 最终确认 |
| `event_code` 事件清单 | 有哪些事件、各事件带哪些 `prop_` —— **待补**（影响第 2 条注意点） |
| `prop_data` JSON 结构 | 扩展字段里有哪些 key |
