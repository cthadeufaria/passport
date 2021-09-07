import pandas as pd
import plotly.graph_objects as go
import requests, time, hmac, hashlib
import pprint # used for debugging
from urllib.parse import urlencode
from initialize import initialize
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

endpoints = initialize('prod')[0]
auth_dict = initialize('prod')[1]


def binance_data(): # used for debugging
    # random requests
    r2 = requests.get(endpoints['order_book']+'?'+'symbol=BNBBTC&limit=100', auth=(auth_dict['key'], auth_dict['skey']))
    r3 = requests.get(endpoints['avg_price']+'?'+'symbol=BNBBTC', auth=(auth_dict['key'], auth_dict['skey']))
    r7 = requests.get(endpoints['best_price']+'?'+'symbol=BNBBTC', auth=(auth_dict['key'], auth_dict['skey']))


def ping():
    r = requests.get(endpoints['test'])
    print('server ping: ' + str(r))


def get_timestamp():
    t = int(time.time()*1000)
    servertime = requests.get(endpoints['server_time'])
    st = servertime.json()['serverTime']
    return st, t


def tickers_list(market='BTC'):
    r1 = requests.get(endpoints['exchange_info'], auth=(auth_dict['key'], auth_dict['skey']))

    # get all tickers list:
    tickers = []
    for i in range(0, len(r1.json()['symbols'])):
        if r1.json()['symbols'][i]['symbol'][-3:] == market:
            tickers.append(r1.json()['symbols'][i]['symbol'])
    print(tickers)
    # print('status_code=' + str(r1.status_code) + ';' + str(r1.headers['content-type']))
    return tickers


def price_hist(tickers=['BNBBTC'], apikey=auth_dict['key']):
    data={}
    p1=[]
    p2=[]
    if type(tickers) != list:
        tickers=[tickers]
    for i in tickers:
        params = {
            'symbol' : i,
            'limit' : 1000,
        }
        headers = {
            "X-MBX-APIKEY" : apikey,
        }
        r = requests.get(endpoints['price_hist'], params=params, headers=headers).json()
        for j in r:
            p1.append(j['time'])
            p2.append(float(j['price']))
        data[i] = pd.DataFrame(index=p1.copy(), data=p2.copy(), columns=[i])
        p1.clear()
        p2.clear()
    return data


def candlestick(tickers):
    data = {}
    if type(tickers) != list:
        tickers=[tickers]
    for t in tickers:
        r4 = requests.get(endpoints['candlestick']+'?'+'symbol='+ t +'&interval=1h&limit=1000', auth=(auth_dict['key'], auth_dict['skey']))
        candle_columns=['open_datetime', 'open', 'high', 'low', 'close', 'volume', 'close_datetime', 'quote_volume', 'n_trades', 'taker_buy_asset_vol', 'taker_buy_quote_vol', 'ignore']
        candle_info = pd.DataFrame(data=r4.json(), columns=candle_columns)
        # path = '/home/carlos/Documents/BTC_data_2/'+t+'.csv'
        # candle_info.to_csv(path)
        data[t] = candle_info
        # Plot
        # fig = go.Figure(data=[go.Candlestick(x=candle_info['open_datetime'], open=candle_info['open'], high=candle_info['high'], low=candle_info['low'], close=candle_info['close'])])
        # fig.show()
    return data


def sha256_signature(endpoint_params, skey=auth_dict['skey']):
    secret = skey
    params = urlencode(endpoint_params)
    hashedsig = hmac.new(secret.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
    hashedsig_dict = {
        "signature" : hashedsig
    }
    return hashedsig_dict


def account_info(apikey=auth_dict['key']):
    servertimeint = get_timestamp()[0]
    endpoint_params = {
        "timestamp" : servertimeint,
    }
    hashedsig_dict = sha256_signature(endpoint_params)
    endpoint_params.update(hashedsig_dict)
    userdata = requests.get(endpoints['acc_info'],
        params = endpoint_params,
        headers = {
            "X-MBX-APIKEY" : apikey,
        }
    )
    return userdata.json()


def account_snapshot(apikey=auth_dict['key']):
    servertimeint = get_timestamp()[0]
    endpoint_params = {
            "type" : "SPOT",
            "timestamp" : servertimeint,
        }
    hashedsig_dict = sha256_signature(endpoint_params)
    endpoint_params.update(hashedsig_dict)
    data = requests.get(endpoints['acc_snapshot'],
        params = endpoint_params,
        headers = {
            "X-MBX-APIKEY" : apikey,
        }
    )
    return data.json()


def balances():
    Na = {}
    # d = account_snapshot()['snapshotVos'][0]['data']['balances']
    # for i in d:
    #     Na[i['asset']] = float(i['free'])
    d = account_info()['balances']
    for i in d:
        if float(i['free']) > 0:
            Na[i['asset']] = float(i['free'])
    return Na


def prices():
    Pbuy = {}
    Psell = {}
    r = requests.get(endpoints['best_price'], auth=(auth_dict['key'], auth_dict['skey']))
    for i in r.json():
        Pbuy[i['symbol']] = i['askPrice']
        Psell[i['symbol']] = i['bidPrice']
    return Pbuy, Psell