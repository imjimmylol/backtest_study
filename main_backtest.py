import datetime
import os
from strategies import bbstrategy as bb
from strategies import kd_sim_strategy as sigwf
from custom_feed_data.add_extra_line import *
import backtrader as bt
# pip install matplotlib==3.2.2
import quantstats

data_path = os.path.join(os.getcwd(), "data")

# Instantiate Cerebro engine
cerebro = bt.Cerebro()

# Set data parameters and add to Cerebro
data = GenericCSV_binary_indicator(
    dataname=data_path+'\\TFX_DAILY_withsig_7.csv',
    fromdate=datetime.datetime(2000, 2, 11),
    todate=datetime.datetime(2020, 8, 21),
    # todate=datetime.datetime(2001, 12, 31),
    nullvalue=0.0,
    dtformat=('%Y-%m-%d'),
    tmformat=('%H:%M:%S'),
    datetime=1,
    open=2,
    high=3,
    low=4,
    close=5,
    volume=6,

    binary_sig=13
)

data2 = bt.feeds.YahooFinanceCSVData(
    dataname= data_path+'\\TSLA.csv',
    fromdate=datetime.datetime(2021, 1, 3),
    todate=datetime.datetime(2022, 4, 6),
)


# Run backtest
cerebro.adddata(data)
cerebro.broker.setcash(1000000.0)
# cerebro.addstrategy(sigwf)
cerebro.addstrategy(bb.bb_strategy)
cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
cerebro.addsizer(bt.sizers.FixedSize, stake=5)
results = cerebro.run()
cerebro.plot()


strat = results[0]

# create performance metric
portfolio_stats = strat.analyzers.getbyname('PyFolio')
returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
returns.index = returns.index.tz_convert(None)

quantstats.reports.html(returns, output='stats.html', title='kd_sim_strategy')



