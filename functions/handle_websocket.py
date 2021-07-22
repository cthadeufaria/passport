from handle_api import tickers_list
from binance import ThreadedWebsocketManager, streams
from initialize import initialize
import pandas as pd 


endpoints = initialize('test')[0]
auth_dict = initialize('test')[1]


def run_twm():
    global twm
    twm = ThreadedWebsocketManager(api_key=auth_dict['key'], api_secret=auth_dict['skey'])
    # start is required to initialise its internal loop
    twm.start()


def handle_socket_message(msg, results=[]):
    results.append(msg['data']['b'])
    if len(results) >= 50:
        results = results[-50:]
    print(msg)
    print(results)
    global df
    df = pd.DataFrame(results)


def best_price(tickers):
    run_twm()

    if type(tickers) != list:
        tickers = [tickers]

    stream_name = '@bookTicker'
    streams = []
    for i in tickers:
        streams.append(i.lower()+stream_name)

    twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)
    twm.join()


if __name__ == "__main__":
   best_price('BNBBTC')