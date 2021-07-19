from handle_api import account_info, tickers_list
# from handle_websocket import best_price
from modelling import delta_price
import time
from threading import Thread

market = 'BTC'
gain = 1.1
Ke = 0.5
k = 300
# Vp =
 
def trading(Vp, Ke=0.5, gain=1.1, market='BTC', k=300):
    # get tickers list (t) for desired market / def tickers_list() / ok
    # get price stream (p) for assets on tickers list / BTC as default currency first (for testnet) / def best_price() / how to run real-time? / partially ok
    # check wallet (w) for free assets / BTC as default currency first (for testnet) / check updating / partially ok
    # update delta price estimation (d) / def delta_price() / choose better prediction model / partially ok
    # run pid to take decision
    # transform pid output using portfolio model
    # run buy or sell operation

    t = tickers_list(market)
    w = next((item for item in account_info()['balances'] if item['asset'] == market), None)
    d = delta_price(t=t)

    controller = PID(Ke, 0, 0)
    controller.send(None) # starts PID
    k = 0
    while True:
        k +=1
        Vref = Vp*gain
        Mv = controller.send([k, Vp, Vref])
        time.sleep(k)


def check(m):
    print('--------------------')
    print(m)
    print('--------------------')


