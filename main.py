import os
import sys
import krakenex
import logging
import influxdb


def write_balance_to_influx(balance):
    """
    Writes the given balance to influx db with the current timestamp

    :param balance: the calculated profit since start
    """
    profit_json_body = [
        {
            "measurement": "account",
            "tags": {
                "type": "kraken",
            },
            "fields": {
                "value": balance
            }
        }
    ]

    client = influxdb.InfluxDBClient('localhost', 8086, 'root', 'root', 'moneys')
    client.write_points(profit_json_body)


if __name__ == '__main__':
    sell_log = {}
    current_assets = {}
    key_path = 'kraken.key'
    logger = logging.getLogger('profitlogger')
    logger.addHandler(logging.StreamHandler(sys.stdout))

    if '-d' in sys.argv:
        logger.setLevel(logging.DEBUG)

    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        key_path = sys.argv[1]
        logger.debug('changed keypath to "%s"', key_path)

    k = krakenex.API()
    k.load_key(key_path)

    balance = k.query_private('Balance')['result']
    balance_in_eur = 0

    for asset in balance:
        is_coin = asset[0] == 'X'

        count = float(balance[asset])

        if is_coin == False:
            balance_in_eur += count
            continue

        query_pair = asset[1:] + 'EUR'
        result_pair = asset + 'ZEUR'

        ticker_data = k.query_public('Ticker', {'pair': query_pair})
        last_price = float(ticker_data['result'][result_pair]['a'][0])

        asset_worth = (last_price * count)
        balance_in_eur += asset_worth
        logger.debug('asset "%s" worth "%s"', asset, asset_worth)

    logger.debug('balance %s', balance_in_eur)
    write_balance_to_influx(balance_in_eur)
