---
created: 2026-07-17
updated: 2026-07-17
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
```

## 表结构速查
- [[dws_eorder 电商订单表]]
- [[fact_dwd_log_c_luckinpop_detail 埋点表]]
- [[t_wecom_external_user 企业微信客户表]]

---
> 遇到新的坑随时补充
