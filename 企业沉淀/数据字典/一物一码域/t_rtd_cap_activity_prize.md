---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 一物一码]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# t_rtd_cap_activity_prize — 活动奖品行

**数据库**：`lucky_epromotion`

## 表结构（30 字段）

### 基础标识

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `id` | bigint | 主键 |
| 2 | `activity_id` | bigint | 活动 ID |
| 3 | `prize_name` | varchar | 奖品名称（运营展示用） |
| 4 | `prize_sort` | int | 奖品序号 |

### 奖品类型 & 内容

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 5 | `prize_type` | varchar | 奖品类型：`AUTO_ISSUE`=自动发券 |
| 6 | `content_type` | varchar | 内容类型：`RED_PACK`=红包, `INSTANT_COUPON`=即时券, `COFFEE_COUPON`=咖啡券, `COFFEE_STORE_COUPON`=门店券 |
| 7 | `prize_content_value` | varchar | 方案编号（与 `content_type` 联合校验） |
| 8 | `prize_grant_mode` | varchar | 基础路径发放方式：`DIRECT`=直接, `PRIVATE_DOMAIN`=私域, `REPURCHASE`=复购 |
| 9 | `ext` | text | JSON 扩展字段，见 `RtdCapActivityPrizeExt`：奖品侧、膨胀侧、发放方式等 |

### 膨胀 & 默认

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 10 | `is_expand` | tinyint | 该行是否膨胀：`0`=否, `1`=是 — **行级权威判断** |
| 11 | `default_prize` | tinyint | 是否默认奖项：`0`=否, `1`=是。全活动至多一行为 `1`；须 `repeat_type=1`, `limit_num=0`, `probability_limit=0`；未中非默认奖时兜底 |

### 数量 & 概率

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 12 | `limit_num` | tinyint | 奖品数量限制：`0`=不限, `1`=限定 |
| 13 | `prize_num` | int | 奖品总数量（`limit_num=1` 时必填正整数） |
| 14 | `won_qty` | int | 已中奖数量（系统回写，件） |
| 15 | `probability_limit` | tinyint | 中奖概率限制：`0`=不限, `1`=限定 |
| 16 | `probability` | decimal | 中奖概率百分数（0~100，`probability_limit=1` 时必填，最多6位小数） |

### 限购 & 去重

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 17 | `repeat_type` | tinyint | 是否允许重复获得：`0`=否, `1`=是 |
| 18 | `unit_limit_type` | tinyint | 单位限购类别：`NULL`或`0`=不限, `1`=自然日全用户合计 |
| 19 | `unit_limit_num` | int | 单位限购数量（`unit_limit_type=1` 时当日全用户合计上限） |
| 20 | `unit_limit_hour_type` | tinyint | 小时限购类型：`NULL`或`0`=不限, `1`=每1小时桶, `2`=每4小时桶, `3`=每8小时桶。自然时间对齐 |
| 21 | `unit_limit_hour_num` | int | 小时限购数量（当前桶内活动奖品行全用户合计发放上限） |
| 22 | `new_guest_win_priority` | int | 新客必中定奖优先级：值越小越优先。`is_new_guest_must_win=0` 时忽略 |

### 发放数量 & 渠道

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 23 | `grant_qty` | int | 基础路径每模板发放数量 |
| 24 | `private_domain_channel_qr_code_url` | varchar | 基础路径加私域渠道码 HTTPS URL（`prize_grant_mode=PRIVATE_DOMAIN` 时必填） |

### 图片素材

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 25 | `prize_image_url` | varchar | 奖品大图 HTTPS URL（二期保存必填） |
| 26 | `expand_effect_image_url` | varchar | 膨胀效果大图 HTTPS URL（`is_expand=1` 时必填） |

### 时间

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 27 | `create_time` | datetime | 创建时间 |
| 28 | `modify_time` | datetime | 修改时间 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_rtd_cap_activity_record_user_line` | `id` → `prize_row_id` | 中奖记录（哪个奖品行被命中了） |
| `t_rtd_cap_participate_log` | `activity_id` | 扫码参与（同一活动下的参与记录） |

## 使用注意点

- **配置表**：一张活动对应多行奖品行，每行是一种奖品配置（不同概率、不同发放方式等）
- **`is_expand`** 是行级权威字段：`1` 表示该奖品支持膨胀（用户可翻倍），膨胀相关逻辑以此为准
- **`default_prize`** = 兜底奖品：用户未中奖时给这个，**全活动最多一行**，且必须允许重复、不限数量、不限概率
- **概率计算**：`probability` 是百分数，`50`=50%，最多6位小数（如 `0.000001`）
- **限购逻辑**：`unit_limit_type` + `unit_limit_hour_type` 组合限制——如 `unit_limit_type=1`（每天全用户合计上限）+ `unit_limit_num=1000` = 每天最多发1000份
- **新客必中**：`new_guest_win_priority` 值越小越优先命中，用于拉新活动的首单必中
- **`won_qty` 是系统回写**：实时更新，可用于判断奖品是否已发完
- **发放模式链路**：
  - `DIRECT` → 直接发券到用户账户
  - `PRIVATE_DOMAIN` → 需用户加企微好友，扫码后发（有 `private_domain_channel_qr_code_url`）
  - `REPURCHASE` → 复购触发（用户购买后发放）

关联：[[t_rtd_cap_participate_log]] · [[t_rtd_cap_activity_record_user_line]] · [[数据字典索引]]
