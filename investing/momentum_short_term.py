# from pandas.core.dtypes import base
# from pandas.core.frame import DataFrame
from handle_api import candlestick, tickers_list, order_book
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import math
from analysis import test_momentum
import time
import pickle


# Portfolio 1 - Markovitz Intraday Momentum:
# Remove less liquid assets (smallest average trading volume) (ok)
# Remove highest betas assets (ok)
# Remove low momentum - Choose assets based on momentum quality (smoothest price path / frog in the pan)
    # Calculate intraday momentum (check for evidence)
    # Check for most relevant period to calculate momentum to predict return in x next hours (use correlation between imi and predicted return to look for best period)
        # Momentum indexes:
            # IMI
            # RSI
            # EMA
            # SMA
# Use Markovitz to define proportions of assets in portfolio
    # how to estimate volatility? GARCH?
    # how to estimate return? EWMA?

# Portfolio 1.1 - Markovitz Long Term Momentum
    # Identify universe (sample_space)
    # Remove outliers (beta) (momentum_outliers)
    # Momentum screen
    # Momentum quality
    # Invest with conviction (?)

# Portfolio 2 - Highest Daily Gainers Chasing:
# Test highest gainers on last 24h for momentum predictability

########################################################################################################

def sample_space(tickers):
    # Filter largest assets
    # Exclude assets with less than 12 months of return data
    # Eliminate less liquid assets based on average daily volume
    pass


def momentum_outliers():
    # Remove assets with bad 6 and 9-month momentum measure
    pass


def momentum_quantity(data, n=20, key='last', cut=0.5):
    # key = 'last' => calculate last imi's / key = 'all' => calculate all imi's
    # n = imi period
    # m = investment period
    momentum = {}
    momentum_filter = {}
    for d in data.keys():
        series = data[d].copy()
        series['close'] = pd.to_numeric(series['close'])
        series['open'] = pd.to_numeric(series['open'])
        series['return'] = series['close']-series['open']
        if key == 'all':
            series['gains'] = 0.0
            series['losses'] = 0.0
            series['imi'] = 0.0
            series['return_m'] = 0.0
            for i in series.index:
                if i < n:
                    pass
                else:
                    series['gains'][i] = series['return'][i-n:i][series['return']>=0].sum()
                    series['losses'][i] = series['return'][i-n:i][series['return']<0].sum()
                    if series['gains'][i]-series['losses'][i] == 0:
                        series['imi'][i] = 0.5
                    else:
                        series['imi'][i] = series['gains'][i]/(series['gains'][i]-series['losses'][i])
                    # if i+m-1 >= len(series):
                    #     pass
                    # else:
                    #     series['return_m'][i] = (series['close'][i+m-1]-series['open'][i])/series['open'][i]
        elif key == 'last':
            i = series.index.max()
            gains = series['return'][i-n:i][series['return']>=0].sum()
            losses = series['return'][i-n:i][series['return']<0].sum()
            if gains-losses == 0:
                pass
            elif gains/(gains-losses)<=cut:
                momentum_filter[d] = gains/(gains-losses)
            else:
                pass
        momentum[d] = series
    if key == 'last':
        momentum = {k:v for k,v in momentum.items() if (pd.Series(momentum_filter.keys()) == k).any()}
    print('quantity series: ' + str(len(momentum)) + ' rows')
    return momentum


def liquidity(data, p=0.7, cut=10000.0):
    volume = {}
    print('input data: ' + str(len(data)) + ' rows')
    for d in data.keys():
        # volume[d] = pd.to_numeric(data[d]['volume']).mean()
        volume[d] = pd.to_numeric(data[d]['volume']).mean()
    # volume = dict(sorted(volume.items(), key=lambda x: x[1], reverse=True))
    # volume = dict(list(volume.items())[:math.ceil(len(volume)*p)])
    volume = {k:v for k,v in volume.items() if v >= cut}
    series = {}
    series = {k:v for k,v in data.items() if (pd.Series(volume.keys()) == k).any()}
    print('liquidity series: ' + str(len(series)) + ' rows')
    return series

        
def beta(data, market, base_asset, p=0.7, cut=0.5):
    # Eliminate 10% of highest betas (What's the cryptocurrencies' market index?)
    # market = candlestick(base_asset)[base_asset]
    market_delta = pd.DataFrame(
        data=(pd.to_numeric(market['close'])-pd.to_numeric(market['open']))/pd.to_numeric(market['open']),
        columns=[base_asset]
    ).set_index(market['open_datetime'])
    df = pd.DataFrame()
    for s in data.keys():
        if len(df) == 0:
            df = pd.DataFrame(
                    data=(pd.to_numeric(data[s]['close'])-pd.to_numeric(data[s]['open']))/pd.to_numeric(data[s]['open']),
                    columns=[s]
                ).set_index(data[s]['open_datetime'])
        else:
            df = df.join(
                pd.DataFrame(
                    data=(pd.to_numeric(data[s]['close'])-pd.to_numeric(data[s]['open']))/pd.to_numeric(data[s]['open']),
                    columns=[s]
                ).set_index(data[s]['open_datetime']),
                how='left'
            )
    df.dropna(axis=1, inplace=True)
    df = df.join(market_delta, how ='left')
    df.dropna(inplace=True)
    
    beta = {}
    for c in df.columns:
        # Create arrays for x and y variables in the regression model
        x = np.array(df[c]).reshape((-1,1))
        y = np.array(df[base_asset])
        # Define the model and type of regression
        model = LinearRegression().fit(x, y)
        beta[c] = (model.coef_[0])
        print(str(c)+'s beta = '+str(model.coef_[0]))

    # beta = dict(sorted(beta.items(), key=lambda x: x[1]))
    # beta = dict(list(beta.items())[:math.ceil(len(beta)*p)])
    beta = {k:v for k,v in beta.items() if v<=cut}

    series = {}
    for (key, value) in data.items():
        if key in beta.keys():
            series[key] = value
    print('beta series: ' + str(len(series)) + ' rows')
    return series


def momentum_quality(data, n=20, p=0.5, cut=0):
    # ID = sign(PRET) * (% months negative - % months positive)
    # -1 <= ID <= 1
    # -1 = high quality momentum / 1 = bad quality momentum
    quality = {}
    for d in data.keys():
        data[d]['return'] = pd.to_numeric(data[d]['close'])-pd.to_numeric(data[d]['open'])
        data[d]['return_n'] = pd.to_numeric(data[d]['close'])-pd.to_numeric(data[d]['open']).shift(n-1)
        data[d]['return_n'][data[d]['return_n'] >= 0] = 1
        data[d]['return_n'][data[d]['return_n'] < 0] = -1
        data[d]['n_neg'] = 0.0
        data[d]['n_pos'] = 0.0
        for l in range(0, len(data[d])):
            if l < (n-1):
                pass
            else:
                for i in range(0, n):
                    if data[d]['return'][l-i] < 0:
                        data[d]['n_neg'][l] += 1
                    else:
                        data[d]['n_pos'][l] += 1
        quality[d] = (float(data[d]['return_n'][-1:]))*((float(data[d]['n_neg'][-1:])/12)-(float(data[d]['n_pos'][-1:])/12))
    
    quality = dict(sorted(quality.items(), key=lambda x: x[1]))
    # quality = dict(list(quality.items())[:math.ceil(len(quality)*p)])
    quality = {k:v for k,v in quality.items() if v<=cut}

    series = {}
    for (key, value) in data.items():
        if key in quality.keys():
            series[key] = value
    print('quality series: ' + str(len(series)) + ' rows')
    return series


def markovitz(data):
    ####################################################################################################################################################################################
    # get adjusted closing prices of 5 selected companies with Quandl
    # quandl.ApiConfig.api_key = '3QMrpN426duegrHv6o4v'
    # selected = ['CNP', 'F', 'WMT', 'GE', 'TSLA']
    # data = quandl.get_table('WIKI/PRICES', ticker = selected,
    #                         qopts = { 'columns': ['date', 'ticker', 'adj_close'] },
    #                         date = { 'gte': '2014-1-1', 'lte': '2016-12-31' }, paginate=True)

    # reorganise data pulled by setting date as index with
    # columns of tickers and their corresponding adjusted prices
    # clean = data.set_index('date')
    # table = clean.pivot(columns='ticker')
    ####################################################################################################################################################################################
    
    selected = list(data.keys())
    table = pd.DataFrame(None)
    for ticker in selected:
        t = data[ticker][['open_datetime', 'close']]
        t.set_index('open_datetime', inplace=True)
        t.columns = [ticker]

        if len(table) == 0:
            table = t.copy()
        else:
            table = t.join(table)

    table.dropna(axis=1, inplace=True)

    # calculate daily and annual returns of the stocks
    returns_daily = table.pct_change()
    returns_annual = returns_daily.mean() * 250

    # get daily and covariance of returns of the stock
    cov_daily = returns_daily.cov()
    cov_annual = cov_daily * 250

    # empty lists to store returns, volatility and weights of imiginary portfolios
    port_returns = []
    port_volatility = []
    sharpe_ratio = []
    stock_weights = []

    # set the number of combinations for imaginary portfolios
    num_assets = len(table.columns)
    num_portfolios = 50000

    #set random seed for reproduction's sake
    np.random.seed(101)

    # populate the empty lists with each portfolios returns,risk and weights
    for single_portfolio in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, returns_annual)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
        sharpe = returns / volatility
        sharpe_ratio.append(sharpe)
        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)

    # a dictionary for Returns and Risk values of each portfolio
    portfolio = {'Returns': port_returns,
                'Volatility': port_volatility,
                'Sharpe Ratio': sharpe_ratio}

    # extend original dictionary to accomodate each ticker and weight in the portfolio
    for counter,symbol in enumerate(table.columns):
        portfolio[symbol] = [Weight[counter] for Weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio)

    # get better labels for desired arrangement of columns
    column_order = ['Returns', 'Volatility', 'Sharpe Ratio'] + [stock for stock in table.columns]

    # reorder dataframe columns
    df = df[column_order]

    # find min Volatility & max sharpe values in the dataframe (df)
    min_volatility = df['Volatility'].min()
    max_sharpe = df['Sharpe Ratio'].max()

    # use the min, max values to locate and create the two special portfolios
    sharpe_portfolio = df.loc[df['Sharpe Ratio'] == max_sharpe]
    min_variance_port = df.loc[df['Volatility'] == min_volatility]

    plt.style.use('seaborn-dark')
    df.plot.scatter(x='Volatility', y='Returns', c='Sharpe Ratio',
                    cmap='RdYlGn', edgecolors='black', figsize=(10, 8), grid=True)
    plt.scatter(x=sharpe_portfolio['Volatility'], y=sharpe_portfolio['Returns'], c='red', marker='D', s=200)
    plt.scatter(x=min_variance_port['Volatility'], y=min_variance_port['Returns'], c='blue', marker='D', s=200 )
    plt.xlabel('Volatility (Std. Deviation)')
    plt.ylabel('Expected Returns')
    plt.title('Efficient Frontier')
    # plt.show()
    plt.savefig('foo.png')

    print(min_variance_port.T)
    print(sharpe_portfolio.T)

    return min_variance_port, sharpe_portfolio


def portfolio_allocation():
    pass


def pnl():
    pass


def run_strategy(market='BTC'): # daily strategy. tests gone bad. do not use!
    # 0. full assets data from api:
    t = tickers_list(market) # (!) ignorado para rodar mais rápido com dados salvos
    # t1 = t.copy()
    # base_asset = 'BTCUSDT'
    # t.append(base_asset)

    d = candlestick(t)
    now = pd.Timestamp.utcnow().strftime("%Y-%m-%d, %H")
    d = {k:v for k,v in d.items() if (pd.to_datetime(v['open_datetime'][-1:], unit='ms').dt.strftime("%Y-%m-%d, %H") == now).any()}
    # d1 = d[base_asset]
    # d2 = {k:v for k,v in d.items() if k in t1}
    # with open('d.pickle', 'rb') as handle: # (!) usado pra rodar mais rápido com dados salvos
    #     d = pickle.load(handle)

    # 1. run regressions and save clean_results:
    test_momentum(d) # (!) ignorar pra rodar mais rápido com dados salvos

    # 1.1. import clean_results (logistics regression's precision greater than 0.7):
    clean_results = pd.read_csv('/home/carlos/Documents/Results/clean_results.csv')

    # 1.2. create new dict from d filtering assets from clean_results:
    clean_data = {k:v for k,v in d.items() if (clean_results['Asset'] == k).any()}

    # 2. build portfolio:
    # 2.1. calculate and filter most relevant imi's:
    a = momentum_quantity(clean_data)

    # 2.2. filter assets by liquidity:
    b = liquidity(a)

    # 2.3. filter betas:
    # c = beta(data=b, market=d1, base_asset=base_asset)

    # 2.4. filter momentum quality:
    # d = momentum_quality(c)

    # 2.5. alocate portfolio proportions with Markovitz:
    e, f = markovitz(b)

    f = f[f.columns[3:]]

    portfolio_n=1
    test_results = {}
    sub_results = {}
    price_bop = {}
    price_eop = {}
    proportion = {}

    # save dict with: real time / asset last close time / price of each asset / number of portfolio / proportion of each asset + asset (f)
    while portfolio_n <= 24:
        # price = order_book['YOYOBTC']['bids'][1][1]
        start_time = pd.Timestamp.utcnow()

        portfolio = f
        for c in portfolio.columns:
            proportion[c] = portfolio[c][portfolio.index[0]]
        
        asks = order_book(proportion.keys())
        for k in asks.keys():
            price_bop[k] = asks[k]['asks'][0][0]

        buy_time = pd.Timestamp.utcnow()

        time_spam = 3600 - (buy_time.timestamp()-start_time.timestamp())

        time.sleep(time_spam)

        bids = order_book(proportion.keys())
        for k in bids.keys():
            price_eop[k] = bids[k]['bids'][0][0]

        sell_time = pd.Timestamp.utcnow()

        sub_results['start_time'] = start_time
        sub_results['buy_time'] = buy_time
        sub_results['sell_time'] = sell_time
        sub_results['price_bop'] = price_bop.copy()
        sub_results['price_eop'] = price_eop.copy()
        sub_results['proportion'] = proportion.copy()

        test_results[portfolio_n] = sub_results.copy()
        print(test_results)

        portfolio_n+=1

        with open('test_results.pickle', 'wb') as handle:
            pickle.dump(test_results, handle, protocol=pickle.HIGHEST_PROTOCOL)

