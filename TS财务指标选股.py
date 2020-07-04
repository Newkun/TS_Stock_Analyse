#! usr/bin/env python
import pandas as pd
import TS计算大股东质押率
import time

pd_stock = pd.read_csv('D:\\股票分析\\沪深股票列表.csv')
pd_fin = pd.read_csv('D:\\股票分析\\沪深股票财务指标20191231.csv')
pd_price = pd.read_csv('D:\\股票分析\\沪深股票价格20200529.csv')
pd_balance = pd.read_csv('D:\\股票分析\\沪深股票资产负债表20191231.csv')


# 1.对财务指标中的同一只股票去重，保留最新记录 (由于上市公司更新财报，会导致同一公司存在多条记录)
result_fin = pd_fin.drop_duplicates(subset=['ts_code'], keep='last')
result_balance = pd_balance.drop_duplicates(subset=['ts_code'], keep='last')


# 2.从财务指标股票表、资产负债表中精选指标
result_fin = pd_fin.loc[:, ['ts_code', 'ann_date', 'end_date', 'eps', 'dt_eps', 'total_revenue_ps', 'profit_dedt', 'current_ratio', 'quick_ratio', 'inv_turn', 'ar_turn',
                        'assets_turn', 'bps', 'profit_to_gr', 'op_of_gr', 'roe', 'roe_waa', 'roe_dt', 'roa', 'salescash_to_or',
                        'ocf_to_opincome', 'debt_to_assets', 'basic_eps_yoy', 'dt_eps_yoy', 'op_yoy', 'netprofit_yoy', 'dt_netprofit_yoy',
                        'roe_yoy', 'tr_yoy', 'or_yoy', 'rd_exp', 'update_flag']]

result_fin.columns = ['ts_code', '公告日期', '报告期', '基本每股收益', '稀释每股收益', '每股营业总收入', '扣除非经常性损益后的净利润', '流动比率', '速动比率', '存货周转率', '应收账款周转率', '总资产周转率',
                  '每股净资产', '净利率(%)', '营业利润率(%)', '净资产收益率(%)', '加权平均净资产收益率(%)', '净资产收益率(扣除非经常性损益)(%)', '总资产报酬率(%)', '销售商品提供劳务收到的现金/营业收入',
                  '经营活动产生的现金流量净额/经营活动净收益', '资产负债率(%)', '基本每股收益同比增长率(%)', '稀释每股收益同比增长率(%)', '营业利润同比增长率(%)', '归属母公司股东的净利润同比增长率(%)',
                  '归属母公司股东的净利润-扣除非经常损益同比增长率(%)', '净资产收益率(摊薄)同比增长率(%)', '营业总收入同比增长率(%)', '营业收入同比增长率(%)', '研发费用', '更新标识']


result_balance = result_balance.loc[:, ['ts_code', 'end_date', 'report_type', 'comp_type', 'total_share',
                      'money_cap', 'trad_asset', 'notes_receiv', 'accounts_receiv', 'oth_receiv', 'prepayment', 'inventories',
                      'fa_avail_for_sale', 'htm_invest', 'lt_eqt_invest', 'time_deposits',
                      'intan_assets', 'r_and_d', 'goodwill', 'total_assets', 'total_liab', 'minority_int', 'total_hldr_eqy_exc_min_int',
                      'total_hldr_eqy_inc_min_int', 'update_flag']]

result_balance.columns = ['ts_code', '报告期', '报表类型', '公司类型', '期末总股本',
                      '货币资金', '交易性金融资产', '应收票据', '应收账款', '其他应收款', '预付款项', '存货',
                      '可供出售金融资产', '持有至到期投资', '长期股权投资', '定期存款',
                      '无形资产', '研发支出', '商誉', '资产总计', '负债合计', '少数股东权益', '股东权益合计(不含少数股东权益)',
                      '股东权益合计(含少数股东权益)', '更新标识']

result_price = pd_price.loc[:, ['ts_code', '交易日期', '收盘价', '涨跌幅 ', '换手率', '量比']]


# 3.合并各类表
plus1 = result_fin.merge(pd_stock, how='left', on='ts_code')         # 将精简财务指标表与股票全量列表合并
plus2 = plus1.merge(result_price, how='left', on='ts_code')        # 将合并的表与股票行情表合并
plus3 = plus2.merge(result_balance, how='left', on='ts_code')        # 将合并的表与资产负债表合并


# 4. 根据原始指标，计算相关指标，增加到表格中
plus3['市盈率'] = plus3['收盘价']/plus3['基本每股收益']
plus3['市净率'] = plus3['收盘价']/plus3['每股净资产']
plus3['商誉净资产比'] = plus3['商誉']/plus3['股东权益合计(含少数股东权益)']
plus3['存货净资产比'] = plus3['存货']/plus3['股东权益合计(含少数股东权益)']
plus3['应收账款净资产比'] = plus3['应收账款']/plus3['股东权益合计(含少数股东权益)']
plus3['应收票据净资产比'] = plus3['应收票据']/plus3['股东权益合计(含少数股东权益)']
plus3['扣非净利率(%)'] = plus3['扣除非经常性损益后的净利润']/(plus3['每股营业总收入']*plus3['期末总股本'])*100
plus3['扣非净利润增长率/市盈率'] = plus3['归属母公司股东的净利润-扣除非经常损益同比增长率(%)']/plus3['市盈率']


# 5.调整列的顺序
order = ['ts_code', '股票代码', '股票名称', '所属行业', '所在地域', '加权平均净资产收益率(%)', '净资产收益率(扣除非经常性损益)(%)', '扣非净利率(%)', '销售商品提供劳务收到的现金/营业收入',
       '市盈率', '扣非净利润增长率/市盈率', '市净率', '营业总收入同比增长率(%)', '归属母公司股东的净利润-扣除非经常损益同比增长率(%)', '基本每股收益同比增长率(%)',
       '稀释每股收益同比增长率(%)','资产负债率(%)', '流动比率', '速动比率', '商誉净资产比', '存货净资产比', '应收账款净资产比', '应收票据净资产比', '营业收入同比增长率(%)',
       '营业利润同比增长率(%)', '归属母公司股东的净利润同比增长率(%)', '净资产收益率(摊薄)同比增长率(%)',
       '公告日期', '报告期_x', '基本每股收益', '稀释每股收益', '存货周转率', '应收账款周转率', '总资产周转率', '每股净资产', '净利率(%)', '营业利润率(%)',
       '净资产收益率(%)', '总资产报酬率(%)', '经营活动产生的现金流量净额/经营活动净收益',  '研发费用', '更新标识_x',
       '市场类型', '上市日期', '是否沪深港通标的', '交易日期', '收盘价', '涨跌幅 ', '换手率', '量比', '报告期_y', '报表类型',
       '公司类型', '期末总股本', '货币资金', '交易性金融资产', '应收票据', '应收账款', '其他应收款', '预付款项', '存货', '可供出售金融资产', '持有至到期投资',
       '长期股权投资', '定期存款', '无形资产', '研发支出', '商誉', '资产总计', '负债合计', '股东权益合计(含少数股东权益)', '股东权益合计(不含少数股东权益)',
       '少数股东权益', '更新标识_y']

plus3 = plus3[order]


# 6.从合并后的表中，筛选出满足指标的股票
plus3['上市日期'] = pd.to_datetime(plus3['上市日期'], format='%Y%m%d')     # 将数据类型转换为日期类型，以便下面按日期进行筛选

# 使用日期截断函数truncate()之前，需要先将上市日期设为index，并排序（此处按升序排）
# 方法1：
# plus3 = plus3.sort_values('上市日期')
# plus3 = plus3.set_index('上市日期')
# 方法2：
plus3 = plus3.set_index('上市日期').sort_index()

select = plus3[(plus3['加权平均净资产收益率(%)']>=15) & (plus3['销售商品提供劳务收到的现金/营业收入']>=1) & (plus3['经营活动产生的现金流量净额/经营活动净收益']>=1) &
               (plus3['扣非净利率(%)']>=15) & (plus3['商誉净资产比']<=0.5) & (plus3['存货净资产比']<=0.5) & (plus3['应收账款净资产比']<=0.5) &
               (plus3['流动比率']>=2) & (plus3['速动比率']>=1) & (plus3['营业总收入同比增长率(%)']>=20) & (plus3['归属母公司股东的净利润-扣除非经常损益同比增长率(%)']>=20)]

select = select.truncate(after='2019-05-01')    # 截取指定日期以后的数据，只保留日期之前的数据。注意：该筛选条件不能与上面财务指标筛选写在一起，上面
# 针对columns筛选，这里针对index筛选，函数的格式不同，放到一起会报错！

select = select.sort_values(by='市盈率', ascending=True)


# 7.在筛选出的股票基础上，评估大股东质押率
list_pledge = []
for code in select['ts_code'].values:
    a = TS计算大股东质押率.get_pledgeHolders10(code, '20200331')
    list_pledge.append(a)
select['前十大股东质押率'] = list_pledge
select['前十大股东质押率'].fillna(0, inplace=True)    # 将质押率为NaN（即空）的数据，转化成0，以便筛选
select = select[select['前十大股东质押率']<=25]
select.to_csv('D:\\股票分析\\基本面选股_基于19年年报和0529股价(市盈率升序).csv')


# 后续迭代
# 1.衡量业绩的稳定性：评估至少两年的财报指标
