#! usr/bin/env python
import tushare as ts
import pandas as pd

# 从本地读取token
f = open('D:\\股票分析\\token.txt')
token = f.read()

ts.set_token(token)
pro = ts.pro_api()

def get_stock():
    '''获取股票列表'''
    stock_pd = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date,is_hs')
    stock_pd.columns = ['ts_code', '股票代码', '股票名称', '所在地域', '所属行业', '市场类型', '上市日期', '是否沪深港通标的']
    stock_pd = stock_pd.sort_values(by='所属行业', ascending=True)
    # count = stock_pd['所属行业'].value_counts(normalize=False, dropna=False)    # 按行业统计各行业股票的家数
    # kind = set(stock_pd['所属行业'].values)       # 获取行业的种类，集合去重
    stock_pd.to_csv('D:\\股票分析\\沪深股票列表.csv')
    return stock_pd

if __name__ == '__main__':
    get_stock()
