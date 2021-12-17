import time
from handle_api import order_book, candlestick

class Portfolio:


    def __init__(self, portfolioId, description, asset):
        self.portfolioId = portfolioId
        self.description = description
        self.asset = asset
    
    
    def getOrderBook(self):
        self.orderBook = order_book(self.asset)


    def getClosePrice(self):
        self.priceHistory = candlestick(self.asset) # select best interval (1h?)


time.sleep(3)

# info:
    # main asset: 
        # bid prices (order_book)
        # ask prices (order_book)
        # close price history (candlestick)
    # asset's option:
        # bid prices
        # ask prices
        # strike price
        # time to maturity
    # general
        # risk free interest rate:
            # 
            # 

 # methods (?):
    # Black and Scholes (implicit volatility):
        # 1. option's bid or ask price
        # 2. strike price
        # 3. time to maturity
        # 4. daily risk-free interest rate
        # 5. asset's price (average between ask and bid price at the moment of implicit volatility calculation)

    # EWMA (exponential decay = 0.94)
        # 1. asset's closing price history until one day before
        # 2. asset's price (average between ask and bid price at the moment of implicit volatility calculation)
