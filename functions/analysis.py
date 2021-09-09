# Python file for strategies' analysis and testing.
import pandas as pd
import os


def momentum_analysis():
    final_path = '/home/carlos/Documents/Test_Results'
    path = '/home/carlos/Documents/Results'
    list = os.listdir(path)
    number_files = len(list)
    results = pd.DataFrame(index=range(1,number_files), columns=['id', 'Pearsonr correlation', 'Spearmanr correlation', 'Pearsonr correlation (0.7 <= x <= 0.3)', 'Spearmanr correlation (0.7 <= x <= 0.3)', 'Log Accuracy', 'Log Precision', 'Log Recall'])

    i = 1
    for n in range(1, 19):
        for m in range(1,25):
            number = str(n) + '_' + str(m)
            data = path + '/results' + number + '.csv'
            df = pd.read_csv(data)

            results['id'][i] = number
            results['Pearsonr correlation'][i] = df['Pearsonr correlation'].mean()
            results['Spearmanr correlation'][i] = df['Spearmanr correlation'].mean()
            results['Pearsonr correlation (0.7 <= x <= 0.3)'][i] = df['Pearsonr correlation (0.7 <= x <= 0.3)'].mean()
            results['Spearmanr correlation (0.7 <= x <= 0.3)'][i] = df['Spearmanr correlation (0.7 <= x <= 0.3)'].mean()
            results['Log Accuracy'][i] = df['Log Accuracy'].mean()
            results['Log Precision'][i] = df['Log Precision'].mean()
            results['Log Recall'][i] = df['Log Recall'].mean()

            i += 1

    results.to_csv(final_path + '/momentum_analysis.csv')


def markovitz_model(data):
    # import needed modules
    # import quandl
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

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
    stock_weights = []

    # set the number of combinations for imaginary portfolios
    num_assets = len(selected)
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
        portfolio[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio)

    # get better labels for desired arrangement of columns
    column_order = ['Returns', 'Volatility'] + [stock+' Weight' for stock in selected]

    # reorder dataframe columns
    df = df[column_order]

    # plot the efficient frontier with a scatter plot
    plt.style.use('seaborn')
    df.plot.scatter(x='Volatility', y='Returns', figsize=(10, 8), grid=True)
    plt.xlabel('Volatility (Std. Deviation)')
    plt.ylabel('Expected Returns')
    plt.title('Efficient Frontier')
    plt.show()