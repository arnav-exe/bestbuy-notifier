import time
import os
from dotenv import load_dotenv
from pathlib import Path
import importlib

from src.send_ntfy import post_ntfy
from src.ntfy_templates import sale_ntfy, non_sale_ntfy
from src.log_handler import init_logger
from src.datasources.registry import SourceRegistry

load_dotenv()

DATASOURCE_PATH = Path("src\\datasources\\")

PRODUCTS = [
    {  # airpods pro 3
        "desired_price": 200,
        "identifiers": [
            {"bestbuy": 6376563},
            {"amazon": "B0FQFB8FMG"}
        ],
        "stock_notifier": False,
        "sale_notifier": True,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },

    {  # lenovo legion go 2 - 1tb
        "desired_price": 1400,
        "identifiers": [
            {"bestbuy": 6643145},
            {"amazon": "B0G573TMZS"},
        ],
        "stock_notifier": True,
        "sale_notifier": False,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },

    {  # lenovo legion go 2 - 2tb
        "desired_price": 1500,
        "identifiers": [
            {"bestbuy": 6666376},
            {"amazon": "B0FYR2V7ZB"},
        ],
        "stock_notifier": True,
        "sale_notifier": False,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },

    {  # LG 27 inch 1440p 180hz monitor (TESTING)
        "desired_price": 400,
        "identifiers": [
            {"bestbuy": 6575404},
            {"bhvideo": "some_sku_number"}
        ],
        "stock_notifier": True,
        "sale_notifier": True,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    }
]


def parse_and_notify(product: dict, user_product_data: dict):
    product_name = " ".join(product["name"].split()[:5])

    sent_ntfy = False

    if product["orderable"] == "Available" and product["onSale"]:  # if sale
        ntfy_body = sale_ntfy(product_name, product["salePrice"], product["regularPrice"], product["dollarSavings"], product["percentSavings"], product["url"], product["priceUpdateDate"])

        post_ntfy(ntfy_body, user_product_data["ntfy_topic"])

        sent_ntfy = True

    # if not sale but price <= desired price
    elif product["orderable"] == "Available" and product["regularPrice"] <= user_product_data["desired_price"]:
        ntfy_body = non_sale_ntfy(product_name, product["regularPrice"], user_product_data["desired_price"], product["url"], product["priceUpdateDate"])

        post_ntfy(ntfy_body, user_product_data["ntfy_topic"])

        sent_ntfy = True

    return sent_ntfy


def process_products(logger, p):
    logger.info("")
    # exponential backoff params
    retries = 10
    delay = 2
    exp = 0

    url = f"https://api.bestbuy.com/v1/products/{p['bestbuy_sku']}.json?show={FIELDS}&apiKey={os.getenv('BESTBUY_API')}"

    # fetch product data from API
    for i in range(retries):  # exponential backoff
        data = get_product_data(url, logger)

        if "errorCode" in data:  # if returned dict contains 'errorCode' (implying fetch was unsuccessful)
            logger.warning(data)
            sleep_time = (delay ** exp) / 2
            time.sleep(sleep_time)
            exp += 1

        else:
            break

    # parse returned data and fire noti
    sent_ntfy = parse_and_notify(data, p)

    if sent_ntfy:
        logger.info(f"Sent ntfy notification for product: {p['bestbuy_sku']}")

    else:
        logger.info(f"Did NOT send ntfy notification for product {p['bestbuy_sku']} (either out of stock or above desired price)")

    logger.info("")
    logger.info("="*80)


# auto import all modules inside 'src/datasources' to trigger source registry
def import_datasources():
    rel_path = str(DATASOURCE_PATH).replace("\\", ".")
    for file in os.listdir(DATASOURCE_PATH):
        if file.endswith("py") and "_" not in file and file not in ["__init__.py", "base.py", "implementation-test.py", "registry.py"]:
            src_import_str = rel_path + "." + file.split(".")[0]
            importlib.import_module(src_import_str)


def main():
    logger = init_logger()
    logger.info("="*80)
    for p in PRODUCTS:
        process_products(logger, p)


if __name__ == "__main__":
    import_datasources()
    # for product in PRODUCTS:
    #     for id in product["identifiers"]:
    #         print(id)
    #     print()

    print(SourceRegistry.all())
    pass




    # at some point (either after each succesful fetch or after both for loops have executed), run logic to determine whether to send ntfy or not
