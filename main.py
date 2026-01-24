import requests
import os
from dotenv import load_dotenv

from send_email_smtp import send_email
from email_templates import sale_email, non_sale_email

load_dotenv()

PRODUCTS = [
    {  # airpods pro 3
        "sku": 6376563,
        "desired_price": 200,
        "email_to": os.getenv("RECIPIENT_ADDRESS")
    },
    {  # lenovo legion go 2
        "sku": 6643145,
        "desired_price": 1500,
        "email_to": os.getenv("RECIPIENT_ADDRESS")
    },
    {  # LG 27 inch 1440p 180hz monitor (TESTING)
        "sku": 6575404,
        "desired_price": 400,
        "email_to": os.getenv("RECIPIENT_ADDRESS")
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

    sent_email = False

    if product["orderable"] == "Available" and product["onSale"]:  # if sale
        email_body = sale_email(product_name, product["salePrice"], product["regularPrice"], product["dollarSavings"], product["percentSavings"], product["url"], product["priceUpdateDate"])

        send_email(
            user_product_data["email_to"],
            f"BestBuy Alert - {product_name} is in stock and {product['percentSavings']}% off!",
            email_body
        )
        sent_email = True

    # if not sale but price <= desired price
    elif product["orderable"] == "Available" and product["regularPrice"] <= user_product_data["desired_price"]:
        email_body = non_sale_email(product_name, product["regularPrice"], user_product_data["desired_price"], product["url"], product["priceUpdateDate"])
        send_email(
            user_product_data["email_to"],
            f"BestBuy Alert - {product_name} is in stock!",
            email_body
        )
        sent_email = True

    return sent_email


def main():
    for p in PRODUCTS:
        url = f'https://api.bestbuy.com/v1/products/{p["sku"]}.json?show={FIELDS}&apiKey={os.getenv('BESTBUY_API')}'

        # fetch product data from API
        data = get_product_data(url)

        # data parsing logic
        sent_email = parse_product_data(data, p)

        if sent_email:
            print(f"Sent email for product: {p['sku']}")
        else:
            print(f"Email NOT sent for product: {p['sku']}")


if __name__ == "__main__":
    main()
