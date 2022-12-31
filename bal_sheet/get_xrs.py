def get_xrs(statement: dict) -> dict:
    """Pulls in exchange rate data from Coinbase API and tags them on to the statement

    Args:
        statement (dict): The statement, as generated by import_statement.py

    Returns:
        dict: statement, with XRs attached
    """
    from datetime import datetime
    from datetime import timedelta
    import time, json
    import requests
    from collections import namedtuple
    from statistics import mean

    Candle = namedtuple('candle', ('time', 'low', 'high', 'open', 'close', 'volume', 'mean'))

    # maximum number of items (candles) per request - Coinbase allows 300 max
    max_items = 150

    # number of seconds between each item - Coinbase allows values of 60, 300, 900, 3600, 21600, 86400
    # 86400s = 1 day
    granularity = 86400

    # the maximum time between start date and end date in the query
    # i.e., converts items/granularity to time interval
    interval_seconds = max_items * granularity
    interval = timedelta(seconds=interval_seconds)

    # EURO exchange-rate data is missing for DASH, OXT, ZEC, REP, DAI, EUR
    # BTC exchange-rate data is missing for BTC, OXT, USDC, DAI, EUR

    xrs = []

    for name, currency in statement.items():

        # the remaining time to be covered in a query - inititate this so it's > 0 and the loop runs
        remainder = timedelta(seconds=1)

        # subtract one day from start date to make sure the timeframe starts early enough
        query_start_date = currency.start_date - timedelta(seconds=granularity)
        # set start and end to the same as they'll get adjusted in first iteration of loop
        query_end_date = query_start_date

        # whether request failed to yield XR data candles
        failed = False

        while remainder >= timedelta(seconds=0) and failed == False:
            # update start and end of next query
            query_start_date = query_end_date + timedelta(seconds=1)
            query_end_date += interval

            # calculate the new remainder
            # we add a day to currency.end_date to make sure we capture the whole timeframe
            remainder = currency.end_date + timedelta(days=1) - query_end_date

            # make the HTTP request
            failed = False
            payload = {'granularity': granularity, 'start': datetime.strftime(query_start_date, '%Y-%m-%dT%H:%M:%S.%fZ'), 'end': datetime.strftime(query_end_date, '%Y-%m-%dT%H:%M:%S.%fZ')}
            r = requests.get(url=f'https://api.exchange.coinbase.com/products/{name}-EUR/candles/', params=payload)
            
            # parse json
            xrs = json.loads(r.text)
            if not isinstance(xrs, list):
                print(f'Failed with response {r.text} for currency {name}')
                print(payload)
                failed = True
                continue
            
            # convert json to namedtuples (Candle)
            candles = []
            for xr in xrs:
                candles.append(Candle(time.localtime(xr[0]), *xr[1:], mean=mean(xr[1:5])))
            
            # add to statement
            statement[name].xrs.extend(candles)

            # short pause to avoid hammering the API and getting blocked
            time.sleep(0.5)

    return statement

def xr_convert(tx_time, xrs: list):
    # assumes granularity of 1 day, i.e. it's the right XR if it's for the same day
    try:
        return tuple(
            filter(
                lambda xr: all(
                    (xr.time.tm_year == tx_time.year, xr.time.tm_mon == tx_time.month, xr.time.tm_mday == tx_time.day)
                    ), xrs
                )
            )[0].mean
    except IndexError:
        print('No results...')
        return -1


if __name__ == '__main__':
    get_xrs()