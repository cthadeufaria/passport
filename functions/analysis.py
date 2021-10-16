# Python file for strategies' analysis and testing.
import pandas as pd
import os
from datetime import datetime
from scipy.stats import spearmanr
from scipy.stats import pearsonr
# from scipy.stats.stats import moment
from handle_api import candlestick, tickers_list
from log_reg import logistic_regression
import pickle


def test_momentum(data={'BNBBTC' : pd.read_csv('/home/carlos/Documents/BTC_data/BNBBTC.csv')}, test=1):
    # 
    cols = [
        'Asset', 'Last IMI', 'Pearsonr correlation', 'Spearmanr correlation', 
        'Pearsonr correlation (0.7 <= x <= 0.3)', 'Spearmanr correlation (0.7 <= x <= 0.3)', 
        'cnf_matrix', 'Log Accuracy', 'Log Precision', 'Log Recall'
    ]
    # results = pd.DataFrame(None, columns=cols)
    for n in range(20, 21):
        for m in range(1, 2):
            results = pd.DataFrame(None, columns=cols)
            for d in data.keys():
                series = data[d]
                # n: imi period
                # m: investment period
                # define needed variables
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

                # corr, _ = pearsonr(series['imi'][n:len(series)-m], series['return_m'][n:len(series)-m])
                corr = 0
                # corr2, _ = spearmanr(series['imi'][n:len(series)-m], series['return_m'][n:len(series)-m])
                corr2 = 0

                # series_b = series[((series['imi']<=0.3) | (series['imi']>=0.7)) & (series['gains']!=0)].copy()
                # if len(series_b) == 0:
                #     corr_b = 0
                #     corr2_b = 0
                # else:
                #     corr_b, _ = pearsonr(series_b['imi'], series_b['return_m'])
                #     corr2_b, _ = spearmanr(series_b['imi'], series_b['return_m'])
                
                corr_b = 0
                corr2_b = 0
                
                # # Logistics Regression
                cnf_matrix, accuracy, precision, recall = logistic_regression(series)
                imi = series['imi'].iloc[-1]

                corr_data = [
                    d, imi, corr, corr2, corr_b, corr2_b, str(cnf_matrix), accuracy, precision, recall
                ]
                partial_result = dict(zip(cols, corr_data))
                results = results.append(pd.DataFrame(partial_result, index=[len(results)]))
                print(results)
            results.to_csv('/home/carlos/Documents/Results/MainResults/results' + str(n) + '_' + str(m) + '.csv')

            clean_results = results[results['Log Precision'] >= 0.7].copy()
            clean_results.to_csv('/home/carlos/Documents/Results/clean_results.csv')

            # return only makes sense if imi period and investment period are a range of size 1 each. For testing a bigger range, assign test=1 (default).
            if test==0:
                return results


def results_analysis():
    today = str(datetime.today())
    final_path = '/home/carlos/Documents/Test_Results'
    path = '/home/carlos/Documents/Results/Results_2'
    list = os.listdir(path)
    number_files = len(list)
    results = pd.DataFrame(index=range(1,number_files), columns=['id', 'Pearsonr correlation', 'Spearmanr correlation', 'Pearsonr correlation (0.7 <= x <= 0.3)', 'Spearmanr correlation (0.7 <= x <= 0.3)', 'Log Accuracy', 'Log Precision', 'Log Recall'])

    i = 1
    for n in range(18, 25):
        for m in range(1,3):
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

    results.to_csv(final_path + '/' + today + ' - momentum_analysis.csv')


def results_analysis_2():
    with open('test_results.pickle', 'rb') as handle:
        data = pickle.load(handle)

    results = pd.DataFrame(columns=['portfolio_n', 'asset', 'price_bop', 'price_eop', 'proportion', 'returns'])
    portfolio_n = []
    asset = []
    price_bop = []
    price_eop = []
    proportion = []
    returns = []

    for i in data.keys():

        n=0
        while n < len(data[i]['price_bop']):
            portfolio_n.append(i)
            n+=1

        for j in data[i]['price_bop'].keys():
            asset.append(j)
            price_bop.append(data[i]['price_bop'][j])
            price_eop.append(data[i]['price_eop'][j])
            proportion.append(data[i]['proportion'][j])

    results['portfolio_n'] = portfolio_n.copy()
    results['asset'] = asset.copy()
    results['price_bop'] = price_bop.copy()
    results['price_eop'] = price_eop.copy()
    results['proportion'] = proportion.copy()

    results.to_csv('results.csv')



results_analysis_2()