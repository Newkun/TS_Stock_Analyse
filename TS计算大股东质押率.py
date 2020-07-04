#! usr/bin/env python
import tushare as ts
import pandas as pd

# 从本地读取token
f = open('D:\\股票分析\\token.txt')
token = f.read()

ts.set_token(token)
pro = ts.pro_api()

def get_pledgeHolders10(ts_code, day):
    '''计算前十大股东的质押数据'''
    # 1.获取最近一期的10大股东，并排序
    pd_holdersTop10 = pro.top10_holders(ts_code=ts_code, period=day, timeout=5)
    pd_holdersTop10.columns = ['ts_code', '公告日期', '报告期', '股东名称', '持有数量（股）', '持有比例']
    pd_holdersTop10 = pd_holdersTop10.sort_values(by='持有比例', ascending=False)
    pd_holdersTop10['股东持股量名次'] = list(range(1, (len(pd_holdersTop10) + 1)))

    # 2.获取质押明细
    pd_pledgeDetail = pro.pledge_detail(ts_code=ts_code)
    pd_pledgeDetail.columns = ['ts_code', '公告日期', '股东名称', '质押数量（万股）', '质押开始日期', '质押结束日期', '是否已解押', '解押日期',
                               '质押方', '持股总数（万股）', '质押总数（万股）', '本次质押占总股本比例', '持股总数占总股本比例', '是否回购']
    # print(pd_pledgeDetail)

    # 3.从质押明细中，找出前十个股东的最新一条质押明细（最新一条包含了持股总数、质押总数）
    pd_pledgeHolders10 = pd.DataFrame()
    for holder in pd_holdersTop10['股东名称'].values:
        pd_temp = pd_pledgeDetail[pd_pledgeDetail['股东名称'] == holder]
        if len(pd_temp) > 0:
            pd_temp = pd_temp.iloc[0, :]           # 提示：从dataframe中截取一列或一行的数据时，会自动转化成series，但不影响在dataframe中相加
            # pd_temp = pd.DataFrame([pd_temp.values], columns=pd_temp.index)     # 如series转化成只有一行的dataframe，则index变为0
            pd_pledgeHolders10 = pd_pledgeHolders10.append(pd_temp)

    if len(pd_pledgeHolders10) > 0:
        # 清除最新一条质押明细中最新质押总数为0的数据
        pd_pledgeHolders10 = pd_pledgeHolders10[pd_pledgeHolders10['质押总数（万股）'] > 0]

        if len(pd_pledgeHolders10) > 0:
            # 4.将股东持股量名次并入
            pd_holdersTop10_simple = pd_holdersTop10.loc[:, ['股东名称', '股东持股量名次']]
            pd_pledgeHolders10 = pd_pledgeHolders10.merge(pd_holdersTop10_simple, how='left', on='股东名称')

            # 5.计算前十大股东的合计质押比率、每人质押比率
            pd_pledgeHolders10['质押比率(%)'] = pd_pledgeHolders10['质押总数（万股）']/pd_pledgeHolders10['持股总数（万股）']*100
            # print(pd_pledgeHolders10)

            # 打印合计质押比率
            sum_pledge = pd_pledgeHolders10['质押总数（万股）'].sum()
            sum_holding = pd_pledgeHolders10['持股总数（万股）'].sum()
            sum_pledgeHolders10 = sum_pledge/sum_holding*100
            print('存在质押股份的前十大股东中，整体质押率(%)为：', sum_pledgeHolders10, end='    ')
            if sum_pledgeHolders10 > 25:
                print('-->预警：整体质押率(%)大于25!', end='')

            # 打印每个股东的质押比率
            for number in range(len(pd_pledgeHolders10)):
                print('\n第%s大股东%s的质押率为：%s' % (pd_pledgeHolders10.loc[number, '股东持股量名次'], pd_pledgeHolders10.loc[number, '股东名称'],
                                          pd_pledgeHolders10.loc[number, '质押比率(%)']), end='    ')
                if pd_pledgeHolders10.loc[number, '质押比率(%)'] > 25:
                    print('-->预警：该股东累计质押率(%)大于25!', end='')

            return sum_pledgeHolders10