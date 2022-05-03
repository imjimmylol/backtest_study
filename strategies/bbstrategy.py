import backtrader as bt

class bb_strategy(bt.Strategy):

    params = (('bbperiod', 20), ('devfactor', 2.0), ('k_score_low', 20), ('k_score_high', 80),

              ('kdperiod', 14), ('dfast', 3), ('dslow',3),

              ('nbar2close_trade', 5),

              ('stop_profit', 0.03), ('stop_loss', 0.02))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.exeprice = None
        self.buycomm = None
        self.redline = None
        self.blueline = None

        # Add indicator
        self.bband = bt.indicators.BollingerBands(self.datas[0], period = self.params.bbperiod)
                                                  # devfactor = self.params.devfatcor)

        self.kd = bt.indicators.Stochastic(self.datas[0], period=14, period_dfast=3, period_dslow=3)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.exeprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # get k d value
        self.k, self.d = self.kd.lines.percK[0], self.kd.lines.percD[0]

        if self.order:
            return

        if not self.position:

            if self.dataclose < self.bband.lines.bot and self.k < self.params.k_score_low:

                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()

            if self.dataclose > self.bband.lines.top and self.d > self.params.k_score_high:

                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

        else:

            if len(self) >= (self.bar_executed + self.params.nbar2close_trade):
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close()

                # 設置停損
            elif self.dataclose < (self.exeprice * (1 - self.params.stop_loss)):
                self.log(f'CLOSE CREATE STOP LOSS{self.dataclose[0]:2f}')
                self.order = self.close()
                # 設停利
            elif self.dataclose > (self.exeprice * (1 + self.params.stop_profit)):
                self.log(f'CLOSE CREATE STOP PROFIT{self.dataclose[0]:2f}')
                self.order = self.close()



