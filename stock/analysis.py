import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import talib
import empyrical

# 使用pandas读入所有美国股票的信息（资源来自于kaggle）
df = pd.read_csv("all_stocks_5yr.csv")

# 只过滤苹果AAPL的数据
df = df[df.Name == 'AAPL']

# 查看一下，苹果数据的分布情况
print("苹果股价的统计：")
print(df.describe())

# 按照日期列进行排序
df = df.sort_values(by='date')

# 增加一个year列（为了对年进行统计）
df['date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
df['year'] = pd.DatetimeIndex(df['date']).year
df['sma'] = talib.SMA(df.close, 20)

# 写一个对年进行收益率的函数
def calculate_year_profit(df_year):
    """
    年收益率计算 = （年末的close价格 - 年初的价格）/ 年初的close价格
    :param df_year:
    :return:
    """
    end = df_year.iloc[-1].close
    begin = df_year.iloc[0].close
    profit = (end - begin) / begin
    return profit


# 按照年year进行分组，每组（每年）内，进行收益率计算
df_result = df.groupby(by=['year']).apply(calculate_year_profit)


################## 画图表示 ########################

# 画图准备
fig = plt.figure(figsize=(50, 10))
axis = fig.add_subplot(1, 1, 1)
axis.grid()
axis.set_title(f"苹果APPLE报告")
axis.set_xlabel('日期')  # 设置x轴标题
axis.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
axis.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
axis.xaxis.set_tick_params(rotation=45)
axis.set_ylabel(f'价格', color='r')  # 设置Y轴标题

# 把苹果的日期作为x轴，收盘价close作为y周，画出来
handle, = plt.plot(df.date, df.close,color='orange')
handle_sma, = axis.plot(df.date, df.sma, color='#6495ED', linestyle='--', linewidth=1)

plt.legend(handles=[handle,handle_sma],
		   labels=['苹果价格','20日均线'],
		   loc='best')
plt.show()
plt.clf()

# 计算投资收益率
print("-"*80)
print("每年的收益率：")
print(df_result)
print("-"*80)

# 设置日期为索引列
df = df.set_index('date')
# 计算每日收益率（empyrial需要每日收益率）
df['_return'] = df.close.pct_change(periods=1)
# 使用empyrial库计算年化收益率和最大回撤
print("年化收益率： %.2f%%" % (empyrical.annual_return(df._return)*100))
print("最大回测  ： %.2f%%" % (empyrical.max_drawdown(df._return)*100))

# 每日收益率分布
fig, axis = plt.subplots()
axis.set_title(f"苹果AAPL日收益率分布直方图")
axis.set_xlabel('收益率')  # 设置x轴标题
plt.hist(df._return,bins=100)
plt.show()