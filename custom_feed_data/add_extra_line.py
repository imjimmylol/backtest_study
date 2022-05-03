from backtrader.feeds import GenericCSVData
import backtrader as bt

class GenericCSV_binary_indicator(GenericCSVData):

    # 说明列名是pe
    lines = ('binary_sig',)
    # 定义pe所在的csv文件列位置，在第8列，即配置为9
    params = (('binary_sig', 0),)