import requests, os, quandl
import pandas as pd
import pandas_datareader.data as web # https://pandas-datareader.readthedocs.io/en/latest/index.html


class Data:


    def __init__(self, source, startDate, endDate, periodicity, tickers):
        self.source = source
        self.startDate = startDate
        self.endDate = endDate
        self.periodicity = periodicity
        
        if type(tickers) != list:
            self.tickers = [tickers]
        else:
            self.tickers = tickers

    
    def getData(self):
        if self.source == 'fred':
            #if you get an error after executing the code, try adding below:
            pd.core.common.is_list_like = pd.api.types.is_list_like
            data = web.DataReader(self.tickers, self.source, self.startDate, self.endDate)
            self.data = data

        if self.source == 'alpha_vantage':
            url = 'https://www.alphavantage.co/query?function=SMA&symbol=XLE&interval=weekly&time_period=10&series_type=open&apikey=' + os.environ['ALPHA_VANTAGE_FREE_API_KEY']
            r = requests.get(url)
            data = r.json()
            print(data)

        if self.source == 'quandl':
            # get adjusted closing prices of 5 selected companies with Quandl
            quandl.ApiConfig.api_key = os.environ['QUANDL_API_KEY']
            selected = ['CNP', 'F', 'WMT', 'GE', 'TSLA']
            data = quandl.get_table('WIKI/PRICES', ticker = selected,
                                    qopts = { 'columns': ['date', 'ticker', 'adj_close'] },
                                    date = { 'gte': '2014-1-1', 'lte': '2016-12-31' }, paginate=True)
            # reorganise data pulled by setting date as index with
            # columns of tickers and their corresponding adjusted prices
            clean = data.set_index('date')
            table = clean.pivot(columns='ticker')


