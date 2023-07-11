from misc.transaction_log import Currency
from typing import NamedTuple, Any
from collections import UserDict

class Candle(NamedTuple):
    time: Any #TODO declare time_struct properly
    mean: float
    low: float
    high: float
    close: float
    volume: int

class Candles(UserDict):
    def __init__(self, currencies: dict[str, Currency], cached=True, write_cache=True):
        self.data: dict = {}
        for curr in currencies.values():
            self.get_xr_candles(curr, cached=cached, write_cache=write_cache)

    def get_xr_candles(self, curr: Currency, cached=False, write_cache=True):
        import datetime, requests, time, json, shelve
        from statistics import mean

        # maximum number of items (candles) per request - Coinbase allows 300 max
        max_items = 150

        # number of seconds between each item - Coinbase allows values of 60, 300, 900, 3600, 21600, 86400
        # 86400s = 1 day
        granularity = 86400

        # the maximum time between start date and end date in the query
        # i.e., converts items/granularity to time interval
        interval_seconds = max_items * granularity
        interval = datetime.timedelta(seconds=interval_seconds)

        # EURO exchange-rate data is missing for DASH, OXT, ZEC, REP, DAI, EUR
        # BTC exchange-rate data is missing for BTC, OXT, USDC, DAI, EUR

        # the remaining time to be covered in a query - inititate this so it's > 0 and the loop runs
        remainder = datetime.timedelta(seconds=1)

        # subtract one day from start date to make sure the timeframe starts early enough
        query_start_date = curr.start_date - datetime.timedelta(seconds=granularity)
        # set start and end to the same as they'll get adjusted in first iteration of loop
        query_end_date = query_start_date

        # whether request failed to yield XR data candles
        failed = False

        while remainder >= datetime.timedelta(seconds=0) and failed == False:
            # update start and end of next query
            query_start_date = query_end_date + datetime.timedelta(seconds=1)
            query_end_date += interval

            # calculate the new remainder
            # we add a day to currency.end_date to make sure we capture the whole timeframe
            remainder = (curr.end_date + datetime.timedelta(days=1)) - query_end_date

            # build the HTTP request
            failed = False
            payload = {'granularity': str(granularity), 'start': datetime.date.strftime(query_start_date, '%Y-%m-%dT%H:%M:%S.%fZ'), 'end': datetime.date.strftime(query_end_date, '%Y-%m-%dT%H:%M:%S.%fZ')}
            
            cache_success = False
            if cached:
                # get data from cache if required and if it exists
                try:
                    with shelve.open('cache/xrs.shelve') as cache_obj:
                        r = cache_obj[str(payload)]
                except:
                    print("Couldn't read from cache")
                    cache_success = False
                else:
                    print('Successfully read from cache')
                    cache_success = True

            if not cache_success:
                print('Reading from API')
                time.sleep(0.5)
                r = requests.get(url=f'https://api.exchange.coinbase.com/products/{curr.name}-EUR/candles/', params=payload)
                if write_cache:
                    print('Writing to cache')
                    with shelve.open('cache/xrs.shelve') as cache_obj:
                        cache_obj[str(payload)] = r
            
            # parse json
            xrs = json.loads(r.text)
            if not isinstance(xrs, list):
                print(f'Failed with response {r.text} for currency {curr.name}')
                print(payload)
                failed = True
                continue
            
            # convert json to namedtuples (Candle)
            candles = []
            for xr in xrs:
                #xr_time, xr_mean, low, high, close, volume = time.localtime(xr[0]), mean(xr[1:5]), xr[1], xr[2], xr[3], xr[4]
                candles.append(Candle(time.localtime(xr[0]), mean(xr[1:5]), *xr[1:5]))

            if curr.name in self.data.keys():
                self.data[curr.name] += candles
            else:
                self.data[curr.name] = candles

    def get_candle_for_time(self, curr: Currency, tx_time) -> Candle | None:
        # find candle for given tx_time. assumes granularity of 1 day, i.e. it's the right candle if it occurs on the same day
        candle = None
        for c in self.data.get(curr.name, []):
            if all((c.time.tm_year == tx_time.year, c.time.tm_mon == tx_time.month, c.time.tm_mday == tx_time.day)):
                candle = c
                break
        return candle