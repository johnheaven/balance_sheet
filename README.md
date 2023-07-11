# bal_sheet - calculating taxable income from Coinbase Pro statement

Calculating tax owed on cryptocurrency is a pain in the arse. Especially as Coinbase Pro statements don't tell you the precise Euro amount at the time of sale. Don't take my word for it (i.e. don't sue me if I get it wrong), but in Germany:

* you have to decide on LIFO or FIFO as a method for calculating your tax, then stick to it for the foreseeable future
* any profit on currency you sell within a year of buying it is taxable
* exchanging one cryptocurrency for another counts as a sale, so you have to know the Euro price you paid when you bought the thing you're selling, and the Euro price of the thing you're buying now.

For example: you buy 1 Bitcoin for 10,000 EUR and then another for 20,000 EUR, then sell 1.5 for 30,000 EUR

If you calculate according to last in, first out – **LIFO** –
* your income is 30,000
* your costs are 20,000 + 5,000
* your profit is 30,000 - 25,000 = 5,000.

If you calculate per first in first out – **FIFO** –
* your income is 30,000
* your costs are 10,000 + 10,000
* your profit is 30,000 - 20,000 = 10,000.

So in this case you want to go for LIFO to pay less tax.

To make things even more complicated: any profits on things you bought more than a year ago don't (afaik) have to be taxed. So if you bought the first Bitcoin in the above example more than a year ago, any profit on that coin wouldn't be taxable. Urgh... terribly difficult.

Add in all the complexity of calculating my tax owed on cryptocurrency sales from my Coinbase Pro statement... and that's what this repo is for. There's absolutely no guarantee or warranty or anything resembling liability on my part if you use this code.

## How it works

### Step 1: Read CSV and capture transactions and currencies
It reads a CSV and builds i) a list of transactions and ii) a separate list of currencies encountered. 

For each currency in this list, it notes the first and last date on which it was encountered.

### Step 2: Get exchange rate data (candles)

The list of currencies is used to build a list of candles (i.e. exchange rates), pulled from the Coinbase Pro API. Each currency contains a start and end date, so it knows the time frame for which to fetch exchange rates specific to each currency.

Because of the way the Coinbase API works, we have to make several requests per currency to get exchange rates for the entire time window because there is a maximum number of candles you can receive in a query.

### Step 3: Add Euro exchange rate to each transaction

We then go through each transaction and add the Euro exchange rate for later use. We do this by looking up a candle for the day of the transaction. (The granularity could be increased but this would require more API requests.)

### Step 4: Build the balance sheet

The balance sheet is then built by determining whether each transaction is a purchase or a sale (based on whether it's a +ve or -ve amount). It builds an inventory for each currency, and notes how much of each currency was bought for what price.

When booking a sale, it "drills down" into the inventory to take just enough of the inventory for that currency to fulfil the sale, noting how much was sold at what price, and keeping a records of what profit is taxable as it goes along.

### Step 5: Tell you how much taxable profit you've made

Then it just tells you how much you need to tax. Elation! The code (one assumes) worked, or at least didn't crash! Disillusionment: I owe the tax office a lot of money.

## Additional notes

* It doesn't do much error-handling, so if you run out inventory for a currency, the whole thing blows up. It just ignores inventory it can't find exchange rate data for.
* It caches the API requests if set correctly, using the `shelve` module from the Python standard library. This saves time and avoids hammering the Coinbase Pro API during debugging.
* If using the API and not the cached data, it pauses for 0.5 seconds between requests.

## Objects

There are tonnes of objects in this project. Here are the main ones:

* `TransactionLog` -> the log of transactions that is generated from the CSV.
* `Transaction` -> data about a single transaction, including whether it's a deposit, withdrawal, match etc., the time, the amount. Later in the process, a Euro exchange rate gets added for that specific time and currency.
* `Currency` -> a "specification" for each currency - `name`, `start_date` and `end_date`. We only need this to know which window to query the Coinbase API for for each currency. This extends `collections.namedtuple`.
* `Candles` -> essentially a dictionary with a couple of added methods for getting all the candles from Coinbase needed to convert the inventory items appropriately. The `Candle` object represents an individual candle (i.e. exchange rate data for a particular period) and extends `collections.namedtuple`. There's duplication between the `Candles` key and the `name` attribute within the `Candle` object but it was quicker and easier to search for a currency by its key within the `Candles` object.
