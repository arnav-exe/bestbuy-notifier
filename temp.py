import subprocess
import sys
import os


PRODUCTS = [
    {  # airpods pro 3
        "bestbuy_sku": 6376563,
        "amazon_asin": "B0FQFB8FMG",
        "desired_price": 200,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },
    {  # lenovo legion go 2
        "bestbuy_sku": 6643145,
        "desired_price": 1500,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },
    {  # LG 27 inch 1440p 180hz monitor (TESTING)
        "bestbuy_sku": 6575404,
        "desired_price": 400,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    }
]


def main(asin):
    try:
        if sys.platform == "win32":
            subprocess.run(["node_modules\\.bin\\amazon-buddy", "asin", asin, "--random-ua"], check=True, shell=True)
        else:
            subprocess.run(["node_modules/.bin/amazon-buddy", "asin", asin, "--random-ua"], check=True)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    # asin = PRODUCTS[0]["amazon_asin"]
    # main(asin)

    p1 = PRODUCTS[0]

    if "amazon_asin" in p1.keys():
        print("true")


"""
AMAZON URL TEMPLATE:
    https://www.amazon.com/dp/{amazon_asin}
"""
