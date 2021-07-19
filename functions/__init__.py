


def initialize(api_type = 'test'):

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
    }

    # complete endpoints strings
    for i in endpoints:
        if endpoints[i].find(main_endpoint) == -1:
            endpoints[i] = main_endpoint + endpoints[i]

    # choose auth for each main endpoint
    if main_endpoint[:11] == 'https://api':
        auth_dict = {
            'key' : '6PsKNupfO7ubDdgBaDv3KDveMp4PAAUE2ywIV1bVmZHZ9lIxfbMDWSbSt1XoMJXe',
            'skey' : 'w24jgAs9WIjPz8ss7T9kLILl1tSpl86pbxMrcYE2e6cr5q9M4LHYaKPeivw15k9v',
        }
    elif main_endpoint == 'https://testnet.binance.vision':
        auth_dict = {
            'key' : '2fwlKq8Tzw0EKVXKi5I1gV7dNL7tPZcA7be4CKnZYPRxO7GkP7GY8iyDTfie4sTl',
            'skey' : 'T8pxHPP9Z1HIrL2a2JnMhwOiD7xzDmSz6UXg161cRg6G2NXD7cK70UxNTuCAiuIh',
        }
        
    print(endpoints)

    return endpoints, auth_dict