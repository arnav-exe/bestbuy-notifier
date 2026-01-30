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


def main(asin):
    if sys.platform == "win32":
        subprocess.run(["node_modules\\.bin\\amazon-buddy", "asin", asin], shell=True)
    else:
        subprocess.run(["node_modules\\.bin\\amazon-buddy", "asin", asin])


if __name__ == "__main__":
    asin = PRODUCTS[0]["amazon_asin"]
    main(asin)
