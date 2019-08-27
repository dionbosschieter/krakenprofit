import sys
import krakenex
import logging
import influxdb


def write_profit_to_influx(profit):
    """
    Writes the given profit to influx db with the current timestamp

    :param profit: the calculated profit since start
    """
    profit_json_body = [
        {
            "measurement": "profit",
            "tags": {
                "exchange": "kraken",
            },
            "fields": {
                "value": profit
            }
        }
    ]

    client = influxdb.InfluxDBClient('localhost', 8086, 'root', 'root', 'moneys')
    client.write_points(profit_json_body)


if __name__ == '__main__':
    profit = 0
    sell_log = {}
    current_assets = {}
    logger = logging.getLogger('profitlogger')
    logger.addHandler(logging.StreamHandler(sys.stdout))

    if '-d' in sys.argv:
        logger.setLevel(logging.DEBUG)

    k = krakenex.API()
    k.load_key('kraken.key')

    balance = k.query_private('Balance')['result']
    orders = k.query_private('ClosedOrders')
    closed_orders = orders['result']['closed']

    for order_id in closed_orders:
        order = closed_orders[order_id]
        if order['status'] == 'closed':
            type = order['descr']['type']
            pair = order['descr']['pair']
            cost = float(order['cost'])
            if type == 'sell':
                sell_log[pair] = cost
            elif type == 'buy':
                if pair in sell_log:
                    profit += sell_log[pair] - cost
                    sell_log.pop(pair)
                else:
                    current_assets[pair] = cost

            logger.debug('{} {} {}'.format(type, pair, cost))

    for asset in balance:
        is_coin = asset[0] == 'X'

        count = float(balance[asset])

        if is_coin == False:
            continue

        query_pair = asset[1:] + 'EUR'
        result_pair = asset + 'ZEUR'

        ticker_data = k.query_public('Ticker', {'pair': query_pair})
        last_price = float(ticker_data['result'][result_pair]['a'][0])

        asset_worth = (last_price * count)
        diff = asset_worth - current_assets[query_pair]
        logger.debug('profit %s', profit)
        logger.debug('diff %s', diff)
        profit += diff

    logger.debug('profit %s', profit)
    logger.debug('assets %s', current_assets)
    logger.debug('balance %s', balance)
    write_profit_to_influx(profit)
