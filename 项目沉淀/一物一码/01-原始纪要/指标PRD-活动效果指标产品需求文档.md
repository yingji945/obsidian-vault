---
created: 2026-07-28
tags: [一物一码, PRD, 数据, 指标]
source: 飞书文档（QD0xw9lhdiMNRvkdpImcxAa1nub）
---

# 即享-瓶内营销码活动效果指标产品需求文档（PRD）

> 原始文档：45,495字
> 本文为完整原文入库，供数据视角引用

即享-瓶内营销码活动效果指标产品需求文档
版本变更记录


版本

日期

变更内容

V1.1

2026-07-21

按三份已验收SQL重构明细层：新增曝光会员10分钟轻明细、参与中奖履约明细、实际加C会员10分钟轻明细；应用层收敛为活动效果与奖励履约2张；修正hit_result枚举及参与、中奖、实际加C口径。

V1.0

2026-07-15

初版
 
0、看板示意图


瓶内码活动效果看板高保真原型V6.html
1.1 背景与目标
本方案用于建设瓶内营销码活动效果指标，服务业务运营、数据开发、BI开发和验收人员。本期将活动流量与奖品路径分层：曝光、参与和活动中奖在活动层统计，奖品分析从中奖记录开始，并沿基础奖品、获得方式、实际膨胀选项和奖励履约展开。
商品售卖数据与瓶内码活动数据不存在直接归因关系，因此采用独立数据链路展示，不将售卖量关联到具体activity_no。
1.2 本期范围
包含23项P0指标：售卖3项、活动流量与转化7项、奖品路径9项、奖励发放4项。
商品范围：订单商品表中 level2_category = 'RTD'。
活动范围：通过 t_rtd_cap_activity.activity_no 识别具体瓶内码活动。
统计周期：各业务链路使用自身业务时间字段，统一切分至10分钟时间分片。
交付范围：3类明细模型（曝光会员10分钟轻明细、参与中奖履约明细、实际加C会员10分钟轻明细）和2张实时应用层表（活动效果、奖励履约）；售卖指标直接复用现有交易汇总表。
1.3 不在本期范围
订单复购、商品售卖趋势归因、核销、券费用及其他成本指标。
新老用户、拉新率及其他用户生命周期指标。
物理应用表命名、字段字典及ETL实现设计。
1.4 方案原则


原则

方案说明

售卖独立

售卖量按RTD订单商品统计，与activity_no不做关联。

活动流量独立

曝光、参与、活动中奖只在活动层统计，不向奖品层归因。

活动参与

participate_log.hit_result IN (2,3)均计参与；参与人数按member_id去重。

双中奖口径

活动级中奖取participate_log.hit_result=3；奖品级中奖直接按record_user_line统计。

实际中奖率

中奖率=活动中奖人数÷活动参与人数，按实际值展示，不设置100%预期。

基础奖品

activity_prize.id=record_user_line.prize_row_id，基础券类型和获得方式取奖品配置表。

实际膨胀

record_user_line.expand_option_id=expand_option.id，并校验双方prize_row_id一致。

两层获得方式

基础取prize_grant_mode，膨胀取prize_expand_mode；DIRECT/PRIVATE_DOMAIN/REPURCHASE统一映射。

自然时间

各指标使用自身业务发生时间并归属dt和time_slice_10min。

不可直接加总

活动总量不得由奖品路径行求和；人数跨奖品、跨路径必须重新去重。
 
2. 数据源概览
2.1 表清单


源表

中文说明

关键字段

本期用途

状态

dw_drs_ads.ads_inst_shop_sku_order_summary_10min_d_inc_uniq

即享SKU粒度订单商品汇总


dt、level2_category、channel_l1~l4、spec_num

RTD售卖量

已确认

ods_log.t_hmonitor_track_event

用户行为埋点事件日志

event_code、properties、user_id、event_time

活动级曝光

已确认

lucky_epromotion.t_rtd_cap_activity

RTD瓶盖活动主表

id、activity_no、activity_name

活动主数据

已确认

lucky_epromotion.t_rtd_cap_participate_log

RTD扫码参与流水

id、member_id、activity_id、hit_result、create_time

活动参与与活动中奖

已确认

lucky_epromotion.t_rtd_cap_activity_record_user_line

RTD活动用户中奖记录

activity_record_no、member_id、prize_row_id、expand_option_id、fulfillment_phase

奖品级中奖与路径事实

已确认

lucky_epromotion.t_rtd_cap_activity_prize

RTD活动奖品配置

id、content_type、is_expand、prize_grant_mode

基础奖品维度

已确认

lucky_epromotion.t_rtd_cap_activity_prize_expand_option

RTD活动奖品膨胀选项

id、prize_row_id、expand_target_type、expand_prize_name、prize_expand_mode

实际膨胀与膨胀奖品维度

已确认

lucky_epromotion.t_rtd_cap_activity_record_user_line_grant_item

RTD奖励发放明细

activity_record_no、member_id、content_type、coupon_no

奖励发放

已确认

lucky_epromotion.t_rtd_redpack_user_instance

RTD用户现金红包实例

activity_record_no、prize_row_id、redpack_denomination、transfer_done_time

现金红包费用

已确认

lucky_wecom.t_wecom_external_user_history

企业微信外部联系人历史

id、member_id、state、event_time

PRIVATE_DOMAIN路径加C结果

已确认
 
2.2 不同业务场景的数据来源说明


场景

源表

取数字段

时间字段

处理说明

活动曝光

ods_log.t_hmonitor_track_event

properties.activity_no、user_id、event_code

event_time

仅活动层；event_code='lottery_main_page_bw'。

活动参与

t_rtd_cap_participate_log


id、member_id、activity_id、hit_result

create_time

hit_result IN (2,3)；layer_break_code本期不处理。

活动中奖

t_rtd_cap_participate_log

id、member_id、activity_id、hit_result

create_time

hit_result=3；不使用record_user_line计算活动总量。

奖品中奖

t_rtd_cap_activity_record_user_line

activity_record_no、member_id、prize_row_id

create_time

奖品层从中奖记录开始，直接按中奖记录统计。

基础奖品路径

activity_prize + record_user_line

content_type、prize_grant_mode、is_expand

user_line.create_time/claim_time

is_expand表示配置支持能力。

实际膨胀路径

record_user_line + activity_prize_expand_option

expand_option_id、expand_target_type、expand_prize_name、prize_expand_mode

claim_time

expand_option_id=id且prize_row_id一致。

加C

中奖路径 + t_wecom_external_user_history

member_id、state、effective_grant_mode

event_time

仅最终获得方式PRIVATE_DOMAIN路径；state取业务确认3个值。

复购第二瓶

t_rtd_cap_activity_record_user_line

member_id、activity_record_no、fulfillment_phase、effective_grant_mode

modify_time

最终获得方式REPURCHASE且FULFILLED。

奖励发放

record_user_line + grant_item

activity_record_no、member_id、grant_item.id

中奖记录create_time

发放结果回写至中奖记录归属分片。

现金红包费用

t_rtd_redpack_user_instance

activity_record_no、redpack_denomination

transfer_done_time

按转账完成时间统计金额，路径维度由中奖记录补齐。
 
2.3 核心关联关系


链路

关联关系

输出

曝光

properties.activity_no直接识别活动

activity_no × user_id

参与/活动中奖

participate_log.activity_id=activity.id；0/1参与，1中奖

activity_no × member_id × participate_log.id

基础奖品

activity_prize.id=record_user_line.prize_row_id

activity_no × prize_id × activity_record_no

实际膨胀

record_user_line.expand_option_id=expand_option.id，且双方prize_row_id一致

prize_id × is_expanded × expand_option_id

最终获得方式

is_expanded=1取prize_expand_mode，否则取prize_grant_mode

DIRECT/PRIVATE_DOMAIN/REPURCHASE

首次路径

record_user_line.first_scan_id=participate_log.scan_id，且participate_phase=1

首次膨胀/首次直接领取

加C

PRIVATE_DOMAIN路径会员集合按activity_no+路径+member_id去重后关联wecom_history.member_id

奖品路径 × 加C事件

奖励发放

record_user_line.activity_record_no=grant_item.activity_record_no

中奖路径 × 发放明细

红包费用

redpack.activity_record_no=record_user_line.activity_record_no

中奖路径 × 红包金额
 
3. 维度体系与统计设计
本需求不新增独立维度或主数据表，统一取用当前即享基础维度。
3.1 核心维度


维度

字段

来源

维护方式

说明

自然时间

dt、time_slice_10min

各业务源表时间字段

沿用现有维护机制

各链路按自身业务时间归属。

活动

activity_no、activity_name

t_rtd_cap_activity

沿用活动主表

曝光、参与和活动中奖最高拆到活动。

基础奖品

prize_id、prize_name、prize_type、base_content_type

t_rtd_cap_activity_prize

沿用奖品配置

奖品分析从中奖记录开始。

基础获得方式

base_grant_mode

t_rtd_cap_activity_prize.prize_grant_mode

枚举映射


DIRECT/PRIVATE_DOMAIN/REPURCHASE。

膨胀配置能力

is_expand_supported

t_rtd_cap_activity_prize.is_expand

沿用奖品配置

不等于用户实际膨胀。

实际膨胀

is_expanded、expand_option_id

record_user_line.expand_option_id + expand_option.id

按中奖记录

成功关联为1，未关联异常保留。

膨胀奖品

expand_prize_name、expand_target_type、expand_proposal_no

t_rtd_cap_activity_prize_expand_option

沿用膨胀选项

expand_target_type为膨胀券类型。

膨胀获得方式

expand_grant_mode

expand_option.prize_expand_mode

枚举映射

DIRECT/PRIVATE_DOMAIN/REPURCHASE。

最终获得方式

effective_grant_mode

基础与膨胀获得方式派生

应用层派生

实际膨胀取膨胀方式，否则取基础方式。

会员

member_id

RTD、埋点和企微表

仅用于关联与去重

user_id=member_id仅用于活动曝光参与同人。
 
3.2 指标分组


分组

指标数量

指标清单

商品售卖

3

全渠道售卖量（线上+线下）、全渠道售卖量（线上）、全渠道售卖量（线下）

活动流量与转化

7

活动曝光人数、活动参与人数、活动人均参与次数、活动参与率、中奖人数、中奖次数、中奖率

奖品路径

9

实际加C人数、实际加C人次、加C领取路径履约率、复购第二瓶人数、复购第二瓶次数、奖品膨胀人数、直接选择人数、首次奖品膨胀人数、首次直接选择人数

奖励发放

4

现金红包费用、奖品发放人数、奖品发放次数、奖品发放率
 
4. 指标定义与技术取数口径
4.1 全渠道售卖量（线上+线下）


名称

全渠道售卖量（线上+线下）

业务定义

统计周期内，RTD二级品类在线上和线下渠道产生的订单商品数量。

计算公式

全渠道售卖量（线上+线下） = SUM(spec_num)，范围为线上渠道 ∪ 线下渠道。

数据来源

dw_drs_ads.ads_inst_shop_sku_order_summary_10min_d_inc_uniq

时间口径

按dt归属dt，并按time_slice_10min切分。

统计粒度

dt × time_slice_10min × 渠道 × SKU；展示时可汇总为全渠道。

过滤条件与口径边界

level2_category='RTD'；线上线下沿用现有渠道分类；不关联activity_no。

去重与聚合

数量字段spec_num直接求和。

异常阈值

指标值不得小于0；关键关联字段空值率超过5%时告警，不静默丢弃。
 
4.2 全渠道售卖量（线上）


名称

全渠道售卖量（线上）

业务定义

统计周期内，RTD二级品类在线上渠道产生的订单商品数量。

计算公式

全渠道售卖量（线上） = SUM(spec_num)，范围为线上渠道。

数据来源

dw_drs_ads.ads_inst_shop_sku_order_summary_10min_d_inc_uniq

时间口径

按dt归属dt，并按time_slice_10min切分。

统计粒度

dt × time_slice_10min × 线上渠道 × SKU。

过滤条件与口径边界

level2_category='RTD'；渠道限定为现有线上分类；不关联activity_no。

去重与聚合

数量字段spec_num直接求和。

异常阈值

指标值不得小于0；关键关联字段空值率超过5%时告警，不静默丢弃。
 
4.3 全渠道售卖量（线下）


名称

全渠道售卖量（线下）

业务定义

统计周期内，RTD二级品类在线下渠道产生的订单商品数量。

计算公式

全渠道售卖量（线下） = SUM(spec_num)，范围为线下渠道。

数据来源

dw_drs_ads.ads_inst_shop_sku_order_summary_10min_d_inc_uniq

时间口径

按dt归属dt，并按time_slice_10min切分。

统计粒度

dt × time_slice_10min × 线下渠道 × SKU。

过滤条件与口径边界

level2_category='RTD'；渠道限定为现有线下分类；不关联activity_no。

去重与聚合

数量字段spec_num直接求和。

异常阈值

指标值不得小于0；关键关联字段空值率超过5%时告警，不静默丢弃。
 
4.4 活动曝光人数


名称

活动曝光人数

业务定义

统计周期内，进入指定瓶内码活动主页面的去重会员数。

计算公式

活动曝光人数=COUNT(DISTINCT user_id)。

数据来源

ods_log.t_hmonitor_track_event。

时间口径

按event_time归属dt和time_slice_10min。

统计粒度

dt × time_slice_10min × activity_no，仅活动层。

过滤条件与口径边界

event_code='lottery_main_page_bw'；properties.activity_no识别活动；不得归因到prize_id或expand_option_id。

去重与聚合

活动内按user_id去重；多日按查询范围内activity_no+user_id重新去重。

异常阈值

指标非负；user_id空值率超过5%告警。
 
4.5 活动参与人数


名称

活动参与人数

业务定义

统计周期内，指定活动产生参与流水的去重会员数。

计算公式

活动参与人数=COUNT(DISTINCT member_id)，其中hit_result IN (2,3)。

数据来源

lucky_epromotion.t_rtd_cap_participate_log + t_rtd_cap_activity。

时间口径

按participate_log.create_time归属dt和time_slice_10min。

统计粒度

dt × time_slice_10min × activity_no，仅活动层。

过滤条件与口径边界

hit_result IN (2,3)；layer_break_code本期不处理；不提供奖品级参与。

去重与聚合

活动内按member_id去重；多日按查询范围重新去重。

异常阈值

指标非负；member_id或hit_result空值率超过5%告警。
 
4.6 活动人均参与次数


名称

活动人均参与次数

业务定义

统计周期内，指定活动每位参与会员平均产生的参与流水次数。

计算公式

活动人均参与次数=COUNT(participate_log.id) ÷ COUNT(DISTINCT member_id)，其中hit_result IN (2,3)。

数据来源

lucky_epromotion.t_rtd_cap_participate_log。

时间口径

按participate_log.create_time归属。

统计粒度

dt × time_slice_10min × activity_no，仅活动层。

过滤条件与口径边界

hit_result IN (2,3)；分母为0显示“—”；不提供奖品级指标。

去重与聚合

分子计参与流水id，分母按member_id去重。

异常阈值

指标非负；分母为0不计算。
 
4.7 活动参与率


名称

活动参与率

业务定义

统计周期内，曝光后又参与的同人用户占曝光用户比例。

计算公式

活动参与率=COUNT(DISTINCT 曝光且参与的用户) ÷ COUNT(DISTINCT 曝光用户)。

数据来源

t_hmonitor_track_event + t_rtd_cap_participate_log。

时间口径

曝光按event_time、参与按create_time，在查询范围内计算。

统计粒度

activity_no，仅活动层。

过滤条件与口径边界

track_event.user_id=participate_log.member_id；参与限定hit_result IN (2,3)；分母为0显示“—”。

去重与聚合

分子、分母均从明细按查询范围重新去重。

异常阈值

结果0%~100%；分母为0显示“—”。
 
4.8 中奖人数


名称

中奖人数

业务定义

统计周期内，指定活动hit_result=3的去重参与会员数。

计算公式

中奖人数=COUNT(DISTINCT member_id)，其中hit_result=3。

数据来源

lucky_epromotion.t_rtd_cap_participate_log。

时间口径

按participate_log.create_time归属。

统计粒度

dt × time_slice_10min × activity_no；奖品级中奖另按user_line统计。

过滤条件与口径边界

hit_result=3为活动级唯一权威条件；不使用record_prize_status过滤。

去重与聚合

活动内按member_id去重；多日按查询范围重新去重。

异常阈值

指标非负；hit_result空值率超过5%告警。
 
4.9 中奖次数


名称

中奖次数

业务定义

统计周期内，指定活动hit_result=3的参与流水数。

计算公式

中奖次数=COUNT(participate_log.id)，其中hit_result=3。

数据来源

lucky_epromotion.t_rtd_cap_participate_log。

时间口径

按participate_log.create_time归属。

统计粒度

dt × time_slice_10min × activity_no；奖品级中奖次数另按activity_record_no统计。

过滤条件与口径边界

hit_result=3；不使用record_user_line计算活动级中奖次数。

去重与聚合

按唯一participate_log.id计数。

异常阈值

指标非负；参与流水主键重复率必须为0。
 
4.10 中奖率


名称

中奖率

业务定义

统计周期内，指定活动中奖会员占参与会员的比例。

计算公式

中奖率=中奖人数 ÷ 活动参与人数。

数据来源

lucky_epromotion.t_rtd_cap_participate_log。

时间口径

分子、分母均按participate_log.create_time归属。

统计粒度

activity_no，仅活动层。

过滤条件与口径边界

分子hit_result=3；分母hit_result IN (2,3)；分母为0显示“—”。

去重与聚合

查询范围内分别去重后计算，不累加分片比率。

异常阈值

结果0%~100%；不设置100%预期。
 
4.11 实际加C人数


口径要素

定义

名称

实际加C人数

业务定义

统计周期内，通过指定瓶内码渠道state产生真实企微加好友事件的去重会员数。

计算公式

实际加C人数=COUNT(DISTINCT member_id)。

数据来源

瓶内码实际加C会员10分钟轻明细模型（SQL 3），源自企微外部联系人历史表。

时间口径

按企微event_time归属日期和10分钟时间片；event_time为13位毫秒时间戳。

统计粒度

日期 × 10分钟 × state；查询周期按member_id重新去重。

过滤条件与口径边界

event_type='add_external_contact'且state属于已确认的3类瓶内码渠道。state不是活动ID，暂不归因具体活动。

去重与聚合

按member_id去重；不得累加每日或10分钟人数。

异常阈值

指标非负；member_id空值率超过5%告警；外部联系人关联状态异常需保留。
 
4.12 实际加C人次


口径要素

定义

名称

实际加C人次

业务定义

统计周期内，通过指定瓶内码渠道state产生的真实企微加好友事件数。

计算公式

实际加C人次=SUM(add_c_event_cnt)，底层按企微历史事件ID去重。

数据来源

瓶内码实际加C会员10分钟轻明细模型（SQL 3），源自企微外部联系人历史表。

时间口径

按企微event_time归属日期和10分钟时间片；event_time为13位毫秒时间戳。

统计粒度

日期 × 10分钟 × state。

过滤条件与口径边界

event_type='add_external_contact'且state属于已确认的3类瓶内码渠道。暂不关联具体活动和中奖记录。

去重与聚合

底层按企微历史事件ID去重；分片事件数可以相加。

异常阈值

指标非负；事件ID重复率必须为0。
 
4.13 加C领取路径履约率


口径要素

定义

名称

加C领取路径履约率

业务定义

统计周期内，PRIVATE_DOMAIN领取路径中已完成业务履约的会员占该路径中奖会员的比例。

计算公式

加C领取路径履约率=PRIVATE_DOMAIN且fulfillment_phase='FULFILLED'的去重会员数 ÷ PRIVATE_DOMAIN路径中奖去重会员数。

数据来源

瓶内码活动参与中奖履约明细模型（SQL 2）。

时间口径

按参与时间归属；履约状态允许延迟更新。

统计粒度

活动 × 基础奖品 × 是否膨胀 × 膨胀选项 × 最终获得方式。

过滤条件与口径边界

分母为hit_result=3且effective_grant_mode='PRIVATE_DOMAIN'；分子追加fulfillment_phase='FULFILLED'。该指标不代表真实企微加好友转化率。

去重与聚合

分子、分母均按member_id在查询范围重新去重；跨路径会员数不可直接相加。

异常阈值

范围0至100%；分母为0显示“—”；分子不得大于分母。
 
4.14 复购第二瓶人数


名称

复购第二瓶人数

业务定义

统计周期内，最终获得方式为复购第二瓶且已履约的去重会员数。

计算公式

复购第二瓶人数=COUNT(DISTINCT member_id)，其中effective_grant_mode='REPURCHASE'且fulfillment_phase='FULFILLED'。

数据来源

record_user_line + activity_prize + expand_option。

时间口径

按record_user_line.modify_time归属。

统计粒度

activity_no × prize_id × is_expanded × expand_option_id。

过滤条件与口径边界

实际膨胀取prize_expand_mode，否则取prize_grant_mode；不表示订单复购。

去重与聚合

按路径和member_id去重；跨路径重新去重。

异常阈值

指标非负；关键字段空值率超过5%告警。
 
4.15 复购第二瓶次数


名称

复购第二瓶次数

业务定义

统计周期内，最终获得方式为复购第二瓶且已履约的中奖记录数。

计算公式

复购第二瓶次数=COUNT(DISTINCT activity_record_no)，过滤条件同人数。

数据来源

record_user_line + activity_prize + expand_option。

时间口径

按record_user_line.modify_time归属。

统计粒度

activity_no × prize_id × is_expanded × expand_option_id。

过滤条件与口径边界

effective_grant_mode='REPURCHASE'且fulfillment_phase='FULFILLED'。

去重与聚合

按activity_record_no去重；每条中奖记录只归属一个最终路径。

异常阈值

指标非负；activity_record_no重复归属率必须为0。
 
4.16 奖品膨胀人数


名称

奖品膨胀人数

业务定义

统计周期内，中奖记录实际关联到膨胀选项的去重会员数。

计算公式

奖品膨胀人数=COUNT(DISTINCT member_id)，其中expand_option_id成功关联expand_option.id。

数据来源

record_user_line + t_rtd_cap_activity_prize_expand_option。

时间口径

按record_user_line.claim_time归属。

统计粒度

activity_no × prize_id × expand_option_id。

过滤条件与口径边界

同时校验双方prize_row_id一致；activity_prize.is_expand只表示配置能力。

去重与聚合

按路径和member_id去重；跨路径重新去重。

异常阈值

指标非负；非空expand_option_id关联失败率必须为0。
 
4.17 直接选择人数


名称

直接选择人数

业务定义

统计周期内，最终获得方式为直接领取的去重会员数。

计算公式

直接选择人数=COUNT(DISTINCT member_id)，其中effective_grant_mode='DIRECT'。

数据来源

record_user_line + activity_prize + expand_option。

时间口径

按record_user_line.claim_time归属。

统计粒度

activity_no × prize_id × is_expanded × expand_option_id。

过滤条件与口径边界

实际膨胀时取prize_expand_mode，未膨胀时取prize_grant_mode。

去重与聚合

按路径和member_id去重；跨路径重新去重。

异常阈值

指标非负；最终获得方式空值率超过5%告警。
 
4.18 首次奖品膨胀人数


名称

首次奖品膨胀人数

业务定义

统计周期内，首次扫码中奖后实际关联膨胀选项的去重会员数。

计算公式

首次奖品膨胀人数=COUNT(DISTINCT user_line.member_id)，其中is_expanded=1且participate_phase=1。

数据来源

record_user_line + expand_option + participate_log。

时间口径

按record_user_line.claim_time归属。

统计粒度

activity_no × prize_id × expand_option_id。

过滤条件与口径边界

first_scan_id=scan_id；participate_phase=1；expand_option_id成功关联。

去重与聚合

按路径和member_id去重。

异常阈值

指标非负；首次扫码关联失败率需监控。
 
4.19 首次直接选择人数


名称

首次直接选择人数

业务定义

统计周期内，首次扫码中奖后最终获得方式为直接领取的去重会员数。

计算公式

首次直接选择人数=COUNT(DISTINCT user_line.member_id)，其中effective_grant_mode='DIRECT'且participate_phase=1。

数据来源

record_user_line + activity_prize + expand_option + participate_log。

时间口径

按record_user_line.claim_time归属。

统计粒度

activity_no × prize_id × is_expanded × expand_option_id。

过滤条件与口径边界

first_scan_id=scan_id；participate_phase=1；最终获得方式为DIRECT。

去重与聚合

按路径和member_id去重。

异常阈值

指标非负；首次扫码关联失败率需监控。
 
4.20 现金红包费用


名称

现金红包费用

业务定义

统计周期内，指定中奖路径完成转账的现金红包面额合计。

计算公式

现金红包费用=SUM(redpack_denomination)。

数据来源

t_rtd_redpack_user_instance + record_user_line。

时间口径

按transfer_done_time归属。

统计粒度

activity_no × prize_id × is_expanded × expand_option_id。

过滤条件与口径边界

transfer_done_time非空；通过activity_record_no补齐路径；金额不得为负。

去重与聚合

红包实例粒度求和，单位元。

异常阈值

金额非负；明细与汇总差异为0。
 
4.21 奖品发放人数


名称

奖品发放人数

业务定义

统计周期内，中奖记录已关联至少一条发放明细的去重会员数。

计算公式

奖品发放人数=COUNT(DISTINCT user_line.member_id)，其中存在grant_item。

数据来源

record_user_line + record_user_line_grant_item。

时间口径

按record_user_line.create_time归属中奖分片。

统计粒度

activity_no × prize_id × is_expanded × expand_option_id。

过滤条件与口径边界

activity_record_no关联；发放明细落表即成功。

去重与聚合

按路径和member_id去重；跨路径重新去重。

异常阈值

指标非负；关联键空值率超过5%告警。
 
4.22 奖品发放次数


名称

奖品发放次数

业务定义

统计周期内，中奖记录关联到的奖品发放明细记录数。

计算公式

奖品发放次数=COUNT(grant_item.id)。

数据来源

record_user_line + record_user_line_grant_item。

时间口径

按record_user_line.create_time归属中奖分片。

统计粒度

activity_no × prize_id × is_expanded × expand_option_id。

过滤条件与口径边界

activity_record_no关联；每条grant_item计1次。

去重与聚合

按grant_item.id计数；中奖记录路径唯一时可加总。

异常阈值

指标非负；grant_item.id重复率必须为0。
 
4.23 奖品发放率
 
5. 明细模型与实时应用层表设计
5.1 设计说明
本期不再建设一张混合粒度的统一事件事实模型，改为建设3类可直接支撑BI聚合的明细模型：活动曝光会员10分钟轻明细、活动参与中奖履约明细、实际加C会员10分钟轻明细。
三类模型分别对应SQL 1、SQL 2、SQL 3的已验证输出粒度。SQL仅作为验证查询和逻辑蓝图；正式数仓建设沿用相同业务粒度、字段口径、时间口径与质量规则。

核心原则：曝光和实际加C数据量较大，按会员与10分钟轻汇总；参与、中奖、奖品路径和奖励履约以一次参与为主行形成宽明细。三类模型均保留member_id，跨日期人数必须从明细重新去重。
应用层保留2张逻辑表：活动效果实时应用层表、奖励履约实时应用层表。奖品和领取路径分析优先从活动参与中奖履约明细聚合，口径稳定且性能不足时再下沉到应用层。
5.2 模型总览


数据对象

对象类型

业务粒度

唯一键

核心来源

核心用途

瓶内码活动曝光会员10分钟轻明细模型

会员轻明细

日期 × 10分钟 × 活动 × 会员

dt + time_slice_10min + activity_no + member_id

活动主页曝光埋点

曝光次数、曝光人数、时段分析

瓶内码活动参与中奖履约明细模型

参与级宽明细

一次活动参与

participate_id

参与流水、中奖记录、奖品配置、膨胀选项、发放明细、红包实例

参与、中奖、奖品、获取方式、膨胀和履约

瓶内码实际加C会员10分钟轻明细模型

会员轻明细

日期 × 10分钟 × state × 会员

dt + time_slice_10min + state + member_id

企微外部联系人历史事件

实际加C人数、事件数、渠道分布

瓶内码活动效果实时应用层表

活动级应用表

日期 × 10分钟 × 活动

dt + time_slice_10min + activity_no

曝光轻明细 + 参与中奖履约明细

活动核心指标和转化漏斗

瓶内码奖励履约实时应用层表

奖品路径应用表

日期 × 10分钟 × 活动 × 奖品路径 × 时间类型

时间分片 + 活动 + 奖品路径 + stat_time_type

参与中奖履约明细

领取路径、发放结果和红包费用
5.3 瓶内码活动曝光会员10分钟轻明细模型（SQL 1）
模型用途：保存活动主页曝光在会员和10分钟粒度下的轻汇总结果。该模型不关联奖品，不将曝光向奖品路径归因。
模型粒度：dt × time_slice_10min × activity_no × member_id。event_time为13位毫秒时间戳，必须先除以1000转换为秒级时间，禁止直接CAST AS TIMESTAMP。


字段英文名

字段中文名

类型

字段角色

口径说明

字段级血缘

dt


统计日期

date

业务维度

曝光发生自然日

event_time毫秒时间戳转换

time_slice_10min

10分钟时间片

string

业务维度

曝光时间向下取整至10分钟

event_time_ms

activity_id

活动ID

bigint

关联键

活动主表主键

properties.activity_no关联活动主表

activity_no


活动编号

string

退化维度

曝光埋点中的活动编号

properties.activity_no

activity_name

活动名称

string

业务维度

活动展示名称

活动主表.activity_name

member_id


会员ID

string

关联键

曝光埋点user_id映射后的会员标识

曝光埋点.user_id

exposure_cnt

曝光次数

bigint

原子指标

唯一曝光事件数

COUNT(DISTINCT rowkey)

first_exposure_time

首次曝光时间

timestamp

业务维度

本时间片首次曝光

MIN(event_time)

last_exposure_time

最后曝光时间

timestamp

业务维度

本时间片最后曝光

MAX(event_time)
5.4 瓶内码活动参与中奖履约明细模型（SQL 2）
模型用途：以一次活动参与为主行，横向补充活动、中奖记录、基础奖品、膨胀选项、最终获得方式、奖励发放和红包转账结果，支持直接回答“一次参与中了什么奖、如何获取、是否膨胀、膨胀奖品是什么、是否履约”。
模型粒度：一行一次活动参与，唯一键为participate_id。参与流水通过activity_id + scan_id关联中奖记录的activity_id + first_scan_id；中奖记录通过prize_row_id关联基础奖品，通过expand_option_id关联膨胀选项，通过activity_record_no关联发放明细和红包实例。
hit_result枚举：0不可参与、1待参与、2未中奖、3已中奖。
完成参与：hit_result IN (2,3)。
活动中奖：hit_result=3。
实际膨胀：expand_option_id成功关联且expand_option.prize_row_id与基础奖品ID一致。
最终获得方式：已膨胀取膨胀获得方式，未膨胀取基础获得方式。
加C领取路径表示业务配置PRIVATE_DOMAIN及其履约状态，不代表企微实际新增联系人。


字段英文名

字段中文名

类型

字段角色

口径说明

字段级血缘

dt / time_slice_10min

日期 / 10分钟时间片

date / string

业务维度

按参与时间归属

参与流水.create_time

participate_id

参与流水ID

bigint

主键

一次活动参与唯一标识

参与流水.id

participate_time

参与时间

timestamp

业务维度

参与业务发生时间

参与流水.create_time

activity_id / activity_no / activity_name

活动ID / 编号 / 名称

组合

业务维度

参与所属活动

参与流水 + 活动主表

member_id

会员ID

string

关联键

参与会员标识

参与流水.member_id

scan_id

扫码ID

string

关联键

参与与中奖记录的关联键

参与流水.scan_id

participate_phase / layer_break_code


参与阶段 / 拦截诊断码

int / string


业务维度

保留原始值，不替代中奖和复购口径

参与流水

hit_result / hit_result_name

参与结果编码 / 名称

int / string

业务维度

0不可参与、1待参与、2未中奖、3已中奖

参与流水.hit_result

is_completed_participate

是否完成参与

int

原子指标

hit_result IN (2,3)为1

hit_result派生

is_win

是否中奖

int

原子指标

hit_result=3为1

hit_result派生

participate_win_join_status / win_match_count


参与中奖关联状态 / 匹配记录数

string / bigint


质量维度

识别缺失、多匹配和异常中奖记录

参与流水关联中奖记录

user_line_id / activity_record_no


中奖记录行ID / 中奖记录编号

bigint / string

关联键

中奖记录及履约主键

中奖记录

win_time / claim_time

中奖记录时间 / 路径确认时间

timestamp

业务维度

中奖与路径确认时间

中奖记录.create_time / claim_time

prize_id / prize_name


基础奖品ID / 名称

bigint / string

奖品维度

中奖时的基础奖品

中奖记录.prize_row_id / prize_name

base_content_type / base_grant_mode


基础奖品内容类型 / 基础获得方式

string

奖品维度

基础奖品配置

基础奖品配置表

prize_grant_mode_snapshot

中奖获得方式快照

string


业务维度

中奖记录保存的获得方式快照

中奖记录.prize_grant_mode

is_expand_supported


是否支持膨胀

int


业务维度

配置能力，不代表实际膨胀

基础奖品.is_expand

expand_option_id / expand_join_status


膨胀选项ID / 关联状态

bigint / string

关联与质量维度

实际膨胀权威关联键及质量状态

中奖记录 + 膨胀选项

is_expanded

是否实际膨胀

int

原子指标

膨胀选项成功关联且奖品一致为1

expand_join_status派生

expand_prize_name / expand_target_type

膨胀奖品名称 / 内容类型

string

奖品维度

实际膨胀后的奖品

膨胀选项

expand_grant_mode

膨胀获得方式

string

业务维度

膨胀路径获得方式

膨胀选项.prize_expand_mode

effective_grant_mode


最终获得方式

string

业务维度

DIRECT / PRIVATE_DOMAIN / REPURCHASE

按is_expanded派生

final_prize_name


最终奖品名称

string

奖品维度

已膨胀取膨胀奖品名称，否则取基础奖品名称

is_expanded + expand_prize_name + prize_name

final_prize_content_type


最终奖品内容类型

string

奖品维度

已膨胀取膨胀内容类型，否则取基础内容类型

is_expanded + expand_target_type + base_content_type

path_display_name

路径展示名称

string

业务维度

是否膨胀与最终获得方式的组合名称

is_expanded + effective_grant_mode

fulfillment_phase

履约阶段

string

业务维度

中奖记录当前履约状态

中奖记录.fulfillment_phase

is_private_domain_path

是否加C领取路径

int

原子指标

中奖且最终获得方式为PRIVATE_DOMAIN

hit_result + effective_grant_mode

is_private_domain_fulfilled

加C路径是否已履约

int

原子指标

PRIVATE_DOMAIN且FULFILLED为1

最终获得方式 + 履约阶段

grant_item_count_snapshot / grant_item_count


中奖记录发放数 / 实际发放数

bigint


质量与原子指标

用于发放明细数量平衡校验

中奖记录 + 发放明细

redpack_grant_count / instant_coupon_grant_count / coffee_coupon_grant_count / coffee_store_coupon_grant_count

各类奖励发放数量

bigint

原子指标

按发放内容类型统计

发放明细.content_type


redpack_instance_count / redpack_transferred_count / redpack_not_transferred_count

红包实例及转账数量

bigint

原子指标

红包实例状态拆分


红包实例

redpack_transferred_amount

红包已转账金额

decimal(18,2)


原子指标

仅统计已转账红包面额

红包实例

fulfillment_fail_code / reason / time / retry_count

履约失败信息

组合

质量维度

保留履约异常，不静默丢弃


中奖记录
5.5 瓶内码实际加C会员10分钟轻明细模型（SQL 3）
模型用途：保存企微历史表中实际发生的加好友事件，支持BI按任意日期范围重新去重实际加C会员人数。该模型与SQL 2中的“加C领取路径”含义不同：SQL 2表示业务领取配置及履约，SQL 3表示真实企微加好友事件。
模型粒度：dt × time_slice_10min × state × member_id。event_time为13位毫秒时间戳，必须先除以1000转换。state表示加C渠道，不是活动ID；活动归因规则未确认前，不关联具体RTD活动。


字段英文名

字段中文名

类型

字段角色

口径说明

字段级血缘

dt

统计日期

date

业务维度

实际加C发生自然日

企微历史.event_time

time_slice_10min

10分钟时间片

string

业务维度

加C时间向下取整至10分钟

event_time_ms

add_c_state

加C渠道原始值

string

业务维度

保留state原始值

企微历史.state

add_c_channel

加C渠道

string

业务维度

即享优惠券 / 现制饮品优惠券 / 现金红包

state映射

member_id

会员ID

string

关联键

支持任意周期重新去重

企微历史.member_id

member_id_status

会员ID状态

string

质量维度

VALID / MISSING_MEMBER

member_id空值判断

event_type

加C事件类型

string

业务维度

固定add_external_contact

企微历史.event_type

add_c_event_cnt

加C事件数

bigint

原子指标

本粒度内唯一事件数

COUNT(DISTINCT id)

external_user_cnt

企微外部联系人数

bigint

质量指标

本粒度内外部联系人ID数

COUNT(DISTINCT external_user_id)

unique_external_user_id

唯一企微外部联系人ID

string

关联键

仅外部联系人ID唯一时输出

企微历史.external_user_id

service_user_cnt / unique_service_user_id

服务人员数 / 唯一服务人员ID

组合


质量与关联维度

识别同一会员同时间片服务人员关系


企微历史.user_id

brand_type_cnt / unique_brand_type

品牌类型数 / 唯一品牌类型

组合

质量与业务维度

品牌映射结果


企微历史.brand_type

first_add_c_time / last_add_c_time

首次 / 最后加C时间

timestamp

业务维度

本时间片首末加C时间

MIN / MAX(event_time)

external_user_join_status

企微外部联系人关联状态

string


质量维度

MISSING_EXTERNAL_USER / UNIQUE / MULTIPLE_EXTERNAL_USER


external_user_id数量派生
5.6 三类明细的关联与使用边界


关系

关联字段

支持的分析

边界

曝光轻明细 → 参与中奖履约明细

activity_id或activity_no + member_id + 查询时间范围

曝光人数、曝光后参与人数、活动参与率

用于集合交集和聚合，不强制逐条曝光匹配某次参与

参与流水 → 中奖记录

activity_id + scan_id = activity_id + first_scan_id

一次参与对应的中奖、奖品和领取路径

多匹配或缺失必须输出质量状态

中奖记录 → 发放与红包

activity_record_no

发放数量、券种、红包转账和费用

发放允许延迟，当前明细反映最新履约状态

参与中奖履约明细 ↔ 实际加C轻明细

当前只共享member_id和时间

可独立对比总量

缺少活动归因窗口和多次中奖规则，禁止直接计算活动级实际加C转化率
SQL 2中的is_private_domain_path和is_private_domain_fulfilled只能统计“加C领取路径中奖/履约”；SQL 3中的实际加C人数和事件数才代表真实企微加好友。两者不得混用。
5.7 瓶内码活动效果实时应用层表
表用途：从SQL 1曝光会员轻明细和SQL 2参与中奖履约明细生成活动级准确总量。表粒度为dt × time_slice_10min × activity_no；多日人数必须回到明细按activity_no + member_id重新去重，不能累加分片UV。


字段英文名

字段中文名

类型

口径说明

dt / time_slice_10min

日期 / 10分钟时间片

date / string

活动行为时间分片

activity_no / activity_name

活动编号 / 名称

string

活动维度

exposure_cnt / exposure_uv

曝光次数 / 人数

bigint

SQL 1曝光次数求和、会员去重

participate_cnt / participate_uv

完成参与次数 / 人数

bigint

SQL 2中hit_result IN (2,3)

exposure_participate_uv

曝光且参与人数

bigint

查询范围内两类明细member_id交集

participate_rate

活动参与率

decimal(10,4)

曝光且参与人数 ÷ 曝光人数

win_cnt / win_uv

中奖次数 / 人数

bigint

SQL 2中hit_result=3

win_rate

中奖率

decimal(10,4)

中奖人数 ÷ 完成参与人数

private_domain_path_win_cnt / uv

加C领取路径中奖次数 / 人数

bigint

SQL 2最终获得方式PRIVATE_DOMAIN

private_domain_fulfilled_cnt / uv

加C领取路径已履约次数 / 人数

bigint

PRIVATE_DOMAIN且FULFILLED

repurchase_fulfilled_cnt / uv

复购第二瓶已履约次数 / 人数

bigint

REPURCHASE且FULFILLED

expand_cnt / expand_uv

实际膨胀次数 / 人数

bigint

is_expanded=1
实际加C人数和事件数来自SQL 3，只在独立渠道模块按日期和state展示，不写入活动级应用表。
5.8 瓶内码奖励履约实时应用层表
表用途：从SQL 2参与中奖履约明细按奖品和领取路径聚合中奖、履约、奖励发放和红包转账。表粒度为dt × time_slice_10min × activity_no × prize_id × is_expanded × expand_option_id × effective_grant_mode × stat_time_type。


字段组

字段内容

口径说明

时间维度

dt、time_slice_10min、stat_time_type

WIN_ATTRIBUTION按中奖时间；TRANSFER_OCCURRENCE按红包转账时间

活动与奖品

activity_no、activity_name、prize_id、final_prize_name、final_prize_content_type

最终奖品按实际膨胀结果派生

路径维度

is_expanded、expand_option_id、effective_grant_mode、path_display_name

六类领取路径组合

中奖指标

win_cnt、win_uv

按参与中奖履约明细重新聚合

履约指标

fulfilled_cnt、fulfilled_uv、pending_cnt、failed_cnt

按fulfillment_phase拆分

发放指标

grant_cnt、grant_uv、各内容类型发放数量

按activity_record_no关联的发放明细聚合

红包指标

redpack_instance_cnt、transferred_cnt、not_transferred_cnt、cash_redpack_cost

金额仅统计已转账红包

6. 备忘录


序号

模块

已确认方案

影响范围

1

指标范围

本期共23项P0指标。

全方案

2

活动曝光

曝光只到活动层，不进入奖品路径。

曝光、参与率、模型与BI

3

活动参与

participate_log.hit_result IN (2,3)均计参与。

参与人数、次数、人均次数、参与率

4

活动中奖

participate_log.hit_result=3为活动级权威口径。

活动中奖人数、次数、中奖率

5

中奖率

按实际中奖人数÷参与人数展示，不再设置100%预期。

指标、质量监控、BI

6

奖品中奖

奖品层从record_user_line直接统计，不与活动中奖强制回加。

奖品路径与履约

7

基础奖品

prize_id=activity_prize.id；基础券类型和获得方式取配置表。

奖品维度

8

膨胀能力

activity_prize.is_expand仅表示配置是否支持膨胀。

配置维度

9

实际膨胀

record_user_line.expand_option_id=expand_option.id，并校验prize_row_id。

路径事实与质量

10

膨胀奖品

券类型取expand_target_type，名称取expand_prize_name。

膨胀奖品维度

11

获得方式

基础取prize_grant_mode；膨胀取prize_expand_mode；派生最终获得方式。

加C、复购、直接领取

12

枚举映射

DIRECT=直接领取、PRIVATE_DOMAIN=加C、REPURCHASE=复购第二瓶领取。

模型与BI展示

13

复购第二瓶

最终获得方式REPURCHASE且fulfillment_phase=FULFILLED。

复购指标

14

应用层结构

活动效果、奖品路径效果、奖励履约三张实时应用层表。

应用层交付

15

人数去重

跨日期、奖品和路径的人数从明细重新去重。

全部人数与比率

16

履约归属

发放结果按record_user_line.create_time回写原中奖分片。

奖励履约

17

实时性

10分钟SLA仍待数据开发确认。

全部实时模型


实验SQL
瓶内码活动曝光会员10分钟轻汇总查询

WITH exposure_filtered AS (
    SELECT
        t.rowkey,
        CAST(t.user_id AS STRING) AS member_id,
        CAST(t.event_time AS BIGINT) AS event_time_ms,
        GET_JSON_OBJECT(
            t.properties,
            '$.activity_no'
        ) AS activity_no
    FROM ods_log.t_hmonitor_track_event t
    WHERE t.dt BETWEEN '2026-07-13' AND '2026-07-19'
      AND t.event_code = 'lottery_main_page_bw'
      AND CAST(t.event_time AS BIGINT)
            >= CAST(
                UNIX_TIMESTAMP('2026-07-13 00:00:00') * 1000
                AS BIGINT
            )
      AND CAST(t.event_time AS BIGINT)
            < CAST(
                UNIX_TIMESTAMP('2026-07-20 00:00:00') * 1000
                AS BIGINT
            )
),

exposure_bucketed AS (
    SELECT
        rowkey,
        member_id,
        activity_no,

        CAST(
            FROM_UNIXTIME(
                CAST(event_time_ms / 1000 AS BIGINT),
                'yyyy-MM-dd HH:mm:ss'
            )
            AS TIMESTAMP
        ) AS event_time,

        TO_DATE(
            FROM_UNIXTIME(
                CAST(event_time_ms / 1000 AS BIGINT),
                'yyyy-MM-dd HH:mm:ss'
            )
        ) AS dt,

        FROM_UNIXTIME(
            CAST(
                FLOOR(event_time_ms / 600000) * 600
                AS BIGINT
            ),
            'yyyy-MM-dd HH:mm:ss'
        ) AS time_slice_10min
    FROM exposure_filtered
),

exposure_agg AS (
    SELECT
        dt,
        time_slice_10min,
        activity_no,
        member_id,
        COUNT(DISTINCT rowkey) AS exposure_cnt,
        MIN(event_time) AS first_exposure_time,
        MAX(event_time) AS last_exposure_time
    FROM exposure_bucketed
    GROUP BY
        dt,
        time_slice_10min,
        activity_no,
        member_id
),

activity_dim AS (
    SELECT
        id AS activity_id,
        activity_no,
        activity_name
    FROM lucky_epromotion.t_rtd_cap_activity
)

SELECT /*+ BROADCAST(a) */
    e.dt,
    e.time_slice_10min,
    a.activity_id,
    e.activity_no,
    a.activity_name,
    e.member_id,
    e.exposure_cnt,
    e.first_exposure_time,
    e.last_exposure_time
FROM exposure_agg e
LEFT JOIN activity_dim a
    ON e.activity_no = a.activity_no;
活动业务行为明细

-- 查询名称：瓶内码活动参与中奖履约宽表查询
-- 查询范围：2026-07-13 00:00:00（含）至2026-07-20 00:00:00（不含）
-- 粒度：一行一次活动参与，唯一键为参与流水ID
-- 完成参与：hit_result IN (2, 3)
-- 中奖：hit_result = 3
-- 加C统计仅表示PRIVATE_DOMAIN领取路径及其履约结果，不代表企微实际新增联系人

WITH activity_dim AS (
    SELECT
        id AS activity_id,
        activity_no,
        activity_name
    FROM lucky_epromotion.t_rtd_cap_activity
),

prize_dim AS (
    SELECT
        id AS prize_id,
        activity_id,
        content_type AS base_content_type,
        prize_grant_mode AS base_grant_mode,
        is_expand AS is_expand_supported
    FROM lucky_epromotion.t_rtd_cap_activity_prize
),

expand_dim AS (
    SELECT
        id AS expand_option_id,
        prize_row_id,
        expand_prize_name,
        expand_target_type,
        prize_expand_mode AS expand_grant_mode
    FROM lucky_epromotion.t_rtd_cap_activity_prize_expand_option
),

participate_source AS (
    SELECT
        CAST(p.id AS BIGINT) AS participate_id,
        CAST(p.member_id AS STRING) AS member_id,
        CAST(p.activity_id AS BIGINT) AS activity_id,
        CAST(p.scan_id AS STRING) AS scan_id,
        CAST(p.participate_phase AS INT) AS participate_phase,
        CAST(p.layer_break_code AS STRING) AS layer_break_code,
        CAST(p.hit_result AS INT) AS hit_result,
        CAST(p.create_time AS TIMESTAMP) AS participate_time
    FROM lucky_epromotion.t_rtd_cap_participate_log p
    WHERE CAST(p.create_time AS TIMESTAMP)
              >= CAST('2026-07-13 00:00:00' AS TIMESTAMP)
      AND CAST(p.create_time AS TIMESTAMP)
              < CAST('2026-07-20 00:00:00' AS TIMESTAMP)
),

relevant_scan_keys AS (
    SELECT DISTINCT
        activity_id,
        scan_id
    FROM participate_source
    WHERE scan_id IS NOT NULL
),

win_ranked AS (
    SELECT
        CAST(u.id AS BIGINT) AS user_line_id,
        CAST(u.activity_record_no AS STRING) AS activity_record_no,
        CAST(u.activity_id AS BIGINT) AS activity_id,
        CAST(u.member_id AS STRING) AS member_id,
        CAST(u.first_scan_id AS STRING) AS first_scan_id,
        CAST(u.prize_row_id AS BIGINT) AS prize_id,
        CAST(u.prize_name AS STRING) AS prize_name,
        CAST(u.record_prize_status AS INT) AS record_prize_status,
        CAST(u.record_coupon_status AS INT) AS record_coupon_status,
        CAST(u.prize_grant_mode AS STRING) AS prize_grant_mode_snapshot,
        CAST(u.fulfillment_phase AS STRING) AS fulfillment_phase,
        CAST(u.grant_item_count AS BIGINT) AS grant_item_count_snapshot,
        CAST(u.expand_option_id AS BIGINT) AS expand_option_id,
        CAST(u.claim_time AS TIMESTAMP) AS claim_time,
        CAST(u.create_time AS TIMESTAMP) AS win_time,
        CAST(u.modify_time AS TIMESTAMP) AS win_modify_time,
        CAST(u.fulfillment_fail_code AS STRING) AS fulfillment_fail_code,
        CAST(u.fulfillment_fail_reason AS STRING) AS fulfillment_fail_reason,
        CAST(u.fulfillment_fail_time AS TIMESTAMP) AS fulfillment_fail_time,
        CAST(u.fulfillment_retry_count AS BIGINT) AS fulfillment_retry_caount,
        COUNT(*) OVER (
            PARTITION BY u.activity_id, u.first_scan_id
        ) AS win_match_count,
        ROW_NUMBER() OVER (
            PARTITION BY u.activity_id, u.first_scan_id
            ORDER BY u.create_time, u.id
        ) AS win_row_number
    FROM lucky_epromotion.t_rtd_cap_activity_record_user_line u
    INNER JOIN relevant_scan_keys k
        ON u.activity_id = k.activity_id
       AND CAST(u.first_scan_id AS STRING) = k.scan_id
),

win_one AS (
    SELECT
        user_line_id,
        activity_record_no,
        activity_id,
        member_id,
        first_scan_id,
        prize_id,
        prize_name,
        record_prize_status,
        record_coupon_status,
        prize_grant_mode_snapshot,
        fulfillment_phase,
        grant_item_count_snapshot,
        expand_option_id,
        claim_time,
        win_time,
        win_modify_time,
        fulfillment_fail_code,
        fulfillment_fail_reason,
        fulfillment_fail_time,
        fulfillment_retry_count,
        win_match_count
    FROM win_ranked
    WHERE win_row_number = 1
),

path_joined AS (
    SELECT /*+ BROADCAST(a, pd, ed) */
        p.participate_id,
        p.member_id,
        p.activity_id,
        a.activity_no,
        a.activity_name,
        p.scan_id,
        p.participate_phase,
        p.layer_break_code,
        p.hit_result,
        p.participate_time,
        CASE p.hit_result
            WHEN 0 THEN '不可参与'
            WHEN 1 THEN '待参与'
            WHEN 2 THEN '未中奖'
            WHEN 3 THEN '已中奖'
            ELSE '未知状态'
        END AS hit_result_name,
        CASE
            WHEN p.hit_result IN (2, 3) THEN 1
            ELSE 0
        END AS is_completed_participate,
        CASE
            WHEN p.hit_result = 3 THEN 1
            ELSE 0
        END AS is_win,
        CASE
            WHEN p.hit_result = 3
             AND w.user_line_id IS NULL
            THEN 'MISSING_WIN'
            WHEN p.hit_result = 3
             AND w.win_match_count = 1
            THEN 'MATCHED'
            WHEN p.hit_result = 3
             AND w.win_match_count > 1
            THEN 'MULTIPLE_WIN'
            WHEN p.hit_result <> 3
             AND w.user_line_id IS NOT NULL
            THEN 'UNEXPECTED_WIN'
            ELSE 'NOT_WIN'
        END AS participate_win_join_status,
        COALESCE(w.win_match_count, 0) AS win_match_count,
        w.user_line_id,
        w.activity_record_no,
        w.first_scan_id,
        w.prize_id,
        w.prize_name,
        pd.base_content_type,
        pd.base_grant_mode,
        CAST(pd.is_expand_supported AS INT) AS is_expand_supported,
        w.record_prize_status,
        w.record_coupon_status,
        w.prize_grant_mode_snapshot,
        w.fulfillment_phase,
        w.grant_item_count_snapshot,
        w.expand_option_id,
        ed.prize_row_id AS expand_prize_row_id,
        ed.expand_prize_name,
        ed.expand_target_type,
        ed.expand_grant_mode,
        w.claim_time,
        w.win_time,
        w.win_modify_time,
        w.fulfillment_fail_code,
        w.fulfillment_fail_reason,
        w.fulfillment_fail_time,
        w.fulfillment_retry_count
    FROM participate_source p
    LEFT JOIN activity_dim a
        ON p.activity_id = a.activity_id
    LEFT JOIN win_one w
        ON p.activity_id = w.activity_id
       AND p.scan_id = w.first_scan_id
    LEFT JOIN prize_dim pd
        ON w.prize_id = pd.prize_id
       AND w.activity_id = pd.activity_id
    LEFT JOIN expand_dim ed
        ON w.expand_option_id = ed.expand_option_id
),

path_calculated AS (
    SELECT
        j.*,
        CASE
            WHEN j.user_line_id IS NULL THEN NULL
            WHEN j.expand_option_id IS NULL THEN 'NOT_EXPANDED'
            WHEN j.expand_prize_row_id IS NULL THEN 'ID_NOT_FOUND'
            WHEN j.expand_prize_row_id <> j.prize_id THEN 'PRIZE_MISMATCH'
            ELSE 'MATCHED'
        END AS expand_join_status,
        CASE
            WHEN j.user_line_id IS NULL THEN NULL
            WHEN j.expand_option_id IS NULL THEN 0
            WHEN j.expand_prize_row_id = j.prize_id THEN 1
            ELSE NULL
        END AS is_expanded,
        CASE
            WHEN j.user_line_id IS NULL THEN NULL
            WHEN j.expand_option_id IS NULL THEN j.base_grant_mode
            WHEN j.expand_prize_row_id = j.prize_id THEN j.expand_grant_mode
            ELSE NULL
        END AS effective_grant_mode
    FROM path_joined j
),

business_detail AS (
    SELECT
        c.*,
        CASE
            WHEN c.is_expanded = 0
             AND c.effective_grant_mode = 'DIRECT'
            THEN '直接领取'
            WHEN c.is_expanded = 0
             AND c.effective_grant_mode = 'PRIVATE_DOMAIN'
            THEN '加C领取'
            WHEN c.is_expanded = 0
             AND c.effective_grant_mode = 'REPURCHASE'
            THEN '复购第二瓶领取'
            WHEN c.is_expanded = 1
             AND c.effective_grant_mode = 'DIRECT'
            THEN '膨胀后直接领取'
            WHEN c.is_expanded = 1
             AND c.effective_grant_mode = 'PRIVATE_DOMAIN'
            THEN '膨胀后加C领取'
            WHEN c.is_expanded = 1
             AND c.effective_grant_mode = 'REPURCHASE'
            THEN '膨胀后复购第二瓶领取'
            ELSE NULL
        END AS path_display_name,
        CASE
            WHEN c.hit_result <> 3 THEN 0
            WHEN c.effective_grant_mode IS NULL THEN NULL
            WHEN c.effective_grant_mode = 'PRIVATE_DOMAIN' THEN 1
            ELSE 0
        END AS is_private_domain_path,
        CASE
            WHEN c.hit_result <> 3 THEN 0
            WHEN c.effective_grant_mode IS NULL THEN NULL
            WHEN c.effective_grant_mode = 'PRIVATE_DOMAIN'
             AND c.fulfillment_phase = 'FULFILLED' THEN 1
            ELSE 0
        END AS is_private_domain_fulfilled,
        CASE
            WHEN c.hit_result = 3
             AND c.effective_grant_mode IS NULL
            THEN 'PATH_INVALID'
            WHEN c.hit_result <> 3
              OR c.effective_grant_mode <> 'PRIVATE_DOMAIN'
            THEN 'NOT_PRIVATE_DOMAIN'
            WHEN c.fulfillment_phase = 'FULFILLED'
            THEN 'FULFILLED'
            ELSE 'PENDING'
        END AS private_domain_fulfillment_status
    FROM path_calculated c
),

relevant_record_keys AS (
    SELECT DISTINCT
        activity_record_no
    FROM business_detail
    WHERE activity_record_no IS NOT NULL
),

grant_summary AS (
    SELECT
        CAST(g.activity_record_no AS STRING) AS activity_record_no,
        COUNT(DISTINCT g.id) AS grant_item_count,
        SUM(CASE WHEN g.content_type = 1 THEN 1 ELSE 0 END) AS redpack_grant_count,
        SUM(CASE WHEN g.content_type = 2 THEN 1 ELSE 0 END) AS instant_coupon_grant_count,
        SUM(CASE WHEN g.content_type = 3 THEN 1 ELSE 0 END) AS coffee_coupon_grant_count,
        SUM(CASE WHEN g.content_type = 4 THEN 1 ELSE 0 END) AS coffee_store_coupon_grant_count,
        MIN(CAST(g.create_time AS TIMESTAMP)) AS first_grant_time,
        MAX(CAST(g.create_time AS TIMESTAMP)) AS last_grant_time
    FROM lucky_epromotion.t_rtd_cap_activity_record_user_line_grant_item g
    INNER JOIN relevant_record_keys k
        ON CAST(g.activity_record_no AS STRING) = k.activity_record_no
    GROUP BY
        CAST(g.activity_record_no AS STRING)
),

redpack_summary AS (
    SELECT
        CAST(r.activity_record_no AS STRING) AS activity_record_no,
        COUNT(DISTINCT r.id) AS redpack_instance_count,
        SUM(CASE WHEN r.instance_status = 50 THEN 1 ELSE 0 END) AS redpack_transferred_count,
        SUM(CASE WHEN r.instance_status <> 50 THEN 1 ELSE 0 END) AS redpack_not_transferred_count,
        SUM(
            CASE
                WHEN r.instance_status = 50
                THEN CAST(r.redpack_denomination AS DECIMAL(18, 2))
                ELSE CAST(0 AS DECIMAL(18, 2))
            END
        ) AS redpack_transferred_amount,
        MAX(
            CASE
                WHEN r.instance_status = 50
                THEN CAST(r.transfer_done_time AS TIMESTAMP)
            END
        ) AS last_transfer_done_time
    FROM lucky_epromotion.t_rtd_redpack_user_instance r
    INNER JOIN relevant_record_keys k
        ON CAST(r.activity_record_no AS STRING) = k.activity_record_no
    GROUP BY
        CAST(r.activity_record_no AS STRING)
)

SELECT
    TO_DATE(b.participate_time) AS `日期`,
    FROM_UNIXTIME(
        CAST(
            FLOOR(UNIX_TIMESTAMP(b.participate_time) / 600) * 600
            AS BIGINT
        ),
        'yyyy-MM-dd HH:mm:ss'
    ) AS `10分钟时间片`,
    b.participate_time AS `参与时间`,
    b.participate_id AS `参与流水ID`,
    b.activity_id AS `活动ID`,
    b.activity_no AS `活动编号`,
    b.activity_name AS `活动名称`,
    b.member_id AS `会员ID`,
    b.scan_id AS `扫码ID`,
    b.participate_phase AS `参与阶段`,
    b.layer_break_code AS `拦截层诊断码`,
    b.hit_result AS `参与结果编码`,
    b.hit_result_name AS `参与结果名称`,
    b.is_completed_participate AS `是否完成参与`,
    b.is_win AS `是否中奖`,
    b.participate_win_join_status AS `参与中奖关联状态`,
    b.win_match_count AS `匹配中奖记录数`,
    b.user_line_id AS `中奖记录行ID`,
    b.activity_record_no AS `中奖记录编号`,
    b.first_scan_id AS `中奖记录首次扫码ID`,
    b.win_time AS `中奖记录时间`,
    b.win_modify_time AS `中奖记录修改时间`,
    b.claim_time AS `路径确认时间`,
    b.prize_id AS `基础奖品ID`,
    b.prize_name AS `基础奖品名称`,
    b.base_content_type AS `基础奖品内容类型`,
    b.base_grant_mode AS `基础获得方式`,
    b.prize_grant_mode_snapshot AS `中奖获得方式快照`,
    b.is_expand_supported AS `是否支持膨胀`,
    b.record_prize_status AS `中奖记录奖品状态`,
    b.record_coupon_status AS `中奖记录券状态`,
    b.expand_option_id AS `膨胀选项ID`,
    b.expand_join_status AS `膨胀关联状态`,
    b.is_expanded AS `是否实际膨胀`,
    CASE
        WHEN b.is_expanded = 1 THEN b.expand_prize_name
    END AS `膨胀奖品名称`,
    CASE
        WHEN b.is_expanded = 1 THEN b.expand_target_type
    END AS `膨胀奖品内容类型`,
    CASE
        WHEN b.is_expanded = 1 THEN b.expand_grant_mode
    END AS `膨胀获得方式`,
    b.effective_grant_mode AS `最终获得方式`,
    b.path_display_name AS `路径展示名称`,
    b.fulfillment_phase AS `履约阶段`,
    b.is_private_domain_path AS `是否加C领取路径`,
    b.is_private_domain_fulfilled AS `加C领取路径是否已履约`,
    b.private_domain_fulfillment_status AS `加C领取路径履约状态`,
    b.grant_item_count_snapshot AS `中奖记录发放明细数量`,
    COALESCE(g.grant_item_count, 0) AS `实际发放明细数量`,
    CASE
        WHEN b.user_line_id IS NULL THEN 'NOT_APPLICABLE'
        WHEN COALESCE(g.grant_item_count, 0)
             = COALESCE(b.grant_item_count_snapshot, 0)
        THEN 'MATCHED'
        ELSE 'MISMATCH'
    END AS `发放明细数量校验状态`,
    COALESCE(g.redpack_grant_count, 0) AS `红包发放数量`,
    COALESCE(g.instant_coupon_grant_count, 0) AS `即享券发放数量`,
    COALESCE(g.coffee_coupon_grant_count, 0) AS `咖啡券发放数量`,
    COALESCE(g.coffee_store_coupon_grant_count, 0) AS `咖啡门店券发放数量`,
    g.first_grant_time AS `首次发放时间`,
    g.last_grant_time AS `最后发放时间`,
    COALESCE(r.redpack_instance_count, 0) AS `红包实例数量`,
    COALESCE(r.redpack_transferred_count, 0) AS `红包已转账数量`,
    COALESCE(r.redpack_not_transferred_count, 0) AS `红包未转账数量`,
    COALESCE(
        r.redpack_transferred_amount,
        CAST(0 AS DECIMAL(18, 2))
    ) AS `红包已转账金额`,
    r.last_transfer_done_time AS `最后红包转账完成时间`,
    b.fulfillment_fail_code AS `履约失败码`,
    b.fulfillment_fail_reason AS `履约失败原因`,
    b.fulfillment_fail_time AS `履约失败时间`,
    b.fulfillment_retry_count AS `履约失败重试次数`
FROM business_detail b
LEFT JOIN grant_summary g
    ON b.activity_record_no = g.activity_record_no
LEFT JOIN redpack_summary r
    ON b.activity_record_no = r.activity_record_no;
活动实际加C用户明细

-- SQL 3：瓶内码实际加C会员10分钟轻明细查询
-- 粒度：日期 + 10分钟时间片 + 加C渠道state + member_id
-- 实际加C：event_type = 'add_external_contact'
-- 时间字段：event_time为13位毫秒时间戳，不能直接CAST AS TIMESTAMP
-- 用途：支持BI按任意日期范围重新去重实际加C会员人数
-- 边界：state不是RTD活动ID，本查询暂不归因到具体活动

WITH add_c_filtered AS (
    SELECT
        CAST(h.id AS BIGINT) AS event_id,
        CAST(h.user_id AS STRING) AS service_user_id,
        CAST(h.member_id AS STRING) AS member_id,
        CAST(h.external_user_id AS STRING) AS external_user_id,
        CAST(h.event_type AS STRING) AS event_type,
        CAST(h.state AS STRING) AS add_c_state,
        CAST(h.brand_type AS STRING) AS brand_type,
        CAST(h.event_time AS BIGINT) AS event_time_ms
    FROM lucky_wecom.t_wecom_external_user_history h
    WHERE h.event_type = 'add_external_contact'
      AND h.state IN (
          'rtd瓶装饮料-瓶内营销码即享优惠券',
          'rtd瓶装饮料-瓶内营销码现制饮品优惠券',
          'rtd瓶装饮料-瓶内营销码现金红包'
      )
      AND CAST(h.event_time AS BIGINT)
              >= CAST(UNIX_TIMESTAMP('2026-07-13 00:00:00') * 1000 AS BIGINT)
      AND CAST(h.event_time AS BIGINT)
              < CAST(UNIX_TIMESTAMP('2026-07-20 00:00:00') * 1000 AS BIGINT)
),

add_c_bucketed AS (
    SELECT
        event_id,
        service_user_id,
        member_id,
        external_user_id,
        event_type,
        add_c_state,
        brand_type,
        CAST(
            FROM_UNIXTIME(
                CAST(event_time_ms / 1000 AS BIGINT),
                'yyyy-MM-dd HH:mm:ss'
            ) AS TIMESTAMP
        ) AS add_c_time,
        TO_DATE(
            FROM_UNIXTIME(
                CAST(event_time_ms / 1000 AS BIGINT),
                'yyyy-MM-dd HH:mm:ss'
            )
        ) AS dt,
        FROM_UNIXTIME(
            CAST(FLOOR(event_time_ms / 600000) * 600 AS BIGINT),
            'yyyy-MM-dd HH:mm:ss'
        ) AS time_slice_10min
    FROM add_c_filtered
)

SELECT
    dt AS `日期`,
    time_slice_10min AS `10分钟时间片`,
    add_c_state AS `加C渠道原始值`,
    CASE add_c_state
        WHEN 'rtd瓶装饮料-瓶内营销码即享优惠券'
        THEN '即享优惠券'
        WHEN 'rtd瓶装饮料-瓶内营销码现制饮品优惠券'
        THEN '现制饮品优惠券'
        WHEN 'rtd瓶装饮料-瓶内营销码现金红包'
        THEN '现金红包'
    END AS `加C渠道`,
    member_id AS `会员ID`,
    CASE
        WHEN member_id IS NULL THEN 'MISSING_MEMBER'
        ELSE 'VALID'
    END AS `会员ID状态`,
    MAX(event_type) AS `加C事件类型`,
    COUNT(DISTINCT event_id) AS `加C事件数`,
    COUNT(DISTINCT external_user_id) AS `企微外部联系人数`,
    CASE
        WHEN COUNT(DISTINCT external_user_id) = 1
        THEN MAX(external_user_id)
        ELSE NULL
    END AS `唯一企微外部联系人ID`,
    COUNT(DISTINCT service_user_id) AS `企微服务人员数`,
    CASE
        WHEN COUNT(DISTINCT service_user_id) = 1
        THEN MAX(service_user_id)
        ELSE NULL
    END AS `唯一企微服务人员ID`,
    COUNT(DISTINCT brand_type) AS `品牌类型数`,
    CASE
        WHEN COUNT(DISTINCT brand_type) = 1
        THEN MAX(brand_type)
        ELSE NULL
    END AS `唯一品牌类型`,
    MIN(add_c_time) AS `首次加C时间`,
    MAX(add_c_time) AS `最后加C时间`,
    CASE
        WHEN COUNT(DISTINCT external_user_id) = 0
        THEN 'MISSING_EXTERNAL_USER'
        WHEN COUNT(DISTINCT external_user_id) = 1
        THEN 'UNIQUE'
        ELSE 'MULTIPLE_EXTERNAL_USER'
    END AS `企微外部联系人关联状态`
FROM add_c_bucketed
GROUP BY
    dt,
    time_slice_10min,
    add_c_state,
    member_id;

业务库表信息

瓶内码营销分析数据表.md


