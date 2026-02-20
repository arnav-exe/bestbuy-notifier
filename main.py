import os
from dotenv import load_dotenv
from pathlib import Path
import importlib

from src.send_ntfy import post_ntfy
from src.ntfy_templates import on_sale, below_max_price, in_stock
from src.log_handler import init_logger
from src.datasources.registry import SourceRegistry

load_dotenv()

DATASOURCE_PATH = Path("src\\datasources\\")

WATCHLIST = [
    {  # lenovo legion go 2 1TB
        "identifiers": {
            "bestbuy": "6643145",
            "amazon": "B0G573TMZS"
        },
        "user_max_price": None,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },
    {  # lenovo legion go 2 2TB
        "identifiers": {
            "bestbuy": "6666376",
            "amazon": "B0FYR2V7ZB",
            "lenovo": "https://www.lenovo.com/us/en/p/handheld/legion-go-gen-2/83n0000aus"
        },
        "user_max_price": None,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },
    {  # LG 27 inch 1440p 180hz monitor (TESTING)
        "identifiers": {
            "bestbuy": 6575404,
            "bhvideo": "some_sku_number"
        },
        "user_max_price": 350,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    }
]


# auto import all modules inside 'src/datasources' to trigger source registry
def import_datasources(logger):
    SourceRegistry.set_logger(logger)

    rel_path = str(DATASOURCE_PATH).replace("\\", ".")
    for file in os.listdir(DATASOURCE_PATH):
        if file.endswith("py") and "_" not in file and file not in ["__init__.py", "base.py", "implementation-test.py", "registry.py"]:
            src_import_str = rel_path + "." + file.split(".")[0]
            importlib.import_module(src_import_str)
            logger.info(f"Registered datasource: {file.split('.')[0]}")


def main(logger):
    sources = SourceRegistry.all()
    logger.info(f"Available datasources: {list(sources.keys())}")

    for item in WATCHLIST:
        logger.info("")
        logger.info("=" * 60)


        for src_name, identifier in item["identifiers"].items():
            if src_name not in sources:
                logger.debug(f"No datasource for '{src_name}', skipping")
                continue

            logger.info(f"Processing: {src_name} | {identifier}")
            logger.info("-" * 60)

            # fetch standardized product data
            data_fetcher = SourceRegistry.get(src_name)

            product = data_fetcher.fetch_product(identifier)

            if product is None:
                continue  # error already logged by datasource

            logger.info(f"Fetched: {product.product_name} | Retailer: {product.retailer_name}")

            if not product.in_stock:
                logger.info("Out of stock, skipping")
                continue

            # check if data meets user reqs
            if item["user_max_price"] is not None:
                if product.on_sale and product.sale_price <= item["user_max_price"]:
                    # fire noti saying that product is in stock AND on sale AND below user_max_price
                    on_sale_body = on_sale(product, item["user_max_price"])
                    post_ntfy(on_sale_body, product.product_url, product.retailer_name, product.retailer_logo, os.getenv("NTFY_TOPIC_URL"))
                    logger.info(f"Sent ON SALE notification for {identifier}")

                elif product.regular_price <= item["user_max_price"]:
                    # fire noti saying product is in stock AND below user_max_price
                    below_max_price_body = below_max_price(product, item["user_max_price"])
                    post_ntfy(below_max_price_body, product.product_url, product.retailer_name, product.retailer_logo, os.getenv("NTFY_TOPIC_URL"))
                    logger.info(f"Sent BELOW MAX PRICE notification for {identifier}")

                else:
                    logger.info(f"Price ${product.regular_price} exceeds max ${item['user_max_price']}, skipping")

            elif item["user_max_price"] is None:
                # fire noti saying product is in stock
                in_stock_body = in_stock(product)
                post_ntfy(in_stock_body, product.product_url, product.retailer_name, product.retailer_logo, os.getenv("NTFY_TOPIC_URL"))
                logger.info(f"Sent IN STOCK notification for {identifier}")


if __name__ == "__main__":
    logger = init_logger()

    import_datasources(logger)
    main(logger)
