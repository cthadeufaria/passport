from handle_api import tickers_list
from binance import ThreadedWebsocketManager, streams
from initialize import initialize
from trading import check   

endpoints = initialize('test')[0]
auth_dict = initialize('test')[1]

def run_twm():
    global twm
    twm = ThreadedWebsocketManager(api_key=auth_dict['key'], api_secret=auth_dict['skey'])
    # start is required to initialise its internal loop
    twm.start()


def best_price(tickers):
    run_twm()

    if type(tickers) != list:
        tickers = [tickers]

    def handle_socket_message(msg, results=[]):
        results.append(msg['data']['b'])
        if len(results) >= 50:
            results = results[0:50]
        print(msg)
        check(results)

    stream_name = '@bookTicker'
    streams = []
    for i in tickers:
        streams.append(i.lower()+stream_name)

    twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)
    twm.join()


# binance websocket example
def main():

    symbol = 'BNBBTC'

    twm = ThreadedWebsocketManager(api_key=auth_dict['key'], api_secret=auth_dict['skey'])
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        # print(f"message type: {msg['e']}")
        print(msg)

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
    twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    twm.join()


if __name__ == "__main__":
   best_price('BNBBTC')