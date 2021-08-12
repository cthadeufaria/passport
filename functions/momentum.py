from handle_api import candlestick, price_hist, tickers_list
import pandas as pd
from scipy.stats import spearmanr
from scipy.stats import pearsonr


# Remove less liquid assets (smallest average trading volume)
# Remove highest betas assets
# Remove low momentum
    # Calculate intraday momentum (check for evidence)
    # Check for most relevant period to calculate momentum to predict return in 4 next hours (use correlation between imi and predicted return to look for best period?)
        # IMI
        # 
        
# Choose assets based on momentum quality (smoothest price path / frog in the pan)
# Use Markovitz to define proportions of assets in portfolio
    # how to estimate volatility?
    # how to estimate return?


# Get price_hist
# t = tickers_list()
# candlestick(t)

series = pd.read_csv('/home/carlos/Documents/BTC_data/YOYOBTC.csv')

n = 16 # imi period
m = 1 # investment period
series['gains'] = 0.0
series['losses'] = 0.0
series['imi'] = 0.0
series['return_m'] = 0.0
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
series.to_csv('/home/carlos/Documents/BTC_data/BNBBTC_2.csv')

corr, _ = pearsonr(series['imi'][n:len(series)-m], series['return_m'][n:len(series)-m])
print('Pearsonr correlation: %.3f' % corr)
corr2, _ = spearmanr(series['imi'][n:len(series)-m], series['return_m'][n:len(series)-m])
print('Spearmanr correlation: %.3f' % corr2)

# plot_acf(s)
# plt.show()

# plot_pacf(s)
# plt.show()