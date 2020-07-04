#! usr/bin/env python
import tushare as ts
import pandas as pd
import TS_getStock, TS计算大股东质押率
import time

# 从本地读取token
f = open('D:\\股票分析\\token.txt')
token = f.read()

ts.set_token(token)
pro = ts.pro_api()
pd_stock = TS_getStock.get_stock()

# 1.输入股票
while True:
    stock = input('请输入股票名称/代码：')
    ts_code = ''
    if stock in pd_stock['股票代码'].values:
        if stock.startswith('6'):
            ts_code = stock + '.SH'
        elif stock.startswith('3'):
            ts_code = stock + '.SZ'
        else:                                      # 最后一种可能性，即是以0开头
            ts_code = stock + '.SZ'
        break

    elif stock in pd_stock['股票名称'].values:
        ts_code = list(pd_stock[pd_stock['股票名称'].isin([stock])]['ts_code'])[0]      # 将series转化成列表，取出列表中的值
        break

    else:
        print('输入的股票不存在，请重新输入：')


# 2.调用函数，获取股票在指定报告期的财务指标、资产负债表, 并去重，并匹配股票基本信息
def evaluateStock(period):
    '''获取某一年度的财务指标'''
    pd_fin = pro.fina_indicator(ts_code=ts_code, period=period, fields=
                 'ts_code, ann_date, end_date, eps, dt_eps, total_revenue_ps, profit_dedt, current_ratio, quick_ratio,'
                 'inv_turn, ar_turn, assets_turn, bps, profit_to_gr, op_of_gr, roe, roe_waa, roe_dt, roa,'
                 'salescash_to_or, ocf_to_opincome, debt_to_assets, basic_eps_yoy, dt_eps_yoy, op_yoy, netprofit_yoy, dt_netprofit_yoy,'
                 'roe_yoy, tr_yoy, or_yoy, rd_exp, update_flag', timeout=5)
    pd_fin = pd_fin.drop_duplicates(subset=['ts_code'], keep='last')

    pd_fin.columns = ['ts_code', '公告日期', '报告期', '基本每股收益', '稀释每股收益', '每股营业总收入', '扣除非经常性损益后的净利润', '流动比率', '速动比率', '存货周转率', '应收账款周转率', '总资产周转率',
                      '每股净资产', '净利率(%)', '营业利润率(%)', '净资产收益率(%)', '加权平均净资产收益率(%)', '净资产收益率(扣除非经常性损益)(%)', '总资产报酬率(%)', '销售商品提供劳务收到的现金/营业收入',
                      '经营活动产生的现金流量净额/经营活动净收益', '资产负债率(%)', '基本每股收益同比增长率(%)', '稀释每股收益同比增长率(%)', '营业利润同比增长率(%)', '归属母公司股东的净利润同比增长率(%)',
                      '归属母公司股东的净利润-扣除非经常损益同比增长率(%)', '净资产收益率(摊薄)同比增长率(%)', '营业总收入同比增长率(%)', '营业收入同比增长率(%)', '研发费用', '更新标识']


    pd_balance = pro.balancesheet(ts_code=ts_code, period=period, fields='ts_code, end_date, report_type, comp_type, total_share,'
                    'money_cap, trad_asset, notes_receiv, accounts_receiv, oth_receiv, prepayment, inventories,'
                    'fa_avail_for_sale, htm_invest, lt_eqt_invest, time_deposits,'
                    'intan_assets, r_and_d, goodwill, total_assets, total_liab, minority_int, total_hldr_eqy_exc_min_int,'
                    'total_hldr_eqy_inc_min_int, update_flag', timeout=5)
    pd_balance = pd_balance.drop_duplicates(subset=['ts_code'], keep='last')

    pd_balance.columns = ['ts_code', '报告期', '报表类型', '公司类型', '期末总股本',
                          '货币资金', '交易性金融资产', '应收票据', '应收账款', '其他应收款', '预付款项', '存货',
                          '可供出售金融资产', '持有至到期投资', '长期股权投资', '定期存款',
                          '无形资产', '研发支出', '商誉', '资产总计', '负债合计',  '少数股东权益', '股东权益合计(不含少数股东权益)', '股东权益合计(含少数股东权益)',
                          '更新标识']

    # 合并以上查到的表字段
    plus1 = pd_fin.merge(pd_balance, how='left', on='ts_code')         # 将财务指标表与资产负债表合并
    plus2 = plus1.merge(pd_stock, how='left', on='ts_code')        # 将合并的表与股票基本信息表合并


    # 增加相关字段
    plus2['商誉净资产比'] = plus2['商誉']/plus2['股东权益合计(含少数股东权益)']
    plus2['存货净资产比'] = plus2['存货']/plus2['股东权益合计(含少数股东权益)']
    plus2['应收账款净资产比'] = plus2['应收账款']/plus2['股东权益合计(含少数股东权益)']
    plus2['应收票据净资产比'] = plus2['应收票据']/plus2['股东权益合计(含少数股东权益)']

    # 数字与NaN（空值）相加为0的处理方法1——对于列中值为NaN的数据，在新创建的副本中替换为0，再赋给原对象，以便相加
    # plus2.loc[:, ['应收账款净资产比', '应收票据净资产比']] = plus2.loc[:, ['应收账款净资产比', '应收票据净资产比']].fillna(0)
    # # 数字与NaN（空值）相加为0的处理方法2——对于列中值为NaN的数据，在原对象（非新创建的副本）中先替换为0，以便相加。注意：方法1中用loc选择多行后，不能用
    # # inplace=True，可能是因为loc选择多行后，已经脱离了原对象，创建了新对象
    # plus2['应收账款净资产比'].fillna(0, inplace=True)
    # plus2['应收票据净资产比'].fillna(0, inplace=True)
    # plus2['应收账款和应收票据合计占净资产比'] = plus2['应收账款净资产比'] + plus2['应收票据净资产比']
    # # 数字与NaN（空值）相加为0的处理方法3——不更改原始列，只更改相加汇总的列，在汇总列中的计算中，将值NaN替换为0
    plus2['应收账款和应收票据合计占净资产比'] = plus2['应收账款净资产比'].add(plus2['应收票据净资产比'], fill_value=0)
    plus2['扣非净利率(%)'] = plus2['扣除非经常性损益后的净利润']/(plus2['每股营业总收入']*plus2['期末总股本'])*100

    return plus2

list_date = ['20191231', '20181231', '20171231']
pd_plusDate = pd.DataFrame()


for date in list_date:
    pd = evaluateStock(date)
    pd_plusDate = pd_plusDate.append(pd)
pd_plusDate.index = list(range(3))        # 修改索引，以便后续查找


# 3.求最新的股价、市盈率等
pd_price = ts.pro_bar(ts_code=ts_code, start_date='20200624', end_date='20200624', adj='qfq',
                    factors=['tor', 'vr'])        # 本接口不需要用pro.pro_bar
pd_price.columns = ['交易日期', 'ts_code', '开盘价', '最高价', '最低价', '收盘价', '昨收价', '涨跌额', '涨跌幅 ', '成交量（手）', '成交额（千元）',
                    '换手率', '量比']
pd_basic = pd_stock[pd_stock['ts_code'] == ts_code]
pd_priceStock = pd_price.merge(pd_basic, how='left', on='ts_code')        # 将股票行情表与股票基本表合并

pd_priceStock['市盈率'] = pd_priceStock['收盘价']/pd_plusDate.loc[0, '基本每股收益']
pd_priceStock['市净率'] = pd_priceStock['收盘价']/pd_plusDate.loc[0, '每股净资产']
pd_priceStock['扣非净利润增长率/市盈率'] = pd_plusDate.loc[0, '归属母公司股东的净利润-扣除非经常损益同比增长率(%)'] / pd_priceStock['市盈率']

pd_plusDate.fillna(0, inplace=True)


# 4.打印公司基本信息、市盈率等
print('1.公司基本信息：')
print('股票名称：', pd_plusDate.loc[0, '股票名称'])
print('所属行业：', pd_plusDate.loc[0, '所属行业'])
print('所在地域：', pd_plusDate.loc[0, '所在地域'])
print('上市日期：', pd_plusDate.loc[0, '上市日期'])
print()

print('2.公司最新静态估值数据：')
print('市盈率为：', pd_priceStock.loc[0, '市盈率'])
print('市净率为：', pd_priceStock.loc[0, '市净率'])
print('扣非净利润增长率/市盈率：', pd_priceStock.loc[0, '扣非净利润增长率/市盈率'])
print()

# 5.打印多年财务平均指标
print('3.公司最近%s年的平均财务数据：' % len(list_date))
print('加权平均净资产收益率(%)：', pd_plusDate['加权平均净资产收益率(%)'].mean(), end='    ')
if pd_plusDate['加权平均净资产收益率(%)'].mean() < 15:
    print('-->预警：加权平均净资产收益率(%)小于15!', end='')
print('\n销售商品提供劳务收到的现金/营业收入：', pd_plusDate['销售商品提供劳务收到的现金/营业收入'].mean(), end='    ')
if pd_plusDate['销售商品提供劳务收到的现金/营业收入'].mean() < 1:
    print('-->预警：销售商品提供劳务收到的现金/营业收入小于1!', end='')
print('\n经营活动产生的现金流量净额/经营活动净收益：', pd_plusDate['经营活动产生的现金流量净额/经营活动净收益'].mean(), end='    ')
if pd_plusDate['经营活动产生的现金流量净额/经营活动净收益'].mean() < 1:
    print('-->预警：经营活动产生的现金流量净额/经营活动净收益小于1!', end='')
print('\n扣非净利率(%)：', pd_plusDate['扣非净利率(%)'].mean(), end='    ')
if pd_plusDate['扣非净利率(%)'].mean() < 15:
    print('-->预警：扣非净利率(%)小于15!', end='')
print('\n商誉净资产比：', pd_plusDate['商誉净资产比'].mean(), end='    ')
if pd_plusDate['商誉净资产比'].mean() > 0.5:
    print('-->预警：商誉净资产比大于0.5!', end='')
print('\n存货净资产比：', pd_plusDate['存货净资产比'].mean(), end='    ')
if pd_plusDate['存货净资产比'].mean() > 0.5:
    print('-->预警：存货净资产比大于0.5!', end='')
print('\n应收账款净资产比：', pd_plusDate['应收账款净资产比'].mean(), end='    ')
if pd_plusDate['应收账款净资产比'].mean() > 0.5:
    print('-->预警：应收账款净资产比大于0.5!', end='')
print('\n应收票据净资产比：', pd_plusDate['应收票据净资产比'].mean(), end='    ')
if pd_plusDate['应收票据净资产比'].mean() > 0.5:
    print('-->预警：应收票据净资产比大于0.5!', end='')
print('\n应收账款和应收票据合计占净资产比：', pd_plusDate['应收账款和应收票据合计占净资产比'].mean(), end='    ')
if pd_plusDate['应收账款和应收票据合计占净资产比'].mean() > 0.5:
    print('-->预警：应收账款和应收票据合计占净资产比大于0.5!', end='')
print('\n资产负债率(%)：', pd_plusDate['资产负债率(%)'].mean(), end='    ')
if pd_plusDate['资产负债率(%)'].mean() > 60:
    print('-->预警：资产负债率(%)大于60!', end='')
print('\n流动比率：', pd_plusDate['流动比率'].mean(), end='    ')
if pd_plusDate['流动比率'].mean() < 2:
    print('-->预警：流动比率小于2!', end='')
print('\n速动比率：', pd_plusDate['速动比率'].mean(), end='    ')
if pd_plusDate['速动比率'].mean() < 1:
    print('-->预警：速动比率小于1!', end='')
print('\n营业总收入同比增长率(%)：', pd_plusDate['营业总收入同比增长率(%)'].mean(), end='    ')
if pd_plusDate['营业总收入同比增长率(%)'].mean() < 20:
    print('-->预警：营业总收入同比增长率(%)小于20!', end='')
print('\n归属母公司股东的净利润同比增长率(%)：', pd_plusDate['归属母公司股东的净利润同比增长率(%)'].mean(), end='    ')
if pd_plusDate['归属母公司股东的净利润同比增长率(%)'].mean() < 20:
    print('-->预警：归属母公司股东的净利润同比增长率(%)小于20!', end='')
print('\n归属母公司股东的净利润-扣除非经常损益同比增长率(%)：', pd_plusDate['归属母公司股东的净利润-扣除非经常损益同比增长率(%)'].mean(), end='    ')
if pd_plusDate['归属母公司股东的净利润-扣除非经常损益同比增长率(%)'].mean() < 20:
    print('-->预警：归属母公司股东的净利润-扣除非经常损益同比增长率(%)小于20!', end='')
print()

# 6.获取前十大股东质押数据
print('\n4.前十大股东质押数据：')
TS计算大股东质押率.get_pledgeHolders10(ts_code, '20200331')


# # 5.打印主要指标，如指标不符合设定标准，打印预警信息
# print('公司2019年的财务数据：')
# print('加权平均净资产收益率(%)：', plus3.loc[0, '加权平均净资产收益率(%)'], end='    ')
# if plus3.loc[0, '加权平均净资产收益率(%)'] < 15:
#     print('-->预警：加权平均净资产收益率(%)小于15!', end='')
# print('\n销售商品提供劳务收到的现金/营业收入：', plus3.loc[0, '销售商品提供劳务收到的现金/营业收入'], end='    ')
# if plus3.loc[0, '销售商品提供劳务收到的现金/营业收入'] < 1:
#     print('-->预警：销售商品提供劳务收到的现金/营业收入小于1!', end='')
# print('\n经营活动产生的现金流量净额/经营活动净收益：', plus3.loc[0, '经营活动产生的现金流量净额/经营活动净收益'], end='    ')
# if plus3.loc[0, '经营活动产生的现金流量净额/经营活动净收益'] < 1:
#     print('-->预警：经营活动产生的现金流量净额/经营活动净收益小于1!', end='')
# print('\n扣非净利率(%)：', plus3.loc[0, '扣非净利率(%)'], end='    ')
# if plus3.loc[0, '扣非净利率(%)'] < 15:
#     print('-->预警：扣非净利率(%)小于15!', end='')
# print('\n商誉净资产比：', plus3.loc[0, '商誉净资产比'], end='    ')
# if plus3.loc[0, '商誉净资产比'] > 0.5:
#     print('-->预警：商誉净资产比大于0.5!', end='')
# print('\n存货净资产比：', plus3.loc[0, '存货净资产比'], end='    ')
# if plus3.loc[0, '存货净资产比'] > 0.5:
#     print('-->预警：存货净资产比大于0.5!', end='')
# print('\n应收账款净资产比：', plus3.loc[0, '应收账款净资产比'], end='    ')
# if plus3.loc[0, '应收账款净资产比'] > 0.5:
#     print('-->预警：应收账款净资产比大于0.5!', end='')
# print('\n应收票据净资产比：', plus3.loc[0, '应收票据净资产比'], end='    ')
# if plus3.loc[0, '应收票据净资产比'] > 0.5:
#     print('-->预警：应收票据净资产比大于0.5!', end='')
# print('\n应收账款和应收票据合计占净资产比：', plus3.loc[0, '应收账款和应收票据合计占净资产比'], end='    ')
# if plus3.loc[0, '应收账款和应收票据合计占净资产比'] > 0.5:
#     print('-->预警：应收账款和应收票据合计占净资产比大于0.5!', end='')
# print('\n资产负债率(%)：', plus3.loc[0, '资产负债率(%)'], end='    ')
# if plus3.loc[0, '资产负债率(%)'] > 60:
#     print('-->预警：资产负债率(%)大于60!', end='')
# print('\n流动比率：', plus3.loc[0, '流动比率'], end='    ')
# if plus3.loc[0, '流动比率'] < 2:
#     print('-->预警：流动比率小于2!', end='')
# print('\n速动比率：', plus3.loc[0, '速动比率'], end='    ')
# if plus3.loc[0, '速动比率'] < 1:
#     print('-->预警：速动比率小于1!', end='')
# print('\n营业总收入同比增长率(%)：', plus3.loc[0, '营业总收入同比增长率(%)'], end='    ')
# if plus3.loc[0, '营业总收入同比增长率(%)'] < 20:
#     print('-->预警：营业总收入同比增长率(%)小于20!', end='')
# print('\n归属母公司股东的净利润同比增长率(%)：', plus3.loc[0, '归属母公司股东的净利润同比增长率(%)'], end='    ')
# if plus3.loc[0, '归属母公司股东的净利润同比增长率(%)'] < 20:
#     print('-->预警：归属母公司股东的净利润同比增长率(%)小于20!', end='')
# print('\n归属母公司股东的净利润-扣除非经常损益同比增长率(%)：', plus3.loc[0, '归属母公司股东的净利润-扣除非经常损益同比增长率(%)'], end='    ')
# if plus3.loc[0, '归属母公司股东的净利润-扣除非经常损益同比增长率(%)'] < 20:
#     print('-->预警：归属母公司股东的净利润-扣除非经常损益同比增长率(%)小于20!', end='')
# print()