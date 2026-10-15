---
created: 2026-07-29
tags: [企业, 数据, 字典, 一物一码, 瓶内营销]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-29
---

# dim_inst_rtd_cap_activity_d_his — RTD 瓶盖复购活动维表

**数据库**：`dw_dim`

> 活动配置层面的维度表，定义活动的基础规则、限制条件、展示信息。

## 关联键

| 关联字段 | 关联表 | 说明 |
|:--------|:------|:----|
| `activity_id` / `activity_no` | [[ads_inst_cap_activity_win_grant_d_inc]] | 活动参与及中奖宽表 |

## 使用注意点

- DIM 层维度表，关联 ADS 宽表时注意一对多关系（一个活动对应多条参与记录）
- `enable_status` ≠ `activity_status`：活动可以「已启用但未开始」，取正在进行的活动要同时判断
- `marketing_scene = 'CAP_INNER'` 即瓶内营销，如果要过滤其他营销场景需注意

## 表结构（37 字段）

### 活动基本信息

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 1 | `activity_id` | 活动 ID |
| 2 | `activity_no` | 活动编号 |
| 3 | `activity_name` | 活动名称 |
| 4 | `activity_desc` | 活动规则说明 |
| 5 | `activity_start_time` | 活动开始时间 |
| 6 | `activity_end_time` | 活动结束时间 |
| 7 | `activity_status` | 活动状态：1未开始 2已开始 3已结束 |
| 8 | `enable_status` | 启用状态：1已新建 2已启用 3已停用 |
| 9 | `is_deleted` | 逻辑删除：0否 1是 |
| 10 | `marketing_scene` | 营销场景：CAP_INNER 瓶内营销 |

### 参与限制

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 11 | `user_win_limit_type` | 单用户中奖次数限制类型：0不限 1限定 |
| 12 | `user_win_max_cnt` | 单用户最多中奖次数 |
| 13 | `daily_draw_limit_type` | 每人每天限抽奖频次限制类型：0不限 1限定 |
| 14 | `daily_draw_max_cnt` | 每人每天限抽奖频次次数 |
| 15 | `join_limit_type` | 每人限参与次数限制类型：0不限 1限定 |
| 16 | `join_max_cnt` | 每人限参与次数 |

### 风控与策略

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 17 | `risk_hit_action` | 命中风控后中奖设置：0不中奖 1命中默认奖品 |
| 18 | `is_new_user_must_win` | 新客必中：0否 1是 |
| 19 | `is_city_limited` | 发放城市是否限定：0不限 1限定 |
| 20 | `is_show_private_domain` | 是否展示加私域：0否 1是 |
| 21 | `private_domain_banner_url` | 加私域展示图 URL |
| 22 | `scan_redirect_url` | 瓶身码跳转 HTTPS 落地页 |

### 审计信息

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 23 | `create_user_id` | 创建人编号 |
| 24 | `modify_user_id` | 修改人编号 |
| 25 | `create_user_name` | 创建人姓名 |
| 26 | `modify_user_name` | 修改人姓名 |
| 27 | `create_time` | 创建时间 |
| 28 | `modify_time` | 修改时间 |

### 展示配置

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 29 | `bg_portrait_url` | 活动背景竖图 URL |
| 30 | `bg_landscape_url` | 活动背景横图 URL |
| 31 | `lottery_animation_url` | 抽奖动效 URL |
| 32 | `lottery_animation_duration` | 抽奖动效时长（毫秒） |
| 33 | `bg_color` | 背景色 #RRGGBB |
| 34 | `no_win_img_url` | 未中奖大图 URL |

## 典型 SQL

```sql
-- 查询当前进行中的活动
SELECT
  activity_id,
  activity_no,
  activity_name,
  activity_start_time,
  activity_end_time,
  join_max_cnt,
  user_win_max_cnt,
  is_new_user_must_win,
  is_city_limited
FROM dw_dim.dim_inst_rtd_cap_activity_d_his
WHERE enable_status = 2        -- 已启用
  AND is_deleted = 0           -- 未删除
  AND activity_status = 2      -- 已开始
  AND CURRENT_DATE BETWEEN activity_start_time AND activity_end_time;
```

## 关联表

- [[ads_inst_cap_activity_win_grant_d_inc]] — 活动参与及中奖宽表（通过 activity_id 关联）
