import time
import pandas as pd
from datetime import datetime, timedelta
from handle_api import order_book, candlestick, options_info, markPrice

class Portfolio:


    def __init__(self, portfolioId, description, asset):
        # Initial parameters:
        self.portfolioId = portfolioId
        self.description = description
        self.asset = asset


    def getInfo(self):
        # Quote asset's info:
        self.assetPriceHistory = candlestick(tickers=[self.asset], interval='1m')
        self.assetOrderBook = order_book([self.asset], key=0)
        print('Asset\'s info complete')

        # Option's info:
        # Find options' trading pairs based on specified criteria:
        optionsInfo = list()
        optionsListFrontMonth = list()
        # optionsListBackMonth = list()
        data = options_info()
        a = datetime.today() + timedelta(weeks=2)
        # b = datetime.today() + timedelta(weeks=2)

        for i in data['data']:
            expiryDate = pd.to_datetime(i['expiryDate'], unit='ms')
            if expiryDate <= a:
                a = expiryDate
            # if expiryDate >= b:
            #     b = expiryDate
        print('Next expiry date is on ' + str(a))
        # print('Last expiry date is on ' + str(b))

        for i in data['data']:
            if pd.to_datetime(i['expiryDate'], unit='ms') == a and i['side'] == 'CALL':
                optionsInfo.append(i)
                optionsListFrontMonth.append(i['symbol'])
            # if pd.to_datetime(i['expiryDate'], unit='ms') == b:
            #     optionsListBackMonth.append(i['symbol'])
        self.optionsInfo = optionsInfo
        print('Closest expiry date calls gathered')

        # self.optionOrderBook = order_book(optionsListFrontMonth, key=1)

        # Options' implied volatility (IV)
        self.impliedVolatility = markPrice(optionsListFrontMonth)
        # priceBackMonthList = markPrice(optionsListBackMonth)
        print('Option\'s implied volatility gathered')
        print('Option\'s info complete')


    def ewma(self):
        ewmaData = pd.DataFrame(data=self.assetPriceHistory[list(self.assetPriceHistory.keys())[0]]['close'])
        ewmaData.columns = [list(self.assetPriceHistory.keys())[0]]

        priceAverage = (
            pd.to_numeric(self.assetOrderBook[list(self.assetPriceHistory.keys())[0]]['asks'][0][0]) +
            pd.to_numeric(self.assetOrderBook[list(self.assetPriceHistory.keys())[0]]['bids'][0][0])
        )/2

        newRow = {list(self.assetPriceHistory.keys())[0] : priceAverage}

        ewmaData = ewmaData.append(newRow, ignore_index=True)
        ewmaData[list(self.assetPriceHistory.keys())[0]] = pd.to_numeric(ewmaData[list(self.assetPriceHistory.keys())[0]])
        ewmaData = ewmaData.pct_change()
        ewmaData = ewmaData.ewm(alpha=0.94).mean()
        
        self.assetVolatility = ewmaData.iloc[-1][0]


time.sleep(3)

# test class:
portfolio = Portfolio(0, 'BTC options arbitrage', 'BTCUSDT')
portfolio.getInfo()
portfolio.ewma()


# EWMA (exponential decay = 0.94)
    # 1. asset's closing price history until one period before
    # 2. asset's price (average between ask and bid price at the moment of implicit volatility calculation)
