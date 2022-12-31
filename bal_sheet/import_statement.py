def import_statement(filename, headers=True) -> dict:
    # imports statement from CSV into statement, a dict of currencies (namedtuples) where key is currency ID (BTC, ETH etc.)
    
    import csv
    from datetime import datetime
    from collections import namedtuple

    statement = dict()

    Currency = namedtuple('currency', ('start_date', 'end_date', 'transactions', 'xrs'))
    Transaction = namedtuple('transaction', ('type', 'time', 'amount'))

    # 0: 'portfolio', 1: type', '2: time', '3: amount', '4: balance', '5: amount/balance unit',
    # '6: transfer id', '7: trade id', '8: order id'

    with open(filename) as f:
        for row in csv.reader(f):
            if headers:
                print([f'{i}: {name}' for i, name in enumerate(row)])
                headers = False
                continue
            currency_name = row[5]
            
            # save TX data
            tx = Transaction(type=row[1], time=datetime.strptime(row[2], '%Y-%m-%dT%H:%M:%S.%fZ'), amount=float(row[3]))

            if currency_name not in statement.keys():
                # set start date if this is the first instance of this currency
                statement[currency_name] = Currency(
                    start_date=tx.time,
                    end_date=tx.time,
                    transactions=[tx],
                    xrs=[]
                    )
            else:
                # update end date only
                statement[currency_name] = statement[currency_name]._replace(end_date=tx.time)
                statement[currency_name].transactions.append(tx)

    return statement
if __name__ == '__main__':
    statement = import_statement('statements/coinbase_2020-2021.csv')
    pass