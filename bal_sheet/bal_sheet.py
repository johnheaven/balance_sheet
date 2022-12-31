class BalSheet():
    # LIFO: last in, first out (i.e. append to right, pop from left to get next item)
    def __init__(self, year, tax_window=1):
        self.year, self.tax_window = year, tax_window
        self.stock = dict()
        self.taxable_profit = 0

    def buy(self, name, pieces, piece_cost, buy_date: str):
        from collections import deque
        from datetime import datetime
        # check for chronological order before adding
        new_buy = Item(pieces, piece_cost, buy_date)
        if self.stock.get(name, None) and new_buy.buy_date < self.stock[name][-1].buy_date:
            raise ValueError('Items must be added in chronological order.')
        # just add another item to the appropriate queue
        self.stock.setdefault(name, deque()).append(new_buy)

    def sell(self, name, pieces, piece_cost, sell_date, taxable=True, date_format='%Y-%m-%d'):
        # continue until we've got enough total stock to sell the required amount
        # if we only partially sell an Item, we need to update it with the remainder
        # and put it back at the front of the queue
        from datetime import datetime
        sell_date = datetime.strptime(sell_date, date_format) if isinstance(sell_date, str) else sell_date

        # start stock picking...
        remainder = pieces
        # while remainder is > 0 with a tiny tolerance for miniscule remainders
        while remainder > pieces / 1e16:
            item = self.stock[name].pop()

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

class Item():
    def __init__(self, pieces, piece_cost, buy_date, date_format='%Y-%m-%d'):
        from datetime import datetime
        self.pieces_remaining = pieces
        self.piece_cost = piece_cost
        self.buy_date = datetime.strptime(buy_date, date_format) if isinstance(buy_date, str) else buy_date

    def update_balance(self, pieces):
        self.pieces_remaining += pieces
