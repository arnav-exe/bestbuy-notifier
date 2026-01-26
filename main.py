import requests
import time
import os
from dotenv import load_dotenv

from send_ntfy import post_ntfy
from ntfy_templates import sale_ntfy, non_sale_ntfy
from log_handler import init_logger

load_dotenv()

PRODUCTS = [
    {  # airpods pro 3
        "sku": 6376563,
        "desired_price": 200,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },
    {  # lenovo legion go 2
        "sku": 6643145,
        "desired_price": 1500,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },
    {  # LG 27 inch 1440p 180hz monitor (TESTING)
        "sku": 6575404,
        "desired_price": 400,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    }
]

FIELDS_ARR = ["orderable", "name", "onSale", "regularPrice", "salePrice", "dollarSavings", "percentSavings", "priceUpdateDate", "url"]
FIELDS = ','.join(FIELDS_ARR)


def get_product_data(url: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.bestbuy.com/",
        "Origin": "https://www.bestbuy.com",
    }

    try:
        raw_data = requests.get(url, headers=headers)
        raw_data.raise_for_status()

    except requests.exceptions.HTTPError as e:  # fail
        pass

    except Exception as e:
        pass

    # success
    data = raw_data.json()

    return data


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


def main():
    logger = init_logger()
    logger.info("="*80)
    for p in PRODUCTS:
        logger.info("")
        # exponential backoff params
        retries = 10
        delay = 2
        exp = 0

        url = f"https://api.bestbuy.com/v1/products/{p["sku"]}.json?show={FIELDS}&apiKey={os.getenv('BESTBUY_API')}"

        # fetch product data from API
        for i in range(retries):  # exponential backoff
            data = get_product_data(url)

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
            logger.info(f"Sent ntfy notification for product: {p['sku']}")

        else:
            logger.info(f"Did NOT send ntfy notification for product {p['sku']} (either out of stock or above desired price)")

        logger.info("")
        logger.info("="*80)


if __name__ == "__main__":
    main()
