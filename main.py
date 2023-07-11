
def main(filepath: str):
    from misc.transaction_log import TransactionLog
    from misc.candles import Candles
    from bal_sheet.bal_sheet import BalanceSheet

    # get statement from CSV
    transactions = TransactionLog()
    transactions.read_csv(filepath)
    # get list of required currencies so we can get exchange rates
    currencies = transactions.get_currencies()
    # get exchange rates we need
    candles = Candles(currencies, cached=True)
    # convert all to EUR
    transactions.add_euro_xrs(candles)

    bs = BalanceSheet(year=2021, tax_window=1, lifo=True)

    bs.build_sheet(transactions=transactions)

    bs.print_taxable_profit()
    
    # pass statement is there just so I can add a breakpoint in VS Code when debugging
    pass

if __name__ == '__main__':
    main(filepath='statements/account.csv')