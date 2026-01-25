import requests
import time
import os
from dotenv import load_dotenv

from send_ntfy import post_ntfy
from ntfy_templates import sale_ntfy, non_sale_ntfy

load_dotenv()

PRODUCTS = [
    # {  # airpods pro 3
    #     "sku": 6376563,
    #     "desired_price": 200,
    #     "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    # },
    # {  # lenovo legion go 2
    #     "sku": 6643145,
    #     "desired_price": 1500,
    #     "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    # },
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
        print(raw_data.text)
        raise SystemExit(f"HTTP Error:\n{e}")

    except Exception as e:
        raise SystemExit(f"Other Error:\n{e}")

    # success
    data = raw_data.json()

    return data


def parse_product_data(product: dict, user_product_data: dict):
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
    # implement exponential backoff with 10 retries (starting at 1s)

    for p in PRODUCTS:
        url = f'https://api.bestbuy.com/v1/products/{p["sku"]}.json?show={FIELDS}&apiKey={os.getenv('BESTBUY_API')}'

        # TODO: add exponential backoff to API fetching (20 total retries)
        # fetch product data from API
        data = get_product_data(url)

        # data parsing logic
        sent_ntfy = parse_product_data(data, p)

        if sent_ntfy:
            print(f"Sent ntfy notification for product: {p['sku']}")
        else:
            print(f"ntfy notification NOT sent for product: {p['sku']}")

        time.sleep(0.5)


if __name__ == "__main__":
    main()
