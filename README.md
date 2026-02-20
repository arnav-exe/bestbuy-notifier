# USAGE
 1. `pip install -r requirements.txt`
 1. `crawl4ai-setup`
 1. `npm install git+https://github.com/arnav-exe/amazon-product-api.git#7a2d602`


# TODO:
 - add multithreading - assign 1 thread to each datasource


# FLOW:
 1. for each product:
    1. for each identifier inside a product:
        1. if we have a matching data source for that particular identiifer, run 'fetch_product()' which will return data in Product obj format
        1. check in stock and sale keys against user specification
        1. if any condition is met, fire appropriate ntfy



# SOURCES TO ADD:
 - bhvideo - crawl4ai



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
