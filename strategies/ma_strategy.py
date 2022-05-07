import backtrader as bt

class ma_strategy(bt.Strategy):

    params = (('ma_pslow', 20), ('ma_pfast', 5),

              ('kd_period', 9), ('dfast', 3), ('dslow',3),

              ('kd_filter_threshold'), 50)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):

        self.dataclose = self.datas[0].close

        # Track order
        self.order = None
        self.exeprice = None
        self.buycomm = None
        self.redline = None
        self.blueline = None

        # add indicator
        self.kd = bt.indicators.Stochastic(self.datas[0], period=14, period_dfast=3, period_dslow=3)

        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.ma_pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.ma_phigh)
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
        self.k, self.d = self.kd.lines.percK[0], self.kd.lines.percD[0]

        if self.order:
            return

        if not self.position:

            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
