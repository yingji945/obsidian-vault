---
created: 2026-10-12
updated: 2026-10-12
tags: [企业, 数据字典, 门店业务域, DWD, 商品分析, 埋点]
field_status: ✅ 完整（55/55 字段类型已按 SHOW CREATE TABLE 核定）
source: 字段列表 2026-10-12；类型由 SHOW CREATE TABLE 核定 2026-10-13（首次入库时曾用同族表交叉继承，8 个推断错误已修正）
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

> **类型**：55 个字段全部来自 `SHOW CREATE TABLE` 核定值（2026-10-13）。
> ⚠️ 注意本表**多数字段是 `string`**：经度/纬度、三个价格字段、各种 id 都是字符串，聚合或计算前需显式 `cast`。

### A. 主键与用户标识（6 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `rowkey` | `string` | 主键 |
| 2 | `open_id` | `string` | 微信授权id |
| 3 | `union_id` | `string` | 微信小程序唯一id |
| 4 | `login_id` | `string` | 登录id（可能是手机号、邮箱、员工号等） |
| 5 | `user_id` | `bigint` | 用户id |
| 6 | `distinct_id` | `string` | 设备id |

### B. 时间戳（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 7 | `event_time` | `bigint` | 时间时间 时间戳 |
| 8 | `server_time_form` | `string` | 数据上报时间 |
| 9 | `server_time` | `bigint` | 上报时间戳 |
| 10 | `event_time_form` | `string` | 事件时间 yyyy-MM-dd |

### C. 设备与环境（10 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 11 | `platform` | `int` | 平台 1ios 2安卓 3小程序 5支付宝小程序 6抖音小程序 |
| 12 | `app_version` | `string` | 版本 |
| 13 | `carrier` | `string` | 运营商 |
| 14 | `longitude` | `string` | 经度 |
| 15 | `latitude` | `string` | 纬度 |
| 16 | `system_language` | `string` | 系统语言 |
| 17 | `os_type` | `string` | 硬件操作系统类别 |
| 18 | `manufacturer` | `string` | 手机生产厂商 |
| 19 | `model` | `string` | 设备型号 |
| 20 | `app_name` | `string` | 应用名 |

### D. 地理位置（7 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 21 | `country` | `string` | 国家 |
| 22 | `country_id` | `bigint` | 国家ID |
| 23 | `province` | `string` | 省份 |
| 24 | `province_id` | `bigint` | 省份ID |
| 25 | `city` | `string` | 城市 |
| 26 | `city_id` | `bigint` | 城市ID |
| 27 | `region_code` | `string` | 经营地区编码 |

### E. 事件与会话（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 28 | `event_type` | `string` | 事件类别 |
| 29 | `event_code` | `string` | 事件code |
| 30 | `session_id` | `string` | 会话id |
| 31 | `current_page_code` | `string` | 页面code |

### F. AB 与门店（7 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 32 | `prop_abtest` | `string` | ab测试信息 |
| 33 | `prop_dept_id` | `string` | 门店部门id |
| 34 | `prop_shop_name` | `string` | 门店部门名称 |
| 35 | `prop_supporttakeout` | `int` | 取餐方式 |
| 36 | `prop_referer` | `string` | 前页面页面id |
| 37 | `prop_location` | `string` | 全局位置 |
| 38 | `prop_label_location` | `string` | 一级类目内位置 |

### G. 位置与类目（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 39 | `prop_position_code` | `string` | 位置code |
| 40 | `prop_position_name` | `string` | 位置名称 |
| 41 | `prop_first_label_name` | `string` | 一级类目名称 |
| 42 | `prop_second_label_name` | `string` | 二级类目名称 |

### H. 商品内容与售卖（9 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 43 | `prop_content_type` | `string` | 内容类型 1商品 2套餐 |
| 44 | `prop_content_id` | `string` | 内容id |
| 45 | `prop_content_value` | `string` | 内容值 |
| 46 | `prop_cmdty_price` | `string` | 商品原价 |
| 47 | `prop_cmdty_discount_price` | `string` | 划线价(折扣价) |
| 48 | `prop_cmdty_final_price` | `string` | 预估到手价 |
| 49 | `prop_sale_state` | `string` | 售卖状态 |
| 50 | `prop_ck_type` | `string` | 点击类型 仅限点击事件 |
| 51 | `prop_cmdty_sourcefrom` | `int` | 商品推荐规则 1-人工 2-算法 3-策略规则 0-无数据 |

### I. 策略与扩展（3 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 52 | `prop_plan_id` | `string` | 方案id |
| 53 | `prop_tactic_id` | `string` | 策略id |
| 54 | `prop_data` | `string` | 扩展字段 |

### J. 其他（1 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 55 | `business_language` | `string` | 语言 |
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

## 七、类型核定记录（2026-10-13）

| 阶段 | 情况 |
|:--|:--|
| 首次入库（10-12） | 只给了字段列表（无 DDL）→ 用**同族表交叉继承**得 39 个类型（标 `†`）+ 16 个待补 |
| DDL 到位（10-13） | 逐字段核对：**39 个继承值中 8 个推断错误** → 已全部按 DDL 真值修正 |
| 当前 | ✅ **55/55** 全部为 DDL 真实类型 |

### 继承推断错的 8 个（同族表类型 ≠ 本表类型）

| 字段 | 同族表（曾推断） | 本表真实 | 性质 |
|:--|:--|:--|:--|
| `server_time_form` | `datetime` | `string` | 承载类型不同 |
| `longitude` / `latitude` | `decimal` | **`string`** | ⚠️ 经纬度是**字符串**，算距离/落地图前必须 `cast` |
| `country_id` / `province_id` / `city_id` | `varchar` | **`bigint`** | ⚠️ 方向相反：同族表存字符串，本表存数值 |
| `platform` | `tinyint` | `int` | 宽度不同 |
| `prop_supporttakeout` | `varchar` | `int` | 承载类型不同 |

> 💡 **教训（写进技能）**：同族表交叉继承**只能当暂定值**——同族 fact 表各自的清洗/写入方式不同，`id`、经纬度、时间这类"**承载型**"字段最容易不一致。继承值必须标 `†` 并等 DDL 核对，不能当结论用。
>
> 💡 **本表的 `string` 陷阱**：`prop_cmdty_price` / `prop_cmdty_discount_price` / `prop_cmdty_final_price`（价格）与 `longitude` / `latitude`（经纬度）都是 **`string`** —— 直接 `sum()`/`avg()` 会走隐式转换甚至报错，必须 `cast(prop_cmdty_price as decimal(19,4))`。

---

## 八、待补

| 对象 | 说明 |
|:--|:--|
| `event_code` 事件清单 | 有哪些事件、各事件带哪些 `prop_` —— **待补**（影响「字段是否有值取决于事件类型」这条口径） |
| `prop_data` JSON 结构 | 扩展字段里有哪些 key |
| `prop_sale_state` / `prop_ck_type` 取值 | 中文备注型字段，取值清单待 `group by` 补 |
