# Usage
 1. `pip install -r requirements.txt`
 1. `crawl4ai-setup`
 1. `npm install git+https://github.com/arnav-exe/amazon-product-api.git#7a2d602`
 1. create `.env` file in the root directory with these two keys: `BESTBUY_API_KEY`, `NTFY_TOPIC_URL` (see `.env.example` for formats)

## For setup on raspberry pi, also run this:
 1. `sudo apt update`
 1. `sudo apt-get install xvfb`


# Flow:
 1. for each product:
    1. for each identifier inside a product:
        1. if we have a matching data source for that particular identiifer, run 'fetch_product()' which will return data in Product obj format
        1. check in stock and sale keys against user specification
        1. if any condition is met, fire appropriate ntfy



# SOURCES TO ADD:
 - bhvideo - crawl4ai
 - microcenter - crawl4ai
 - costco - crawl4ai



# Patterns used:
 1. strategy pattern - main calls a generic 'execute' function to fetch data regardless of datasource. 
 1. adapter pattern - Each datasource is separately implemented, following a 3 stage flow:
    1. fetching data from src (via api)
    1. conforming data into internal representation (shown below)
    1. consuming normalized data  



# Internal Representation
From the `schema.py` Product dataclass
```python
@dataclass
class Product:
    identifier: str  # EG: sku, asin code. etc.
    product_name: str
    in_stock: bool
    on_sale: bool
    sale_price: float
    regular_price: float
    product_url: str
    retailer_name: str
    retailer_logo: str  # retailer logo url

```



# Future Work
## Auto-generated NTFY topic URLs
 * Persistently store hash of all products (both current and historical) and mapping to a uuid4 str which is its NTFY topic URL
 * Have a master NTFY topic that user is subscribed to
 * For every new item, generate new NTFY URL, save item mapping, and send notification via master topic with link attachment that looks like this: `ntfy://ntfy.sh/{ntfy_topic_url}?display={item_name}`
 * when user clicks on link, it will open topic and automatically subscribe
 * all notifications for that particular item will be sent through that topic
