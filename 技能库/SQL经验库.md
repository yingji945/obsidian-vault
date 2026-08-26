---
created: 2026-07-17
updated: 2026-08-26
tags: [个人, SQL, 技能]
---

# SQL 经验库

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
merchant_type = 0                -- 瑞幸即享自营口径，排除POP第三方
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

### 2026-08-26 | 用户分层SQL — DATEDIFF(month) 3参报错 + 跨月窗口用户重复计数

**场景：** 7/20~8/3 窗口用户分层（新客/前3个月留存/沉默3个月回流），join 用 `DATEDIFF(month, b.ym, a.ym)`，且窗口横跨 7、8 两月

❌ `and DATEDIFF(month, b.ym, a.ym) between 1 and 3` — 编译报错 `Invalid number of arguments for function datediff. Expected: 2; Found: 3`
✅ `and months_between(to_date(concat(a.ym,'-01')), to_date(concat(b.ym,'-01'))) between 1 and 3`

❌ `a` 子查询按 `(ym, mem_id)` 去重 — 7月和8月都下单的用户出现两行，同一用户可能同时进「新客」和「前3个月留存」两个桶，人数/单量/收入重复计数
✅ `a` 按 mem_id 取 `min(ym)` 一个代表月，一人一行只归一类

**💡 原因：** ① Spark SQL 的 `datediff` 只支持 2 参（返回天数），3 参月份版是 SQL Server/Databricks 语法；`'2026-05'` 这类年月字符串直接进日期函数会解析失败返回 NULL，需 `concat('-01')` 补全成完整日期。② 分析窗口跨自然月时，按月粒度取用户会产生多行，跨桶重复计数。
**预防原则：** ① 月份差值一律用 `months_between(后面的日期, 前面的日期)`，年月字符串先 `concat('-01')` 再 to_date，别用 3 参 DATEDIFF；② 窗口跨月时，分层基准先按 mem_id 去重（取 `min(ym)`）再分类，避免一人进两桶。

---

> 本文档持续更新。每次 Hermes 帮你改完 SQL，他会自动追加一条到这里。
>
> 关联：[[知识库首页]] · [[我的判断标准]]（你的SQL品味） · [[数据字典索引]] · [[运营数据分析方法论]] · [[用户分层SQL模板]]
