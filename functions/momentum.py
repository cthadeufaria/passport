# from pandas.core.dtypes import base
# from pandas.core.frame import DataFrame
from handle_api import candlestick, tickers_list
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import math
from analysis import test_momentum


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


# Portfolio 2 - Highest Daily Gainers Chasing:
# Test highest gainers on last 24h for momentum predictability

########################################################################################################

# assemble portfolio

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


def liquidity(data, p=0.7):
    volume = {}
    print('input data: ' + str(len(data)) + ' rows')
    for d in data.keys():
        volume[d] = pd.to_numeric(data[d]['volume']).mean()
    volume = dict(sorted(volume.items(), key=lambda x: x[1], reverse=True))
    volume = dict(list(volume.items())[:math.ceil(len(volume)*p)])
    series = {}
    for (key, value) in data.items():
        if key in volume.keys():
            series[key] = value
    print('liquidity series: ' + str(len(series)) + ' rows')
    return series


def beta(data, base_asset='BTCBUSD', p=0.7):
    market = candlestick(base_asset)[base_asset]
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
    df = df.join(market_delta, how ='left').dropna(axis=1)
    beta = {}
    for c in df.columns:
        # Create arrays for x and y variables in the regression model
        x = np.array(df[c]).reshape((-1,1))
        y = np.array(df[base_asset])
        # Define the model and type of regression
        model = LinearRegression().fit(x, y)
        beta[c] = (model.coef_[0])
        print(str(c)+'s beta = '+str(model.coef_[0]))

    beta = dict(sorted(beta.items(), key=lambda x: x[1]))
    beta = dict(list(beta.items())[:math.ceil(len(beta)*p)])

    series = {}
    for (key, value) in data.items():
        if key in beta.keys():
            series[key] = value
    print('beta series: ' + str(len(series)) + ' rows')
    return series


def momentum_quality(data, n=20, p=0.5):
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
    quality = dict(list(quality.items())[:math.ceil(len(quality)*p)])

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
    num_assets = len(selected)
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
    for counter,symbol in enumerate(selected):
        portfolio[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio)

    # get better labels for desired arrangement of columns
    column_order = ['Returns', 'Volatility', 'Sharpe Ratio'] + [stock+' Weight' for stock in selected]

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
    plt.show()
    plt.savefig('foo.png')

    print(min_variance_port.T)
    print(sharpe_portfolio.T)


def portfolio_allocation():
    pass


def pnl():
    pass



# full assets data from api:
d = candlestick(tickers_list())

# run regressions and save clean_results:
# test_momentum(d)

# import clean_results (logistics regression's precision greater than 0.7):
clean_results = pd.read_csv('/home/carlos/Documents/Results/clean_results.csv')

# create new dict from d filtering assets from clean_results:
clean_data = {k:v for k,v in d.items() if (clean_results['Asset'] == k).any()}

# build portfolio:
a = momentum_quantity(clean_data)