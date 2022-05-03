import backtrader as bt

class ouob(bt.Strategy):
    lines = ('binary_sig',)
    params = (('k_score_buy', 20),('k_score_sell', 50), # filter the wave if too high

              ('kdperiod', 14), ('dfast', 3), ('dslow', 3), # KD param

              ('nbar2close_trade', 5), ('stop_profit', 0.06), ('stop_loss', 0.06),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.exeprice = None
        self.buycomm = None
        self.redline = None
        self.blueline = None
        self.signal = self.datas[0].binary_sig
        # Add indicator
        self.kd = bt.indicators.Stochastic(self.datas[0], period=self.params.kdperiod,
                                           period_dfast=self.params.dfast, period_dslow=self.params.dslow)

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

            if self.signal[0] == 1 and self.k < self.params.k_score_buy:

                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()

            elif self.signal[0] == 1 and self.k > self.params.k_score_sell:

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
