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


# 方法1：循环获取单只股票行情
def get_price(tscode, retry_count=3, pause=2):
    '''
    获取每只股票的价格
    ---------
    retry_count:重试次数
    pause:暂停秒数
    '''

    number = 0
    while number <= retry_count:
        try:
            pd_temp = ts.pro_bar(ts_code=tscode, start_date='20200529', end_date='20200529', adj='qfq',
                                 factors=['tor', 'vr'])       # 本接口不需要用pro.pro_bar
        except:
            number += 1
            if number <= retry_count:
                time.sleep(pause)
            else:
                print('自动重试次数超限，未能获取到ts_code代码为%s的股票的价格' % tscode)
        else:
            return pd_temp


# 方法2：循环获取单只股票行情
# def get_price(tscode, retry_count=3, pause=2):
#     '''
#     获取每只股票的价格
#     ---------
#     retry_count:重试次数
#     pause:暂停秒数
#     '''
#
#     for number in range(retry_count):
#         try:
#             pd_temp = ts.pro_bar(ts_code=tscode, start_date='20200522', end_date='20200522', adj='qfq',
#                                  factors=['tor', 'vr'])             # 本接口不需要用pro.pro_bar
#         except:
#             time.sleep(pause)
#         else:
#             return pd_temp
#     print('自动重试次数超限，未能获取到ts_code代码为%s的股票的价格' % tscode)


stock_pd = TS_getStock.get_stock()      # 获取股票列表
stock_price = pd.DataFrame()         # 创建空dataframe，用于存放所有股票的价格

for i in stock_pd['ts_code'].values:        # 遍历每只股票的ts_code
    stock_singlePri = get_price(i)       # 获取该只股票的价格
    stock_price = stock_price.append(stock_singlePri)      # 将该只股票的价格放到汇总dataframe中
    # time.sleep(0.75)

stock_price.columns = ['交易日期', 'ts_code', '开盘价', '最高价', '最低价', '收盘价', '昨收价', '涨跌额', '涨跌幅 ', '成交量（手）', '成交额（千元）',
                       '换手率', '量比']
stock_price.to_csv('D:\\股票分析\\沪深股票价格20200529.csv')


