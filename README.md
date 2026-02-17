# USAGE
 1. `pip install -r requirements.txt` inside project root
 1. `npm install git+https://github.com/arnav-exe/amazon-product-api.git#7a2d602`



# TODO
 - RETRIES + EXPONENTIAL BACKOFF WILL HAVE TO BE A FUNCTION DECORATOR OR SMTN GLOBAL - DO NOT IMPLEMENT THIS PER DATASOURCE


# FLOW:
 1. for each product:
    1. for each identifier inside a product:
        1. if we have a matching data source for that particular identiifer, run 'fetch_product()' which will return data in Product obj format
        1. check in stock and sale keys against user specification
        1. if any condition is met, fire appropriate ntfy



# SOURCES TO ADD:
 - amazon - amazon product api
 - lenovo website - crawl4ai
 - costco - crawl4ai
 - bhvideo - crawl4ai

 (for ssds)
 - micro center - [check if they have own or 3rd party api]
 - newegg - [check if they have own or 3rd party api]



# Goal of this refactor
 * separate concerns into 3 distinct categories:
    1. fetching data from src (via api)
    1. normalizing data into internal representation
    1. consuming normalized data


# Internal Representation
```python
ir = {
    "identifier": "str",
    "product_name": "str",
    "in_stock": "bool",
    "on_sale": "bool",
    "sale_price": "float",
    "regular_price": "float",
    "dollar_savings": "float",
    "percent_savings": "float",
    "retailer": "str",
    "product_url": "str",
    "retailer_icon": "str"
}
```

This state will be stored in a python `dataclass`. Dataclasses should be used whenver the class you are defining holds a lot of attributes. Therefore, dataclasses are typically used over regular classes to store state.


# TODO:
 1. get data of an amazon product that is in stock AND NOT on sale (to confirm that if product is not on sale, current_price == before_price) - maybe lgtv


