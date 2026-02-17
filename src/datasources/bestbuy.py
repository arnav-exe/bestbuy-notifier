from dotenv import load_dotenv
import os
import requests
import logging
import time

try:
    from .base import DataSource
except ImportError:
    from base import DataSource
from ..schema import Product
from .registry import SourceRegistry

load_dotenv()

FIELDS_ARR = ["sku", "orderable", "name", "onSale", "regularPrice", "salePrice", "url"]
FIELDS = ','.join(FIELDS_ARR)


class BestbuySource(DataSource):
    source_name = "bestbuy"

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

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

        self.logger.debug(f"GET request from URL: {url}")

        return requests.get(url, headers=headers)

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

    def fetch_product(self, identifier: str):
        # exponential backoff params
        retries = 10
        delay = 2
        exp = 0

        try:
            for i in range(retries):
                self.logger.debug(f"Fetching product data for product: {identifier} (attempt: {i})")
                response = self.fetch_raw(identifier)

                if not response.ok:
                    if i == retries - 1:  # if max retries reached, log error and return None
                        self.logger.warning(f"[{identifier}] HTTP {response.status_code}: {response.reason}")
                        return None

                    else:  # otherwise continue with exponential backoff
                        sleep_time = (delay ** exp) / 2
                        time.sleep(sleep_time)
                        exp += 1

                else:  # if response==200
                    break

            product = self.parse(response.json())
            return product

        except Exception as e:
            self.logger.error(f"[{identifier}] Failed to fetch/parse: {e}")
            return None



# manually register datasource to registry
SourceRegistry.register(BestbuySource)
