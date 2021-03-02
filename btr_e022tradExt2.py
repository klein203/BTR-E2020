# -*- coding: utf-8 -*-
'''
TopQuant-TQ极宽智能量化回溯分析系统
培训课件系列 2019版

Top极宽量化(原zw量化)，Python量化第一品牌 
by Top极宽·量化开源团队 2019.01.011 首发

网站： www.TopQuant.vip      www.ziwang.com
QQ群: Top极宽量化总群，124134140

'''

import sys;
sys.path.append("topqt/")
#
import matplotlib as mpl
import matplotlib.pyplot as plt

#
import os,time,arrow,math,random,pytz
import datetime  as dt
#
import backtrader as bt
from backtrader.analyzers import SQN, AnnualReturn, TimeReturn, SharpeRatio,TradeAnalyzer

#
import topquant2019 as tq
#   
#----------------------
# 创建一个：最简单的MA均线策略类class
class TQSta001(bt.Strategy):
    # 定义MA均线策略的周期参数变量，默认值是15
    # 增加类一个log打印开关变量： fgPrint，默认自是关闭
    params = (
        ('maperiod', 15),
        ('fgPrint', True),
    )

        
    def log(self, txt, dt=None, fgPrint=False):
        # 增强型log记录函数，带fgPrint打印开关变量
        if self.params.fgPrint or fgPrint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 默认数据，一般使用股票池当中，下标为0的股票，
        # 通常使用close收盘价，作为主要分析数据字段
        self.dataclose = self.datas[0].close

        # 跟踪track交易中的订单（pending orders），成交价格，佣金费用
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # 增加一个均线指标：indicator
        # 注意，参数变量maperiod，主要在这里使用
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 检查订单执行状态order.status：
            # Buy/Sell order submitted/accepted to/by broker 
            # broker经纪人：submitted提交/accepted接受,Buy买单/Sell卖单
            # 正常流程，无需额外操作
            return

        # 检查订单order是否完成
        # 注意: 如果现金不足，经纪人broker会拒绝订单reject order
        # 可以修改相关参数，调整进行空头交易
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行 BUY EXECUTED,成交价： %.2f,小计 Cost: %.2f,佣金 Comm %.2f'  
                         % (order.executed.price,order.executed.value,order.executed.comm), fgPrint=True)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('卖单执行 SELL EXECUTED,成交价： %.2f,小计 Cost: %.2f,佣金 Comm %.2f'  
                         % (order.executed.price,order.executed.value,order.executed.comm), fgPrint=True)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单Order： 取消Canceled/保证金Margin/拒绝Rejected')

        # 检查完成，没有交易中订单（pending order）
        self.order = None

    def notify_trade(self, trade):
        # 检查交易trade是关闭
        if not trade.isclosed:
            return

        self.log('交易操盘利润OPERATION PROFIT, 毛利GROSS %.2f, 净利NET %.2f' %
                 (trade.pnl, trade.pnlcomm)) 
             

    def next(self):
        # next函数是最重要的trade交易（运算分析）函数， 
        # 调用log函数，输出BT回溯过程当中，工作节点数据包BAR，对应的close收盘价
        self.log('当前收盘价Close, %.2f' % self.dataclose[0])
        #
        #
        # 检查订单执行情况，默认每次只能执行一张order订单交易，可以修改相关参数，进行调整
        if self.order:
            return
        #
        # 检查当前股票的仓位position
        if not self.position:
            #
            # 如果该股票仓位为0 ，可以进行BUY买入操作，
            # 这个仓位设置模式，也可以修改相关参数，进行调整
            #
            # 使用最简单的MA均线策略
            if self.dataclose[0] < self.sma[0]:
                # 如果当前close收盘价<当前的ma均价
                # ma均线策略，买入信号成立:
                # BUY, BUY, BUY!!!，买！买！买！使用默认参数交易：数量、佣金等
                self.log('设置买单 BUY CREATE, %.2f, name : %s' % (self.dataclose[0],self.datas[0]._name), fgPrint=True)

                # 采用track模式，设置order订单，回避第二张订单2nd order，连续交易问题
                self.order = self.buy()
                
        else:
            # 如果该股票仓位>0 ，可以进行SELL卖出操作，
            # 这个仓位设置模式，也可以修改相关参数，进行调整
            # 使用最简单的MA均线策略
            if self.dataclose[0] > self.sma[0]:
                # 如果当前close收盘价>当前的ma均价
                # ma均线策略，卖出信号成立:
                # 默认卖出该股票全部数额，使用默认参数交易：数量、佣金等
                self.log('设置卖单 SELL CREATE, %.2f, name : %s' % (self.dataclose[0],self.datas[0]._name), fgPrint=True)

                # 采用track模式，设置order订单，回避第二张订单2nd order，连续交易问题
                self.order = self.sell()        

    def stop(self):
        # 新增加一个stop策略完成函数
        # 用于输出执行后带数据
        self.log('(MA均线周期变量Period= %2d) ，最终资产总值： %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), fgPrint=True)



#----------
        


print('\n#1,设置BT量化回溯程序入口')
cerebro = bt.Cerebro()

#
print('\n#2,设置BT回溯初始参数：起始资金等')
dmoney0=100000.0
cerebro.broker.setcash(dmoney0)
dcash0=cerebro.broker.startingcash

#
#
print('\n\t#2-2,设置数据文件，数据文件，需要按时间字段，正序排序')
rs0='data/stk/'
xcod='002046'
fdat=rs0+xcod+'.csv'
print('\t@数据文件名：',fdat)

# 
print('\t设置数据BT回溯运算：起始时间、结束时间')  
print('\t数据文件,可以是股票期货、外汇黄金、数字货币等交易数据')  
print('\t格式为：标准OHLC格式，可以是日线、分时数据。')  
t0str,t9str='2018-10-01','2018-12-31'
data=tq.pools_get4fn(fdat,t0str,t9str)

#
# 增加一个股票名称变量xcod，可以在策略函数、绘图中使用
cerebro.adddata(data,name=xcod)
#
#
print('\n\t#2-3,添加BT量化回溯程序，对应的策略参数')
print('\n\t# 案例当中，使用的是MA均线策略')
#cerebro.addstrategy(TQSta001,maperiod=5)
cerebro.addstrategy(TQSta001,maperiod=15,fgPrint=False)
#
print('\n\t#2-4,添加broker经纪人佣金，默认为：千一')
cerebro.broker.setcommission(commission=0.001)
#
print('\n\t#2-5,设置每手交易数目为：10，不在使用默认值，默认是：1手')
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

print('\n\t#2-5,设置addanalyzer分析参数')
      
cerebro.addanalyzer(SQN)
#
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'SharpeRatio', legacyannual=True)
cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
#
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')

      
#
print('\n#3,调用BT回溯入口程序，开始执行run量化回溯运算')
results=cerebro.run()

#
print('\n#4,完成BT量化回溯运算')
dval9=cerebro.broker.getvalue()   
dget=dval9-dcash0
kret=dget/dcash0*100
# 最终投资组合价值
print('\t起始资金 Starting Portfolio Value: %.2f' % dcash0)
print('\t资产总值 Final Portfolio Value: %.2f' % dval9)
print('\t利润总额:  %.2f,' % dget)
print('\tROI投资回报率 Return on investment: %.2f %%' % kret)

#
#---------
print('\n#8,analyzer分析BT量化回测数据')
strat =results[0]
anzs=strat.analyzers
#
dsharp=anzs.SharpeRatio.get_analysis()['sharperatio']
trade_info=anzs.TradeAnalyzer.get_analysis()
#
dw=anzs.DW.get_analysis()
max_drowdown_len =dw['max']['len']
max_drowdown =dw['max']['drawdown']
max_drowdown_money =dw['max']['moneydown']
#
print('\t夏普指数SharpeRatio : ',dsharp)
print('\t最大回撤周期 max_drowdown_len : ', max_drowdown_len)
print('\t最大回撤 max_drowdown : ', max_drowdown)
print('\t最大回撤(资金)max_drowdown_money : ', max_drowdown_money)

#---------
#
print('\n#9,绘制BT量化分析图形')
#cerebro.plot(style='line')
#cerebro.plot(style='candle')
cerebro.plot(style='bar')

#---------
#
print('\nzok')
                
 
#--------------------
'''
@maperiod,        val(利润总额)
5,      10.49        
10,     9.52    
15,     7.05
20,     3.70
25,     6.10
30,     -1.97
35,     -1.70
40,     -1.06 
45,     -1.06 
50,     -1.06

'''
