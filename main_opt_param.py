import datetime
import os
from strategies import bbstrategy as bb
from strategies import kd_sim_strategy as sigwf
from custom_feed_data.add_extra_line import *
import backtrader as bt
# pip install matplotlib==3.2.2
import numpy as np

data_path = os.path.join(os.getcwd(), "data")

# Instantiate Cerebro engine
cerebro = bt.Cerebro(optreturn=False)

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




# Add data
cerebro.adddata(data)

cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')

# Add strategy

cerebro.optstrategy(sigwf.ouob, nbar2close_trade=range(2, 6),
                   k_score_buy=range(10, 81, 10),
                    stop_profit=np.linspace(0.01, 0.06, 5),
                    stop_loss=np.linspace(0.01, 0.06, 5))

# Default position size
cerebro.broker.setcash(1000000.0)
cerebro.addsizer(bt.sizers.FixedSize, stake=5)


if __name__ == '__main__':
    optimized_runs = cerebro.run()

    final_results_list = []
    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() - 10000,2)
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            final_results_list.append([
                # ('k_score_buy', 20),('k_score_sell', 60) 參數換了，最佳化記得改
                strategy.params.k_score_buy,
                strategy.params.nbar2close_trade, strategy.params.stop_profit,
                strategy.params.stop_loss,

                PnL, sharpe['sharperatio']])

    sort_by_sharpe = sorted(final_results_list, key=lambda x: x[4],
                             reverse=True)
    for line in sort_by_sharpe[:10]:
        print(line)





