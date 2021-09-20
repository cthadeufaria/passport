# Python file for strategies' analysis and testing.
import pandas as pd, numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from scipy.stats import spearmanr
from scipy.stats import pearsonr
# from scipy.stats.stats import moment
from handle_api import candlestick, tickers_list


def test_momentum(data={'BNBBTC' : pd.read_csv('/home/carlos/Documents/BTC_data/BNBBTC.csv')}):
    # 
    cols = [
        'Asset', 'Pearsonr correlation', 'Spearmanr correlation', 
        'Pearsonr correlation (0.7 <= x <= 0.3)', 'Spearmanr correlation (0.7 <= x <= 0.3)', 
        'cnf_matrix', 'Log Accuracy', 'Log Precision', 'Log Recall'
    ]
    # results = pd.DataFrame(None, columns=cols)
    for n in range(18, 25):
        for m in range(18, 25):
            results = pd.DataFrame(None, columns=cols)
            for d in data.keys():
                series = data[d]
                # n = 24 # imi period
                # m = 12 # investment period
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
                # series.to_csv('/home/carlos/Documents/BTC_data/BNBBTC_2.csv')

                corr, _ = pearsonr(series['imi'][n:len(series)-m], series['return_m'][n:len(series)-m])
                print('Pearsonr correlation: %.3f' % corr)
                corr2, _ = spearmanr(series['imi'][n:len(series)-m], series['return_m'][n:len(series)-m])
                print('Spearmanr correlation: %.3f' % corr2)

                # plt.plot(series['open_datetime'][n:len(series)-m], series['return_m'][n:len(series)-m], 'r')
                # plt.plot(series['open_datetime'][n:len(series)-m], series['imi'][n:len(series)-m], 'b')
                # plt.show()

                # series_b = series[((series['imi']<=0.3) | (series['imi']>=0.7)) & (series['gains']!=0)].copy()
                series_b = series.copy()
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
            results.to_csv('/home/carlos/Documents/Results/Results_2/results' + str(n) + '_' + str(m) + '.csv')



def results_analysis():
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


d = candlestick(tickers_list())