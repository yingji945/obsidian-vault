---
created: 2026-07-17
updated: 2026-07-17
tags: [个人, SQL, 技能]
---

# SQL 经验库

## 常用表结构

### 瓶盖扫码活动宽表 `dw_ads.ads_inst_cap_activity_win_grant_d_inc`

> 即享-瓶盖扫码活动参与及中奖宽表。一物一码项目核心 ADS 表，覆盖从参与→中奖→膨胀→履约全链路。

```sql
-- 表 dw_ads.ads_inst_cap_activity_win_grant_d_inc
SELECT
  participate_id,             -- 活动参与记录 ID
  participate_time,           -- 参与时间
  activity_id,                -- 活动 ID
  activity_no,                -- 活动编号
  activity_name,              -- 活动名称
  mem_id,                     -- 会员 ID
  scan_id,                    -- 扫码 ID
  participate_phase,          -- 参与阶段
  layer_break_code,           -- 拦截层诊断码
  hit_result,                 -- 命中结果
  record_id,                  -- 用户中奖记录 ID
  activity_record_no,         -- 活动记录编号
  win_time,                   -- 中奖时间
  claim_time,                 -- 路径确认时间
  prize_row_id,               -- 命中基础奖品行 ID
  prize_name,                 -- 奖品名称
  base_content_type,          -- 基础内容类型
  base_grant_mode,            -- 基础获得方式
  base_grant_mode_snap,       -- 基础获得方式快照
  is_expand_support,          -- 是否支持膨胀
  expand_option_id,           -- 膨胀选项 ID
  exp_prize_row_id,           -- 膨胀对应奖品行 ID
  is_expand,                  -- 是否膨胀获得
  expand_prize_name,          -- 膨胀奖品名称
  expand_target_type,         -- 膨胀目标类型
  expand_grant_mode,          -- 膨胀获得方式
  final_grant_mode,           -- 最终获得方式
  fulfillment_phase,          -- 履约阶段
  grant_item_cnt_snap,        -- 发放明细数量快照
  grant_item_cnt,             -- 实际发放明细数量
  redpack_grant_cnt,          -- 红包发放数量
  inst_coupon_grant_cnt,      -- 即时券发放数量
  cfcoupon_grant_cnt,         -- 咖啡库券发放数量
  coffee_store_coupon_grant_cnt, -- 咖啡店券发放数量
  first_grant_time,           -- 首次发放时间
  last_grant_time,            -- 最后发放时间
  redpack_instance_cnt,       -- 红包实例数量
  redpack_transferred_cnt,    -- 红包已转账数量
  redpack_not_transferred_cnt,-- 红包未转账数量
  redpack_transferred_amt,    -- 红包已转账金额
  last_transfer_done_time,    -- 最后转账完成时间
  fulfillment_fail_code,      -- 履约失败码
  fulfillment_fail_reason,    -- 履约失败原因
  fulfillment_fail_time,      -- 履约失败时间
  fulfillment_retry_cnt       -- 履约重试次数
FROM
  dw_ads.ads_inst_cap_activity_win_grant_d_inc
```

> 🔗 关联项目：[[一物一码索引]]

### RTD 瓶盖复购活动维表 `dw_dim.dim_inst_rtd_cap_activity_d_his`

> RTD 瓶盖复购活动维表（即享业务）。活动配置层面的维度表，定义活动的基础规则、限制、展示信息。

```sql
-- 表 dw_dim.dim_inst_rtd_cap_activity_d_his
SELECT
  activity_id,               -- 活动 ID
  activity_no,               -- 活动编号
  activity_name,             -- 活动名称
  activity_desc,             -- 活动规则说明
  activity_start_time,       -- 活动开始时间
  activity_end_time,         -- 活动结束时间
  activity_status,           -- 活动状态 1未开始 2已开始 3已结束
  enable_status,             -- 启用状态 1已新建 2已启用 3已停用
  is_deleted,                -- 逻辑删除 0否 1是
  marketing_scene,           -- 营销场景 CAP_INNER 瓶内营销
  user_win_limit_type,       -- 单用户中奖次数限制类型 0不限 1限定
  user_win_max_cnt,          -- 单用户最多中奖次数
  daily_draw_limit_type,     -- 每人每天限抽奖频次限制类型 0不限 1限定
  daily_draw_max_cnt,        -- 每人每天限抽奖频次次数
  join_limit_type,           -- 每人限参与次数限制类型 0不限 1限定
  join_max_cnt,              -- 每人限参与次数
  risk_hit_action,           -- 命中风控后中奖设置 0不中奖 1命中默认奖品
  is_new_user_must_win,      -- 新客必中 0否 1是
  is_city_limited,           -- 发放城市是否限定 0不限 1限定
  is_show_private_domain,    -- 是否展示加私域 0否 1是
  private_domain_banner_url, -- 加私域展示图 URL
  scan_redirect_url,         -- 瓶身码跳转 HTTPS 落地页
  create_user_id,            -- 创建人编号
  modify_user_id,            -- 修改人编号
  create_user_name,          -- 创建人姓名
  modify_user_name,          -- 修改人姓名
  create_time,               -- 创建时间
  modify_time,               -- 修改时间
  bg_portrait_url,           -- 活动背景竖图 URL
  bg_landscape_url,          -- 活动背景横图 URL
  lottery_animation_url,     -- 抽奖动效 URL
  lottery_animation_duration,-- 抽奖动效时长(毫秒)
  bg_color,                  -- 背景色#RRGGBB
  no_win_img_url             -- 未中奖大图 URL
FROM
  dw_dim.dim_inst_rtd_cap_activity_d_his
```

> 🔗 关联项目：[[一物一码索引]]

### 企微加好友明细 `dw_dwd.dwd_mg_tch_wecom_user_action_d_inc`

> 社群-加好友明细记录，lucky/luna（企业微信客户历史）

```sql
-- 表 dw_dwd.dwd_mg_tch_wecom_user_action_d_inc
SELECT
  id,              -- 自增主键
  lucky_user_id,   -- 服务人员的user id
  mem_id,          -- 用户id
  lucky_user_name, -- 服务人员名称
  external_user_id,-- 外部联系人userid
  external_user_name, -- 外部联系人名称
  wx_unionid,      -- 微信unionid
  event_type,      -- 事件的类型
  event_time,      -- 时间发生时间
  state,           -- 加好友的渠道
  brand_type,      -- 品牌类型 LK001 luckin coffee / LK002 小鹿茶
  created_time,    -- 创建时间
  modified_time    -- 修改时间
FROM
  dw_dwd.dwd_mg_tch_wecom_user_action_d_inc
```

## 基础规范

### 日期写法
| 错误 | 正确 | 引擎 |
|:----|:-----|:-----|
| `now()` | `current_date()` | Spark SQL |
| `DATEDIFF(month, ...)` | `months_between(...)` | Spark SQL |
| `date_sub(now(), 1)` | `date_sub(current_date(), 1)` | Spark SQL |

### WHERE 条件
```sql
-- ❌ 错误：OR 写法，永远为 true
event_code = 'a' or 'b'

-- ✅ 正确
event_code IN ('a', 'b')

-- ✅ 区间用半开
event_time >= '2026-07-01 00:00:00'
AND event_time <  '2026-07-02 00:00:00'
```

## 性能优化

### Broadcast Hint
```sql
/*+ broadcast(小表名) */
```
小表 join 大表时加，避免 shuffle。

### OR 拆 UNION ALL
```sql
-- ❌ 慢：OR 阻止分区下推，JSON解析落到全表
WHERE (event_code = 'web_page_start' AND json条件)
   OR event_code IN (多个值)

-- ✅ 快：拆成两个子查询 + UNION ALL
WHERE event_code = 'web_page_start' AND json条件
UNION ALL
WHERE event_code IN (多个值)
```

### get_json_object
- 每条记录都要解析 JSON，非常慢
- 能过滤先过滤，让 JSON 解析只落在需要的行上
- `LIKE '前缀%'` 比 `LIKE '%任意%'` 快（前缀匹配可优化）

## 常用过滤口径

### 有效订单
```sql
eorder_status IN ('2','3','7','8','9','10')
total_ecmdty_payable_money <> 0  -- 剔除门店兑换单
```

## 表结构速查
- 完整字段见 [[数据字典索引]]
---

## 🔧 对话修正记录

> 每当我帮你改 SQL 时发现的常见错误，按时间倒序排列。新手入组可以先翻这部分。

### 2026-07-28 | 用户分层SQL — 全量快照表不需要加时间下限

**场景：** 写新客/留存/沉默分层，`t1` 里自动加了 `>= '2024-01-01'`

❌ `where dt = date_sub(current_date(), 1) and date(eorder_pay_time) >= '2024-01-01'`
✅ `where dt = date_sub(current_date(), 1)` 即可

**💡 原因：** `dws_eorder_eorder_d_his_combine` 是**全量快照表**，一个分区包含所有历史订单，加下限反而会丢失历史数据（沉默用户就判断不出来了）。
**预防原则：** 写 SQL 前先确认表模型——全量快照 vs 增量分区 vs 拉链表，确定是否需要时间下限。

### 2026-07-28 | 用户分层SQL — 窗口参数只改一处

**场景：** 你说要支持 Q1/H1 切换，我一开始在 `target_users` 和 `left join o` 两处各自改

❌ 在 CTE `target_users` 和下游 `left join t1 o` 分别改窗口过滤
✅ 所有下游 CTE 从同一个 `t1` 派生，在 `t1` 加 `date(eorder_pay_time) <= '截止时间'` 一改全改

**💡 原因：** 数据流是 `t1 → 各CTE → final`，控制点只在 `t1`，不需要在每条支路都加阀门。
**预防原则：** 画数据流，找到**单一控制点**再下笔。如果所有支路都从同一个 CTE 衍生，只改那个 CTE。

---

> 本文档持续更新。每次 Hermes 帮你改完 SQL，他会自动追加一条到这里。
>
> 关联：[[知识库首页]] · [[我的判断标准]]（你的SQL品味） · [[数据字典索引]] · [[运营数据分析方法论]] · [[用户分层SQL模板]]
