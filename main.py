
def main(filename):
    from misc.get_xrs import add_xrs_to_statement, xr_convert
    from misc.import_statement import import_statement
    from bal_sheet.bal_sheet import BalSheet

    # get statement from CSV
    statement = import_statement(filename)
    
    # add exchange rates to statement
    statement = add_xrs_to_statement(statement=statement, cached=True)

    # run through transactions and build balance sheet
    bs = BalSheet(year=2020, tax_window=1)
    for currency, data in statement.items():
        for tx in data.transactions:
            # contains type, time and amount. e.g. ->
            # ['withdrawal', '2020-02-19T16:03:50.884Z', '-0.0549117700000000', '0.0000000000000000']
            # ['default', 'deposit', '2020-02-19T11:11:06.798Z', '0.0549117700000000', '0.0549117700000000']
            if currency == 'EUR':
                cost_EUR = 1
            elif len(data.xrs):
                cost_EUR = xr_convert(tx_time=tx.time, xrs=data.xrs)
                if cost_EUR == -1:
                    print(f'Couldn\'t match XR for {currency} at {tx.time}')
                    continue
            else:
                print('No XR info for ' + currency)
                break
            
            match tx.amount > 0:
                case True:
                    bs.buy(name=currency, pieces=tx.amount, piece_cost=cost_EUR, buy_date=tx.time)
                case False:
                    bs.sell(name=currency, pieces=abs(tx.amount), piece_cost=cost_EUR, sell_date=tx.time, taxable=tx.type not in ['fee', 'withdrawal'])

    print(bs.taxable_profit)
    
    # pass statement is there just so I can add a breakpoint in VS Code when debugging
    pass

if __name__ == '__main__':
    main(filename='statements/account.csv')