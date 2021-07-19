#   OLD CODE THAT MIGHT BE USEFUL SOMEDAY

from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from binance.spot import Spot
import logging


def account_data():
    client = Spot()
    print(client.time())
    client = Spot(key=auth_dict['key'], secret=auth_dict['skey'])
    print(client.account())


def account_status():
    config_logging(logging, logging.DEBUG)
    spot_client = Client(auth_dict['key'], auth_dict['skey'])
    logging.info(spot_client.account_status())


def account_snapshot():
    config_logging(logging, logging.DEBUG)
    spot_client = Client(auth_dict['key'], auth_dict['skey'])
    logging.info(spot_client.account_snapshot("SPOT"))