#! usr/bin/env python
import tushare as ts
import pandas as pd
import TS_getStock
import time

# 从本地读取token
f = open('D:\\股票分析\\token.txt')
token = f.read()

ts.set_token(token)
pro = ts.pro_api()

def get_balance(tscode, retry_count=3, pause=2):
    '''
    获取每只股票的资产负债表信息
    ---------
    retry_count:重试次数
    pause:暂停秒数
    '''

    number = 0
    while number <= retry_count:
        try:
            # pd_temp = pro.balancesheet(ts_code=tscode, period='20191231', fields='ts_code, ann_date, f_ann_date, end_date, report_type, comp_type, total_share,'
            #           'money_cap, trad_asset, notes_receiv, accounts_receiv, oth_receiv, prepayment, div_receiv, int_receiv, inventories, amor_exp,'
            #           'fa_avail_for_sale, htm_invest, lt_eqt_invest, invest_real_estate, time_deposits, oth_assets, fix_assets, cip, const_materials,'
            #           'intan_assets, r_and_d, goodwill, defer_tax_assets, total_assets, total_liab, minority_int, total_hldr_eqy_exc_min_int,'
            #           'total_hldr_eqy_inc_min_int, update_flag', timeout=5)
                      # 不能改变顺序，因为返回的字段是按照接口顺序返回的，不是按照这里，如果改变了顺序，后面更改列名称时，也是按照接口返回的字段顺序改的，会导致与期望的不一致
            pd_temp = pro.balancesheet(ts_code=tscode, start_date='20170331', end_date='20200630', fields=
                                     'ts_code, end_date, report_type, comp_type, total_share,'
                                     'money_cap, trad_asset, notes_receiv, accounts_receiv, oth_receiv, prepayment, inventories,'
                                     'fa_avail_for_sale, htm_invest, lt_eqt_invest, time_deposits,'
                                     'intan_assets, r_and_d, goodwill, total_assets, total_liab, minority_int, total_hldr_eqy_exc_min_int,'
                                     'total_hldr_eqy_inc_min_int, update_flag', timeout=5)

        except:
            number += 1
            if number != retry_count:
                time.sleep(pause)
            else:
                print('自动重试次数超限，未能获取到ts_code代码为%s的股票的资产负债表信息' % tscode)
        else:
            return pd_temp


stock_pd = TS_getStock.get_stock()      # 获取股票列表
stock_balance = pd.DataFrame()         # 创建空dataframe，用于存放所有股票的资产负债表信息

for i in stock_pd['ts_code'].values:        # 遍历每只股票的ts_code
    stock_singleBal = get_balance(i)       # 获取该只股票的资产负债表信息
    stock_balance = stock_balance.append(stock_singleBal)      # 将该只股票的资产负债表信息放到汇总dataframe中
    time.sleep(1)

# 对财务指标股票表进行去重，保留最新记录 (由于上市公司更新财报，会导致同一公司存在多条记录)
stock_balance = stock_balance.drop_duplicates(subset=['ts_code', 'end_date'], keep='last')

stock_balance.columns = ['ts_code', '报告期', '报表类型', '公司类型', '期末总股本',
                      '货币资金', '交易性金融资产', '应收票据', '应收账款', '其他应收款', '预付款项', '存货',
                      '可供出售金融资产', '持有至到期投资', '长期股权投资', '定期存款',
                      '无形资产', '研发支出', '商誉', '资产总计', '负债合计', '少数股东权益', '股东权益合计(不含少数股东权益)', '股东权益合计(含少数股东权益)',
                      '更新标识']

stock_balance.to_csv('D:\\股票分析\\沪深股票资产负债表_2017至2019年.csv')

# 如果获取失败，将失败的股票，单独重新获取，导出为Excel，将新旧Excel相加！