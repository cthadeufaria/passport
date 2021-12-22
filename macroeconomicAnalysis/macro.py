# "Does bitcoin and Ethereum offer suitable hedging during Broad Equity drawdowns"
# 1. Get data:
    # S&P 500 index (ok)
    # bitcoin/USD prices (ok)
    # ethereum/USD prices (ok)
        # convert binance datetime to s&p datetime (ok)

# 2. Calculate 2020 drawdown for S&P 500 index - including beggining and end of drawdown period (ok)
    # 2.1. plot drawdowns graph (ok)
# 3. Calculate beta between bitcoin and ethereum and S&P 500 index in drawdown periods
    # 3.1. Plot correlation (beta) graph


import quandl
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import matplotlib.pyplot as plt
from .. import investing
from sklearn.linear_model import LinearRegression



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
    data=candlestick(tickers=tickers, interval='1d')
    return data


def daily_to_monthly_period(data):
    data_month=data.loc[data.groupby(pd.to_datetime(data.index).to_period('M')).apply(lambda x: x.index.max())]
    data_month.index=pd.to_datetime(data_month.index).to_period('M')
    return data_month


def filter_year(data, year):
    data=data[pd.to_datetime(data.index).year==year]
    return data


def beta(base_asset, quote_asset, plot_name):
    x = np.array(quote_asset).reshape((-1,1))
    y = base_asset
    model = LinearRegression().fit(x, y)
    beta = (model.coef_[0])
    plt.scatter(x, y,color='g')
    plt.plot(x, model.predict(x),color='k')
    plt.title(str(plot_name))
    plt.savefig(folder + str(plot_name) + '.png')
    plt.close()

    return beta



folder = '/home/carlos/Documents/Financial Analysis/2020.10.04 - Does Bitcoin and Ethereum offer suitable hedging during Broad Equity Drawdowns?/'
crypto=import_crypto(tickers=['BTCUSDT', 'ETHUSDT'])
for c in crypto.keys():
    crypto[c]['close_datetime']=pd.to_datetime(crypto[c]['close_datetime'], unit='ms').dt.date
    crypto[c]['close']=crypto[c]['close'].astype('float')

btc=crypto['BTCUSDT'][['close', 'close_datetime']]
eth=crypto['ETHUSDT'][['close', 'close_datetime']]

btc.set_index('close_datetime', inplace=True)
eth.set_index('close_datetime', inplace=True)

sp=import_from_datareader(assets=['sp500'], start=btc.index[0], end=btc.index[-1])

sp.dropna(inplace=True)

sp_month=daily_to_monthly_period(sp)
btc_month=daily_to_monthly_period(btc)
eth_month=daily_to_monthly_period(eth)

data=sp_month.merge(btc_month, left_index=True, right_index=True).merge(eth_month, left_index=True, right_index=True)

sp_filtered=filter_year(sp,2020)

data_filtered=sp_filtered.merge(btc, left_index=True, right_index=True).merge(eth, left_index=True, right_index=True)
data_filtered_pct = data_filtered.pct_change(1)
data_filtered_pct.dropna(inplace=True)

i = np.argmax(np.maximum.accumulate(sp_filtered) - sp_filtered) # end of the period
j = np.argmax(sp_filtered[:i]) # start of period

plt.plot(sp_filtered)
plt.plot([sp_filtered.index[i], sp_filtered.index[j]], [sp_filtered.iloc[i], sp_filtered.iloc[j]], 'o', color='Red', markersize=10)
plt.title('Max. Drawdown')
plt.savefig(folder + 'Max. Drawdown.png')
plt.close()

texts = [
    'Drawdown period from '+str(sp_filtered.index[j].strftime("%Y-%m-%d"))+' to '+str(sp_filtered.index[i].strftime("%Y-%m-%d")),
    'Drawdown value (USD) from '+str(sp_filtered['sp500'].iloc[j])+' to '+str(sp_filtered['sp500'].iloc[i])
]

with open(folder + "Drawdown.txt", "w") as f:
    for text in texts:
        f.write(text)
        f.write('\n')

sp_drawdown = sp_filtered[(sp_filtered.index<=sp_filtered.index[i]) & (sp_filtered.index>=sp_filtered.index[j])]

data_drawdown = sp_drawdown.merge(btc, left_index=True, right_index=True).merge(eth, left_index=True, right_index=True)
data_drawdown_pct = data_drawdown.pct_change(1)
data_drawdown_pct.dropna(inplace=True)

drawdowns = {}

btc_beta_drawdown = beta(data_drawdown_pct['sp500'], data_drawdown_pct['close_x'], 'BTC Beta in Drawdown Period')
drawdowns['BTC Beta in Drawdown Period'] = btc_beta_drawdown

eth_beta_drawdown = beta(data_drawdown_pct['sp500'], data_drawdown_pct['close_y'], 'ETH Beta in Drawdown Period')
drawdowns['ETH Beta in Drawdown Period'] = eth_beta_drawdown    

btc_beta_whole = beta(data_filtered_pct['sp500'], data_filtered_pct['close_x'], 'BTC Beta (year 2020)')
drawdowns['BTC Beta (year 2020)'] = btc_beta_whole

eth_beta_whole = beta(data_filtered_pct['sp500'], data_filtered_pct['close_y'], 'ETH Beta (year 2020)')
drawdowns['ETH Beta (year 2020)'] = eth_beta_whole

pd.DataFrame(data=list(drawdowns.values()), index=list(drawdowns.keys()),columns=['Beta']).to_csv(folder+'Beta.csv')