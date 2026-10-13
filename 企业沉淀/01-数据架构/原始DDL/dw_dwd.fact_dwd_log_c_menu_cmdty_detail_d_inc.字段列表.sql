rowkey, -- 主键
event_time, -- 时间时间 时间戳
server_time_form, -- 数据上报时间
server_time, -- 上报时间戳
app_version, -- 版本
carrier, -- 运营商
longitude, -- 经度
latitude, -- 纬度
system_language, -- 系统语言
os_type, -- 硬件操作系统类别
manufacturer, -- 手机生产厂商
open_id, -- 微信授权id
event_type, -- 事件类别
model, -- 设备型号
union_id, -- 微信小程序唯一id
login_id, -- 登录id（可能是手机号、邮箱、员工号等）
app_name, -- 应用名
country, -- 国家
country_id, -- 国家ID
province, -- 省份
province_id, -- 省份ID
city, -- 城市
city_id, -- 城市ID
platform, -- 平台 1ios 2安卓 3小程序 5支付宝小程序 6抖音小程序
event_code, -- 事件code
session_id, -- 会话id
user_id, -- 用户id
current_page_code, -- 页面code
event_time_form, -- 事件时间 yyyy-MM-dd
distinct_id, -- 设备id
prop_abtest, -- ab测试信息
prop_dept_id, -- 门店部门id
prop_shop_name, -- 门店部门名称
prop_supporttakeout, -- 取餐方式
prop_referer, -- 前页面页面id
prop_position_code, -- 位置code
prop_position_name, -- 位置名称
prop_first_label_name, -- 一级类目名称
prop_second_label_name, -- 二级类目名称
prop_content_type, -- 内容类型 1商品 2套餐
prop_content_id, -- 内容id
prop_content_value, -- 内容值
prop_location, -- 全局位置
prop_label_location, -- 一级类目内位置
prop_plan_id, -- 方案id
prop_tactic_id, -- 策略id
prop_cmdty_discount_price, -- 划线价(折扣价)
prop_cmdty_price, -- 商品原价
prop_cmdty_final_price, -- 预估到手价
prop_sale_state, -- 售卖状态
prop_ck_type, -- 点击类型 仅限点击事件
prop_data, -- 扩展字段
prop_cmdty_sourcefrom, -- 商品推荐规则 1-人工 2-算法 3-策略规则 0-无数据
region_code, -- 经营地区编码
business_language -- 语言