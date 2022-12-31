def test_1():
    from bal_sheet.bal_sheet import BalSheet
    balsheet = BalSheet(year=2020, tax_window=1)
    balsheet.buy('BTC', 100, 5, '2019-01-01')
    balsheet.buy('BTC', 200, 5, '2019-12-31')
    balsheet.sell('BTC', 250, 2000, '2020-05-20')
    # revenue of taxable - buying costs, i.e. 200 * 2000 - 200 * 5 
    print(balsheet.taxable_profit)
    assert(balsheet.taxable_profit == 200 * 2000 - 200 * 5)

def test_2():
    from bal_sheet.bal_sheet import BalSheet
    balsheet = BalSheet(year=2020, tax_window=1)
    balsheet.buy('BTC', 200, 5, '2018-12-31')
    balsheet.buy('BTC', 100, 5, '2019-01-01')
    balsheet.sell('BTC', 250, 2000, '2020-05-20')
    # revenue of taxable - buying costs, i.e. 0 because none of purchases are in tax window
    print(balsheet.taxable_profit)
    assert(balsheet.taxable_profit == 0)

def test_3():
    from bal_sheet.bal_sheet import BalSheet
    balsheet = BalSheet(year=2020, tax_window=1)
    balsheet.buy('BTC', 100, 10, '2019-05-21')
    balsheet.buy('BTC', 200, 5, '2019-12-31')
    balsheet.sell('BTC', 250, 2000, '2020-05-20')
    # revenue of taxable - buying costs
    print(balsheet.taxable_profit)
    assert(balsheet.taxable_profit == 250 * 2000 - 200 * 5 - 50 * 10)

def test_4():
    # Test whether we get an assertion error if transactions are in the wrong (chronological) order
    from bal_sheet.bal_sheet import BalSheet
    import pytest
    balsheet = BalSheet(year=2020, tax_window=1)
    balsheet.buy('BTC', 200, 5, '2019-12-31')
    with pytest.raises(ValueError):
        balsheet.buy('BTC', 100, 10, '2019-05-21')

def test_5():
    from bal_sheet.bal_sheet import BalSheet
    balsheet = BalSheet(year=2020, tax_window=1)
    balsheet.buy('ETH', 100, 3, '2020-01-01')
    balsheet.buy('BTC', 300, 60, '2020-01-02') # 290
    balsheet.buy('ETH', 100, 20, '2020-01-02')
    balsheet.buy('BTC', 250, 60, '2020-02-04')
    balsheet.buy('ETH', 15, 55, '2020-03-01')
    balsheet.sell('BTC', 250, 2000, '2020-05-20')
    balsheet.sell('BTC', 10, 3000, '2020-05-20')
    balsheet.sell('ETH', 200, 5, '2020-12-31')
    balsheet.sell('BTC', 250, 2000, '2021-05-20')
    
    print(balsheet.taxable_profit)
    assert(balsheet.taxable_profit == 250 * 2000 - 250 * 60 + 10 * 3000 - 10 * 60 + 200 * 5 - 15 * 55 - 100 * 20 - 85 * 3)
