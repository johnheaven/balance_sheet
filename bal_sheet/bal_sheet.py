class BalanceSheet():
    # LIFO: last in, first out (i.e. append to right, pop from left to get next item)
    def __init__(self, year, tax_window=1, lifo=True):
        self.year, self.tax_window = year, tax_window
        self.stock = {}
        self.taxable_profit = 0
        self.lifo = lifo

    def build_sheet(self, transactions):
        # run through transactions and build balance sheet
        for tx in transactions:
            # contains type, time and amount. e.g. ->
            # ['withdrawal', '2020-02-19T16:03:50.884Z', '-0.0549117700000000', '0.0000000000000000']
            # ['default', 'deposit', '2020-02-19T11:11:06.798Z', '0.0549117700000000', '0.0549117700000000']
        
            match tx.amount > 0:
                case True:
                    self.buy(name=tx.currency.name, pieces=tx.amount, piece_cost=tx.exchange_rate, buy_date=tx.time)
                case False:
                    self.sell(name=tx.currency.name, pieces=abs(tx.amount), piece_cost=tx.exchange_rate, sell_date=tx.time, taxable=tx.tx_type not in ['fee', 'withdrawal'])

    def buy(self, name, pieces, piece_cost, buy_date: str):
        from collections import deque
        # check for chronological order before adding
        new_buy = Item(pieces, piece_cost, buy_date)
        if self.stock.get(name, None) and new_buy.buy_date < self.stock[name][-1].buy_date:
            raise ValueError('Items must be added in chronological order.')
        # just add another item to the appropriate queue
        self.stock.setdefault(name, deque()).append(new_buy)

    def sell(self, name: str, pieces: int, piece_cost: float, sell_date, taxable=True, date_format: str='%Y-%m-%d'):
        # continue until we've got enough total stock to sell the required amount
        # if we only partially sell an Item, we need to update it with the remainder
        # and put it back at the front of the queue
        from datetime import datetime
        sell_date = datetime.strptime(sell_date, date_format) if isinstance(sell_date, str) else sell_date

        # start stock picking...
        remainder = pieces
        # while remainder is > 0 with a tiny tolerance for miniscule remainders
        while round(remainder, 12) > 0:
            try:
                item = self.stock[name].pop() if self.lifo else self.stock[name].popleft()
            except KeyError:
                raise KeyError(f'Attempted to sell {name} {remainder} but none remaining')

            # if we don't need to sell all of the item's contents
            if remainder < item.pieces_remaining:
                stock_picked = remainder
                item.update_balance(-stock_picked)
                # put it back on the queue
                self.stock[name].append(item)
            # if we need to sell all of the item's contents
            elif remainder >= item.pieces_remaining:
                stock_picked = item.pieces_remaining
            remainder -= stock_picked

            if taxable and (sell_date - item.buy_date).days <= 365 and sell_date.year == self.year:
                self.taxable_profit += stock_picked * piece_cost - stock_picked * item.piece_cost

    def print_taxable_profit(self):
        print(f"Taxable profit: ", round(self.taxable_profit, 2))

class Item():
    def __init__(self, pieces, piece_cost, buy_date, date_format='%Y-%m-%d'):
        from datetime import datetime
        self.pieces_remaining = pieces
        self.piece_cost = piece_cost
        self.buy_date = datetime.strptime(buy_date, date_format) if isinstance(buy_date, str) else buy_date

    def update_balance(self, pieces):
        self.pieces_remaining += pieces
