from dotenv import load_dotenv
import os
import sys
import requests

try:
    from .base import DataSource
except ImportError:
    from base import DataSource
from ..schema import Product
from .registry import SourceRegistry

load_dotenv()

FIELDS_ARR = ["sku", "orderable", "name", "onSale", "regularPrice", "salePrice", "dollarSavings", "percentSavings", "priceUpdateDate", "url"]
FIELDS = ','.join(FIELDS_ARR)


class BestbuySource(DataSource):
    source_name = "bestbuy"

    def fetch_raw(self, identifier: str) -> dict:
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

        url = f"https://api.bestbuy.com/v1/products/{identifier}.json?show={FIELDS}&apiKey={os.getenv('BESTBUY_API')}"

        try:
            raw_data = requests.get(url, headers=headers)
            raw_data.raise_for_status()

        except requests.exceptions.HTTPError as e:
            sys.exit(e)

        except Exception as e:
            sys.exit(e)

        return raw_data

    def parse(self, res: dict) -> dict:
        return Product(
            identifier=res["sku"],
            product_name=" ".join(res["name"].split()[:5]),  # product name truncated to 5 words
            in_stock=True if res["orderable"] == "Available" else False,
            on_sale=res["onSale"],
            sale_price=res["salePrice"],
            regular_price=res["regularPrice"],
            product_url=res["url"],
            retailer_name="BestBuy",
            retailer_logo="https://corporate.bestbuy.com/wp-content/uploads/thegem-logos/logo_0717ce843a2125d21ef450e7f05f352e_1x.png"
        )


# manually register datasource to registry
SourceRegistry.register(BestbuySource)

if __name__ == "__main__":
    bestbuy = BestbuySource()

    print()

    print(bestbuy.source_name)

    res = bestbuy.fetch_raw("6376563")
