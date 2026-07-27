---
created: 2026-07-25
tags: [企业, 数据, 字典, 埋点日志, ODS]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-25
---

# ods_log.t_hmonitor_track_event — 埋点事件原始日志（ODS）

**数据库**：`ods_log`

## 表结构（85 字段）

### 基础标识

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `rowkey` | string | 主键 |
| 2 | `track_id` | varchar | 追踪 ID |
| 3 | `upload_id` | varchar | 上传 ID |
| 4 | `collect_id` | varchar | 采集 ID |
| 5 | `lifecycle_id` | varchar | 生命周期 ID |
| 6 | `server_id` | varchar | 服务端 ID |
| 7 | `session_id` | varchar | 会话 ID |

### 用户标识

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 8 | `user_id` | bigint | 用户 ID |
| 9 | `open_id` | varchar | 微信授权 ID |
| 10 | `union_id` | varchar | 微信小程序唯一 ID |
| 11 | `login_id` | varchar | 登录 ID |
| 12 | `distinct_id` | varchar | 设备 ID |
| 13 | `push_id` | varchar | 推送 ID |
| 14 | `token_id` | varchar | Token ID |

### 事件

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 15 | `event_code` | varchar | **事件 code** |
| 16 | `event_type` | varchar | 事件类别 |
| 17 | `event_time` | bigint | 事件时间（时间戳） |
| 18 | `event_time_form` | string | 事件时间（`yyyy-MM-dd` 格式） |
| 19 | `track_type` | varchar | 追踪类型 |
| 20 | `spm` | varchar | SPM 编码（超级位置模型） |
| 21 | `properties` | text | **扩展属性 JSON**（类似 DWD 的 `prop_data`） |

### 设备 & 系统

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 22 | `app_version` | varchar | 应用版本 |
| 23 | `app_buildversion` | varchar | 应用构建版本 |
| 24 | `app_name` | varchar | 应用名 |
| 25 | `app_key` | varchar | 应用 Key |
| 26 | `sdk_type` | varchar | SDK 类型 |
| 27 | `sdk_version` | varchar | SDK 版本 |
| 28 | `core_version` | varchar | 核心版本 |
| 29 | `os_type` | varchar | 操作系统类型 |
| 30 | `os_version` | varchar | 操作系统版本 |
| 31 | `model` | varchar | 设备型号 |
| 32 | `manufacturer` | varchar | 手机生产厂商 |
| 33 | `device_name` | varchar | 设备名称 |
| 34 | `browser` | varchar | 浏览器 |
| 35 | `browser_version` | varchar | 浏览器版本 |
| 36 | `browser_core` | varchar | 浏览器内核 |
| 37 | `user_agent` | varchar | User-Agent |
| 38 | `system_language` | varchar | 系统语言 |
| 39 | `network_type` | varchar | 网络类型 |
| 40 | `carrier` | varchar | 运营商 |
| 41 | `screen_width` | int | 屏幕宽度 |
| 42 | `screen_height` | int | 屏幕高度 |
| 43 | `wx_version` | varchar | 微信版本 |
| 44 | `wx_sdk_version` | varchar | 微信 SDK 版本 |

### 位置 & 网络

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 45 | `country` | varchar | 国家 |
| 46 | `country_id` | varchar | 国家 ID |
| 47 | `province` | varchar | 省份 |
| 48 | `province_id` | varchar | 省份 ID |
| 49 | `city` | varchar | 城市 |
| 50 | `city_id` | varchar | 城市 ID |
| 51 | `region_code` | varchar | 经营地区编码 |
| 52 | `longitude` | decimal | 经度 |
| 53 | `latitude` | decimal | 纬度 |
| 54 | `ip` | varchar | IP 地址 |
| 55 | `server_ip` | varchar | 服务器 IP |
| 56 | `inner_ip` | varchar | 内网 IP |
| 57 | `bssid` | varchar | 基站 BSSID |
| 58 | `ssid` | varchar | WiFi SSID |
| 59 | `mac` | varchar | MAC 地址 |
| 60 | `mcc` | varchar | MCC（移动国家码） |
| 61 | `mnc` | varchar | MNC（移动网络码） |

### 设备安全 & 传感器

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 62 | `is_root` | tinyint | 是否 root：`0`=否, `1`=是 |
| 63 | `is_hook` | tinyint | 是否被 hook：`0`=否, `1`=是 |
| 64 | `is_simulator` | tinyint | 是否模拟器：`0`=否, `1`=是 |
| 65 | `imei` | varchar | IMEI 设备标识 |
| 66 | `android_id` | varchar | Android ID |
| 67 | `idfa` | varchar | IDFA（iOS 广告标识符） |
| 68 | `idfv` | varchar | IDFV（iOS 供应商标识符） |
| 69 | `app_sign` | varchar | 应用签名 |
| 70 | `accelerometer_x` | decimal | 加速度计 X |
| 71 | `accelerometer_y` | decimal | 加速度计 Y |
| 72 | `accelerometer_z` | decimal | 加速度计 Z |
| 73 | `gyro_x` | decimal | 陀螺仪 X |
| 74 | `gyro_y` | decimal | 陀螺仪 Y |
| 75 | `gyro_z` | decimal | 陀螺仪 Z |

### 页面

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 76 | `current_page_code` | varchar | 页面 code |
| 77 | `current_page_title` | varchar | 页面标题 |
| 78 | `channel` | varchar | 渠道 |

### 时间 & ETL

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 79 | `server_time` | bigint | 服务端时间戳 |
| 80 | `server_time_form` | datetime | 服务端时间 |
| 81 | `kafka_receive_time` | bigint | Kafka 接收时间 |
| 82 | `dw_create_time` | datetime | 数据加载时间 |
| 83 | `dw_program` | varchar | ETL 程序名称 |
| 84 | `hour` | string | 小时分区 |
| 85 | `dt` | string | **日期分区字段** |
| 86 | `business_language` | varchar | 语言 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `fact_dwd_log_c_luckinpop_detail_d_inc` | `event_code`, `user_id` | 电商分析 DWD（同源数据，ODS→DWD 加工关系） |
| `fact_dwd_log_c_start_retention_detail_d_inc` | `event_code`, `user_id` | 启动留存分析 DWD（同源数据，ODS→DWD 加工关系） |

## 使用注意点

- **ODS 层原始埋点日志**：这是最原始的埋点数据，比 DWD 层更详尽但未清洗
- **字段超级多（85+）**：包含大量设备信息（传感器、网络、位置、安全检测），分析时按需取字段，不要 `SELECT *`
- **`properties` 是 JSON 扩展字段**：类似 DWD 的 `prop_data`，自定义事件参数在这里
- **`dt` 是日期分区**：必须过滤（如 `dt = '2026-07-25'`），否则全表扫描
- **和 DWD 的区别**：
  - ODS 这张表：原始全量，含设备指纹、传感器、安全检测等原始信息
  - DWD `fact_dwd_log_c_*`：清洗后按业务域拆分的标准化事件
  - 如果 DWD 的字段不够用，可以回 ODS 找
- **`spm` 字段**：SPM（Super Position Model）编码，用于追踪页面位置和模块
- **设备安全字段**：`is_root`/`is_hook`/`is_simulator` 用于反作弊和风控
- **渠道字段在 `channel` 而非 `prop_query_source`**：注意和 `fact_dwd_log_c_start_retention_detail_d_inc` 的渠道字段名不同

## 数据流

```
ods_log.t_hmonitor_track_event (ODS, 原始全量)
     ↓ 清洗、标准化、按业务域拆分
dw_dwd.fact_dwd_log_c_luckinpop_detail_d_inc        (电商交易链路)
dw_dwd.fact_dwd_log_c_start_retention_detail_d_inc  (启动留存)
```

关联：[[fact_dwd_log_c_luckinpop_detail_d_inc]] · [[fact_dwd_log_c_start_retention_detail_d_inc]] · [[数据字典索引]]
