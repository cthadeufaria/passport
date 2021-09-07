# from pandas.core.dtypes import base
# from pandas.core.frame import DataFrame
from scipy.stats.stats import moment
from handle_api import candlestick, tickers_list
import pandas as pd
from scipy.stats import spearmanr
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn import metrics
import math


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


def momentum_quality(data, n=12, p=0.5):
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
    

def momentum_quantity(data, n=12):
    # n = imi period
    # m = investment period
    momentum = {}
    for d in data.keys():
        series = data[d].copy()
        series['gains'] = 0.0
        series['losses'] = 0.0
        series['imi'] = 0.0
        series['return_m'] = 0.0
        series['close'] = pd.to_numeric(series['close'])
        series['open'] = pd.to_numeric(series['open'])
        series['return'] = series['close']-series['open']
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
        momentum[d] = series
    print('quantity series: ' + str(len(momentum)) + ' rows')
    return momentum


def markovitz(data):
    # empty lists to store returns, volatility and weights of imiginary portfolios
    port_returns = []
    port_volatility = []
    stock_weights = []

    # set the number of combinations for imaginary portfolios
    num_assets = len(data)
    num_portfolios = 50000

    # populate the empty lists with each portfolios returns,risk and weights
    for single_portfolio in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, returns_annual)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)

    # a dictionary for Returns and Risk values of each portfolio
    portfolio = {'Returns': port_returns,
                'Volatility': port_volatility}

    # extend original dictionary to accomodate each ticker and weight in the portfolio
    for counter,symbol in enumerate(selected):
        portfolio[symbol+' weight'] = [weight[counter] for weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio)

    # get better labels for desired arrangement of columns
    column_order = ['Returns', 'Volatility'] + [stock+' weight' for stock in selected]

    # reorder dataframe columns
    df = df[column_order]

    df.head()

    plt.style.use('seaborn')
    df.plot.scatter(x='Volatility', y='Returns', figsize=(10, 8), grid=True)
    plt.xlabel('Volatility (Std. Deviation)')
    plt.ylabel('Expected Returns')
    plt.title('Efficient Frontier')
    plt.show()


def portfolio_allocation():
    pass


def pnl():
    pass


def test_momentum(data={'BNBBTC' : pd.read_csv('/home/carlos/Documents/BTC_data/BNBBTC.csv')}):
    cols = [
        'Asset', 'Pearsonr correlation', 'Spearmanr correlation', 
        'Pearsonr correlation (0.7 <= x <= 0.3)', 'Spearmanr correlation (0.7 <= x <= 0.3)', 
        'cnf_matrix', 'Log Accuracy', 'Log Precision', 'Log Recall'
    ]
    # results = pd.DataFrame(None, columns=cols)
    for n in range(1, 25):
        for m in range(1, 25):
            results = pd.DataFrame(None, columns=cols)
            for d in data.keys():
                series = data[d]
                # n = 24 # imi period
                # m = 12 # investment period
                series['gains'] = 0.0
                series['losses'] = 0.0
                series['imi'] = 0.0
                series['return_m'] = 0.0
                series['close'] = pd.to_numeric(series['close'])
                series['open'] = pd.to_numeric(series['open'])
                series['return'] = series['close']-series['open']
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
                        if i+m-1 >= len(series):
                            pass
                        else:
                            series['return_m'][i] = (series['close'][i+m-1]-series['open'][i])/series['open'][i]
                # series.to_csv('/home/carlos/Documents/BTC_data/BNBBTC_2.csv')

                corr, _ = pearsonr(series['imi'][n:len(series)-m], series['return_m'][n:len(series)-m])
                print('Pearsonr correlation: %.3f' % corr)
                corr2, _ = spearmanr(series['imi'][n:len(series)-m], series['return_m'][n:len(series)-m])
                print('Spearmanr correlation: %.3f' % corr2)

                # plt.plot(series['open_datetime'][n:len(series)-m], series['return_m'][n:len(series)-m], 'r')
                # plt.plot(series['open_datetime'][n:len(series)-m], series['imi'][n:len(series)-m], 'b')
                # plt.show()

                series_b = series[((series['imi']<=0.3) | (series['imi']>=0.7)) & (series['gains']!=0)].copy()
                if len(series_b) == 0:
                    corr_b = 0
                    corr2_b = 0
                else:
                    corr_b, _ = pearsonr(series_b['imi'], series_b['return_m'])
                    print('Pearsonr correlation (0.7 <= x <= 0.3): %.3f' % corr_b)
                    corr2_b, _ = spearmanr(series_b['imi'], series_b['return_m'])
                    print('Spearmanr correlation (0.7 <= x <= 0.3): %.3f' % corr2_b)

                # Logistics Regression
                series['return_m'] = np.where(series['return_m']>=0, 1, 0)
                X_train, X_test, y_train, y_test = train_test_split(series['imi'], series['return_m'], test_size=0.25, random_state=0)
                logreg = LogisticRegression()
                logreg.fit(np.array(X_train).reshape(-1, 1),y_train)
                y_pred=logreg.predict(np.array(X_test).reshape(-1, 1))
                cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
                print('cnf_matrix')
                print(cnf_matrix)
                print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
                print("Precision:",metrics.precision_score(y_test, y_pred))
                print("Recall:",metrics.recall_score(y_test, y_pred))

                corr_data = [
                    d, corr, corr2, corr_b, corr2_b, str(cnf_matrix), 
                    metrics.accuracy_score(y_test, y_pred), 
                    metrics.precision_score(y_test, y_pred), 
                    metrics.recall_score(y_test, y_pred)
                ]
                partial_result = dict(zip(cols, corr_data))
                results = results.append(pd.DataFrame(partial_result, index=[len(results)]))
                print(results)
            results.to_csv('/home/carlos/Documents/Results/results' + str(n) + '_' + str(m) + '.csv')

# data=candlestick(tickers_list(market='BTC'))
# data={'BNBBTC' : pd.read_csv('/home/carlos/Documents/BTC_data/BNBBTC.csv')}
d = momentum_quantity(momentum_quality(beta(liquidity(candlestick(tickers_list(market='BTC'))))))
# test_momentum(data)

# plot_acf(s)
# plt.show()
# plot_pacf(s)
# plt.show()
