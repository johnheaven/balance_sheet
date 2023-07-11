from typing import NamedTuple, List, Self
from datetime import datetime
import csv

class Currency(NamedTuple):
    name: str
    start_date: datetime
    end_date: datetime

class Transaction(NamedTuple):
    currency: Currency
    tx_type: str
    time: datetime
    amount: float
    exchange_rate: float | None

    def with_xr(self, to, method: str="mean") -> Self: # TODO declare to: Candle
        # method can be e.g. mean, open, close i.e. the "method" by which to calculate the exchange rate
        amount_eur: float = getattr(to, method)
        return self._replace(exchange_rate=amount_eur)

    def with_xr_1(self):
        # convert 1 to 1 i.e. eur_amount is amount
        return self._replace(exchange_rate=1)


class TransactionLog():
    transactions: List[Transaction] = []
    currencies: dict[str, Currency] = {}

    def __iter__(self):
        return self.transactions.__iter__()

    def read_csv(self, filepath: str, headers=True):
        # imports CSV into self.currencies, a dict of Currency (namedtuples) where key is currency ID (BTC, ETH etc.)
        # CSV schema: 
        # 0: 'portfolio', 1: type', '2: time', '3: amount', '4: balance', '5: amount/balance unit',
        # '6: transfer id', '7: trade id', '8: order id'
        with open(filepath) as f:
            for row in csv.reader(f):
                if headers:
                    print([f'{i}: {name}' for i, name in enumerate(row)])
                    headers = False
                    continue
                currency_name = row[5]
                tx_date = datetime.strptime(row[2], '%Y-%m-%dT%H:%M:%S.%fZ')
                
                if currency_name in self.currencies.keys():
                    # update end date only and overwrite if it already exists
                    self.currencies[currency_name] = self.currencies[currency_name]._replace(end_date=tx_date)
                else:
                    # insert new if it doesn't already exist
                    self.currencies[currency_name] = Currency(name=currency_name, start_date=tx_date, end_date=tx_date)

                # save TX data
                tx = Transaction(currency=self.currencies[currency_name], tx_type=row[1], time=tx_date, amount=float(row[3]), exchange_rate=None)
                self.transactions.append(tx)

    def get_currencies(self) -> dict[str, Currency]:
        return self.currencies
    
    def add_euro_xrs(self, candles): # TODO annotate candles: Candles
        for i, tx in enumerate(self.transactions):
            candle = candles.get_candle_for_time(curr=tx.currency, tx_time=tx.time)
            if candle is not None:
                self.transactions[i] = tx.with_xr(to=candle)
            elif tx.currency.name == "EUR":
                self.transactions[i] = tx.with_xr_1()
            else:
                print(f"No candle found for non-EUR transaction {tx}")
