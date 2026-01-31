# conditions to send emails:
 1. onSale = true (regardless of price)
    * send email saying product is on sale, and state salePrice
 1. regularPrice <= desired price
    * does not matter if product is on sale or not

# Other factors to consider:
 1. if notifying about sale
    1. (str) orderable = Available
    1. (float) dollarSavings
    1. (str) percentSavings
    1. (str) url

 1. if notifying about regular price coming down
    1. (str) orderable = Available
    1. (str) url

NOTE: keys with missing values are either `empty` or `null`

# PROBLEMS:
 1. 'send_ntfy.py' is too opinionated - too much default data for bestbuy specifically
 1. separate bestbuy and amazon fetching into 2 files?? - need to modularize this to allow future additiosn (EG: returned webscraper data)
 1. use function decorators to cleanly separate logging?

# TODO:
 1. implement strategy pattern to abstract API querying from main (requires defining own internal representatin of data)
 1. implement adapters to translate returned API data into compatible format

# USAGE
 1. `pip install -r requirements.txt` inside project root
 1. `npm install git+https://github.com/arnav-exe/amazon-product-api.git#7a2d602`
