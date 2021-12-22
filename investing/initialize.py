import os


def initialize(api_type = 'prod'):

    # /api/ endpoints
    endpoints = {
        'test' : '/api/v3/ping',
        'server_time' : '/api/v3/time',
        'exchange_info' : '/api/v3/exchangeInfo',
        'order_book' : '/api/v3/depth',
        'candlestick' : '/api/v3/klines',
        'avg_price' : '/api/v3/avgPrice',
        'best_price' : '/api/v3/ticker/bookTicker',
        'acc_info' : '/api/v3/account',
        'acc_snapshot' : '/sapi/v1/accountSnapshot',
        'price' : '/api/v3/ticker/price',
        'price_hist' : '/api/v3/historicalTrades',
        'order' : '/api/v3/order',
        'test_order' : '/api/v3/order/test',
        'trades' : '/api/v3/myTrades',
        'options_info' : '/vapi/v1/optionInfo',
        'options_order_book' : '/vapi/v1/depth',
        'options_mark_price' : '/vapi/v1/mark',
    }


    if api_type == 'test':
        main_endpoint = 'https://testnet.binance.vision'
        auth_dict = {
            'key' : os.environ.get('TEST_KEY'),
            'skey' : os.environ.get('TEST_SKEY'),
        }
    elif api_type == 'prod':
        main_endpoint = 'https://api1.binance.com'
        optionsEndpoint = 'https://vapi.binance.com'
        auth_dict = {
            'key' : os.environ.get('SPOT_KEY'),
            'skey' : os.environ.get('SPOT_SKEY'),
        }


    # complete endpoints strings
    for i in endpoints:
        # if endpoints[i].find(main_endpoint) == -1:
        if i[0:7] == 'options':
            endpoints[i] = optionsEndpoint + endpoints[i]
        else:
            endpoints[i] = main_endpoint + endpoints[i]
        
    print(endpoints)

    return endpoints, auth_dict