# "Does bitcoin and Ethereum offer suitable hedging during Broad Equity drawdowns"
# 1. Get data:
    # S&P 500 index (ok)
        # filter by start of the week (same period as crypto info)
    # bitcoin/USD prices (ok)
    # ethereum/USD prices (ok)
        # convert binance datetime to s&p datetime (ok)

# 2. Calculate drawdowns for S&P 500 index
# 3. Calculate beta for bitcoin and ethereum for S&P 500 index

# I. Study types of hedging


import quandl, datetime
import pandas as pd, pandas_datareader.data as web
from handle_api import candlestick



def import_from_quandl():
    # get adjusted closing prices of 5 selected companies with Quandl
    quandl.ApiConfig.api_key = '3QMrpN426duegrHv6o4v'
    selected = ['CNP', 'F', 'WMT', 'GE', 'TSLA']
    data = quandl.get_table('WIKI/PRICES', ticker = selected,
                            qopts = { 'columns': ['date', 'ticker', 'adj_close'] },
                            date = { 'gte': '2014-1-1', 'lte': '2016-12-31' }, paginate=True)
    # reorganise data pulled by setting date as index with
    # columns of tickers and their corresponding adjusted prices
    clean = data.set_index('date')
    table = clean.pivot(columns='ticker')


def import_from_datareader(assets, start, end, web=web):
    #if you get an error after executing the code, try adding below:
    pd.core.common.is_list_like=pd.api.types.is_list_like
    data=web.DataReader(assets, 'fred', start, end)
    return data


def import_crypto(tickers):
    # Kline/Candlestick chart intervals:
    # 1m/3m/5m/15m/30m/1h/2h/4h/6h/8h/12h/1d/3d/1w/1M
    data=candlestick(tickers=tickers, interval='1w')
    return data



sp=import_from_datareader(assets=['sp500'], start=datetime.datetime(2017, 8, 20), end=datetime.datetime(2021, 10, 3))
crypto=import_crypto(tickers=['BTCUSDT', 'ETHUSDT'])
for c in crypto.keys():
    crypto[c]['close_datetime']=pd.to_datetime(crypto[c]['close_datetime'], unit='ms')
    crypto[c]['open_datetime']=pd.to_datetime(crypto[c]['open_datetime'], unit='ms')