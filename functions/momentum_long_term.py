# Portfolio 1 - Intermediate-Term Momentum
    # Identify universe (sample_space) (ok)
    # Remove outliers (beta) (ok) (momentum_outliers) (ok)
    # Momentum screen (momentum_quantity)
    # Momentum quality (momentum_quality)
    # Invest with conviction
        # Find best value assets
        # Define portfolio size

########################################################################################################

from handle_api import tickers_list, candlestick, prices, trades, balances
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import time, datetime


def sample_space(OneYearData, MinimumValue=0.5, MinimumVolume=10000):
    # MinimumValue = Minimum value of asset in USDT / MinimumVolume = Minimum average volume of asset in last 30 days
    # Exclude assets with less than 12 months of return data (ok)
    # Filter largest assets (ok)
    # Eliminate less liquid assets based on average daily volume (ok)

    EnoughReturnData = {k:v for k,v in OneYearData.items() if len(v) == 365}
    print('EnoughReturnData length = ' + str(len(EnoughReturnData)))

    LargestAssets = {k:v for k,v in EnoughReturnData.items() if sum(pd.to_numeric(v['high'][-30:]))/30 >= MinimumValue}
    print('LargestAssets length = ' + str(len(LargestAssets)))

    LiquidAssets = {k:v for k,v in LargestAssets.items() if sum(pd.to_numeric(v['volume'][-30:]))/30 >= MinimumVolume}
    print('LiquidAssets length = ' + str(len(LiquidAssets)))

    return LiquidAssets


def beta(data, base_asset='BTCUSDT', p=0.3):
    # Eliminate assets with abs(beta) greater than 'p' (ok)

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

    beta = {}
    for c in df.columns:
        # Create arrays for x and y variables in the regression model
        x = np.array(df[c]).reshape((-1,1))
        y = np.array(df[base_asset])
        # Define the model and type of regression
        model = LinearRegression().fit(x, y)
        beta[c] = (model.coef_[0])
        print(str(c)+'s beta = '+str(model.coef_[0]))

    beta = {k:v for k,v in beta.items() if abs(v)<=p}

    LowBetaAssets = {k:v for k,v in data.items() if (k == pd.Series(beta.keys())).any()}
    # LowBetaAssets['BTCUSDT'] = data['BTCUSDT']
    # LowBetaAssets['ETHUSDT'] = data['ETHUSDT']
    print('LowBetaAssets length: ' + str(len(LowBetaAssets)) + ' rows')
    
    return LowBetaAssets


def calculate_momentum(data, periods = [180, 270, 360]):
    # Calculate momentum for given time periods
    # periods = periods' list to calculate momentum
    MomentumData = {}
    info = {}
    for k in data.keys():
        for i in periods:
            length = len(data[k]['close'])
            end = length - 7
            beginning = max(end - i, 0)
            info[str(i)] = (pd.to_numeric(data[k]['close'][end]) - pd.to_numeric(data[k]['open'][beginning])) / pd.to_numeric(data[k]['open'][beginning])
        MomentumData[k] = info.copy()
        for i in periods:
            info.pop(str(i))
    
    return MomentumData


def momentum_outliers(data, MomentumData, screen = 0.0, periods = [180, 270]):
    # Remove assets with negative 6 and 9-month momentum measure from data
    MomentumDataNoOutliers = {k:v for k,v in MomentumData.items() if v[str(periods[1])] >= screen and v[str(periods[0])] >= screen}
    
    OutliersRemoved = {k:v for k,v in data.items() if (k == pd.Series(MomentumDataNoOutliers.keys())).any()}

    print('OutliersRemoved length = ' + str(len(OutliersRemoved)) + ' rows')

    return OutliersRemoved, MomentumDataNoOutliers


def momentum_quantity(data, MomentumDataNoOutliers):
    # Select assets with higher 12-month momentum
    # Create DataFrame for storing 12-month momentum data
    dfMomentum = pd.DataFrame(data=None, columns=['asset', 'momentum'], index=range(0, len(MomentumDataNoOutliers)))
    i = 0
    for k in MomentumDataNoOutliers.keys():
        dfMomentum['asset'][i] = k
        dfMomentum['momentum'][i] = MomentumDataNoOutliers[k]['360']
        i+=1
    
    # Filter positive 12-month momentum
    dfMomentum = dfMomentum[dfMomentum['momentum']>1.0]

    CleanData = {k:v for k,v in data.items() if (k == dfMomentum['asset']).any()}

    print('CleanData length = ' + str(len(CleanData)) + ' rows')

    return CleanData


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
        t[ticker] = pd.to_numeric(t[ticker])

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
    plt.show()
    plt.savefig('plots/Markowitz Efficient Frontier.png')

    print(min_variance_port.T)
    print(sharpe_portfolio.T)

    return min_variance_port, sharpe_portfolio


def run_strategy():
    # Get tickers + data from specific market:
    t = tickers_list(market='USDT')
    data = candlestick(tickers=t, limit=365, interval='1d')

    # Screen nº 1:
    a = sample_space(data)

    # Screen nº 2:
    b = beta(a)

    # Screen nº 3:
    c = calculate_momentum(b)
    d, MomentumDataNoOutliers = momentum_outliers(b, c)

    # Screen nº 4:
    e = momentum_quantity(d, MomentumDataNoOutliers)

    # Screen nº5:
    f = momentum_quality(e)
    
    return f


def pnl(portfolio_keys=['00']):
    for key in portfolio_keys:
        portfolio = pd.read_csv('portfolios/' + key + '.csv')

        AllTickers = tickers_list()
        # holding = list(balances().keys())
        holding = list(portfolio['asset'])

        tickers = []
        for i in AllTickers:
            for j in holding:
                if i[0:len(j)] == j and (i[-3:] == 'BRL' or i[-3:] == 'BTC'):
                    tickers.append(i)
        
        TradeHistory = trades(tickers)

        pnl = {}
        for s in TradeHistory:
            price = []
            qty = []
            Time = []
            for v in s:
                if v['isBuyer'] == True:
                    price.append(v['price'])
                    qty.append(v['qty'])
                    Time.append(v['time'])
                    pnl[v['symbol']] = {'price': price, 'qty': qty, 'time': Time,}

        while True:
            Psell = prices()[1]

            print(datetime.datetime.now())
            print('\n')

            for k in pnl.keys():
                pnl[k]['sell'] = Psell[k]

                # sum of quantities times current price
                # sum(pd.to_numeric(pnl['LRCBTC']['qty']))*pd.to_numeric(Psell['LRCBTC'])
                # sum of each buy price times each quantity
                # sum(pd.to_numeric(pnl['LRCBTC']['price'])*pd.to_numeric(pnl['LRCBTC']['qty']))
                pnl[k]['pnl_total'] = \
                    sum(pd.to_numeric(pnl[k]['qty']))*pd.to_numeric(Psell[k]) - \
                    sum(pd.to_numeric(pnl[k]['price'])*pd.to_numeric(pnl[k]['qty']))

                pnl[k]['pnl_percent'] = \
                    ((sum(pd.to_numeric(pnl[k]['qty']))*pd.to_numeric(Psell[k])/ \
                    sum(pd.to_numeric(pnl[k]['price'])*pd.to_numeric(pnl[k]['qty']))) - 1) * 100

                print(
                    k + ': ' + str(round(pnl[k]['pnl_percent'], 2)) + '%'
                )
            
            print('\n\n')

            time.sleep(3)
    

# build_portfolio variables:
#   [0]: build new portfolio
#   [1]: calculate Markowitz for new portfolio
build_portfolio = [0, 0]
if __name__ == "__main__":
    
    if build_portfolio[0] == 1:
        f = run_strategy()
        if build_portfolio[1] == 1:
            g, h = markovitz(f)
    
    pnl()