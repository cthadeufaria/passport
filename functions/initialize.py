import os


def initialize(api_type = 'prod'):

    if api_type == 'test':
        main_endpoint = 'https://testnet.binance.vision'
    elif api_type == 'prod':
        main_endpoint = 'https://api1.binance.com'

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
    }

    # complete endpoints strings
    for i in endpoints:
        if endpoints[i].find(main_endpoint) == -1:
            endpoints[i] = main_endpoint + endpoints[i]

    # choose auth for each main endpoint
    if main_endpoint == 'https://api1.binance.com':
        auth_dict = {
            'key' : os.environ.get('SPOT_KEY'),
            'skey' : os.environ.get('SPOT_SKEY'),
        }
    elif main_endpoint == 'https://testnet.binance.vision':
        auth_dict = {
            'key' : os.environ.get('TEST_KEY'),
            'skey' : os.environ.get('TEST_SKEY'),
        }
        
    print(endpoints)

    return endpoints, auth_dict