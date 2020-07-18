#! usr/bin/env python
import pandas as pd


pd_fin = pd.read_csv('D:\\股票分析\\沪深股票财务指标_2017至2019年.csv')
pd_balance = pd.read_csv('D:\\股票分析\\沪深股票资产负债表_2017至2019年.csv')
pd_stock = pd.read_csv('D:\\股票分析\\沪深股票列表.csv')

# 1.将基本财务指标、资产负债表、股票基本信息表合并，筛选出近三年的年报
plus_financial = pd_fin.merge(pd_balance, how='left', on=['ts_code', '报告期'])    # 将基本财务指标与资产负债表指标合并
plus_financial = plus_financial[plus_financial['报告期'].isin(['20171231', '20181231', '20191231'])]    # 筛选出年报数据
plus_candidate = plus_financial.merge(pd_stock, how='left', on='ts_code')         # 将年报数据与股票基本信息合并


# 2.在原始指标上，加工生成新的指标
plus_candidate['商誉净资产比'] = plus_candidate['商誉']/plus_candidate['股东权益合计(含少数股东权益)']
plus_candidate['存货净资产比'] = plus_candidate['存货']/plus_candidate['股东权益合计(含少数股东权益)']
plus_candidate['应收账款净资产比'] = plus_candidate['应收账款']/plus_candidate['股东权益合计(含少数股东权益)']
plus_candidate['应收票据净资产比'] = plus_candidate['应收票据']/plus_candidate['股东权益合计(含少数股东权益)']
plus_candidate['扣非净利率(%)'] = plus_candidate['扣除非经常性损益后的净利润']/(plus_candidate['每股营业总收入']*plus_candidate['期末总股本'])*100

# 调整列的顺序
order = ['ts_code', '公告日期', '报告期', '股票代码', '股票名称', '所在地域', '所属行业', '上市日期', '基本每股收益', '稀释每股收益', '每股营业总收入',
       '扣除非经常性损益后的净利润', '流动比率', '速动比率', '存货周转率', '应收账款周转率', '总资产周转率', '每股净资产',
       '净利率(%)', '营业利润率(%)', '净资产收益率(%)', '加权平均净资产收益率(%)',
       '净资产收益率(扣除非经常性损益)(%)', '总资产报酬率(%)', '销售商品提供劳务收到的现金/营业收入',
       '经营活动产生的现金流量净额/经营活动净收益', '资产负债率(%)', '基本每股收益同比增长率(%)', '稀释每股收益同比增长率(%)',
       '营业利润同比增长率(%)', '归属母公司股东的净利润同比增长率(%)', '归属母公司股东的净利润-扣除非经常损益同比增长率(%)',
       '净资产收益率(摊薄)同比增长率(%)', '营业总收入同比增长率(%)', '营业收入同比增长率(%)', '研发费用', '更新标识_x',
       'Unnamed: 0_y', '报表类型', '公司类型', '期末总股本', '货币资金', '交易性金融资产', '应收票据',
       '应收账款', '其他应收款', '预付款项', '存货', '可供出售金融资产', '持有至到期投资', '长期股权投资', '定期存款',
       '无形资产', '研发支出', '商誉', '资产总计', '负债合计', '少数股东权益', '股东权益合计(不含少数股东权益)',
       '股东权益合计(含少数股东权益)', '更新标识_y', '市场类型', '是否沪深港通标的', '商誉净资产比', '存货净资产比', '应收账款净资产比',
       '应收票据净资产比', '扣非净利率(%)']
plus_candidate = plus_candidate[order]


# 3.过滤点次新股（成立时间早于2019.3.31）
plus_candidate['上市日期'] = pd.to_datetime(plus_candidate['上市日期'], format='%Y%m%d')     # 将数据类型转换为日期类型，以便下面按日期进行筛选
plus_candidate = plus_candidate.set_index('上市日期').sort_index()        # 使用日期截断函数truncate()之前，需要先将上市日期设为index，并排序（此处按升序排）
plus_candidate = plus_candidate.truncate(after='2019-03-01')    # 截取指定日期以后的数据，只保留日期之前的数据。注意：该筛选条件不能与上面财务指标筛选写在一起，上面


# 4.计算每只股票，最近三年的指标是否都满足条件(须考虑有些股票成立时间不足三年)
select = pd.DataFrame()           # 用于后续记录符合条件的股票
set_tscode = set(plus_candidate['ts_code'].values)
for stock in set_tscode:
    pd_temp = plus_candidate[plus_candidate['ts_code'] == stock]

    # pd_judge筛选出相反条件的数据，pd_judge存在数据，则说明该只股票不符合筛选条件
    if pd_temp['加权平均净资产收益率(%)'].mean() < 15 or\
            pd_temp['销售商品提供劳务收到的现金/营业收入'].mean() < 1 or\
            pd_temp['经营活动产生的现金流量净额/经营活动净收益'].mean() < 1 or\
            pd_temp['扣非净利率(%)'].mean() < 15 or\
            pd_temp['商誉净资产比'].mean() > 0.5 or\
            pd_temp['存货净资产比'].mean() > 0.5 or\
            pd_temp['应收账款净资产比'].mean() > 0.5 or\
            pd_temp['流动比率'].mean() < 2 or\
            pd_temp['速动比率'].mean() < 1 or\
            pd_temp['营业总收入同比增长率(%)'].mean() < 15 or\
            pd_temp['归属母公司股东的净利润-扣除非经常损益同比增长率(%)'].mean() < 15:
        continue
    else:
        select = select.append(pd_temp)

select.to_csv('D:\\股票分析\\财务指标选股（多期平均值满足）_2017至2019年.csv')
