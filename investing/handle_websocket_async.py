import asyncio
from binance import AsyncClient, BinanceSocketManager
from initialize import initialize

endpoints = initialize('test')[0]
auth_dict = initialize('test')[1]

async def best_price_async(tickers):
    client = await AsyncClient.create(api_key=auth_dict['key'], api_secret=auth_dict['skey'])
    bm = BinanceSocketManager(client, user_timeout=5)
    # start any sockets here, i.e a trade socket
    # ts = bm.trade_socket('BNBBTC')
    if type(tickers) != list:
        tickers = [tickers]

    stream_name = '@bookTicker'
    streams = []
    for i in tickers:
        streams.append(i.lower()+stream_name)
    ts = bm.multiplex_socket(streams=streams)

    # then start receiving messages
    # async with ts as tscm:
    #     while True:
    #         res = await tscm.recv()
    #         print(res)
    
    # enter the context manager
    await ts.__aenter__()
    # receive a message
    msg = await ts.recv()
    print(msg)
    # exit the context manager
    await ts.__aexit__(None, None, None)

    # await client.close_connection()

# if __name__ == "__main__":

#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main(tickers))

# # set a timeout of 60 seconds
# bm = BinanceSocketManager(client, user_timeout=60)

# ts = bm.trade_socket('BNBBTC')
# # enter the context manager
# await ts.__aenter__()
# # receive a message
# msg = await ts.recv()
# print(msg)
# # exit the context manager
# await ts.__aexit__(None, None, None)