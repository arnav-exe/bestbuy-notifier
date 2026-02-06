from dotenv import load_dotenv
import os
import requests

try:
    from .base import DataSource
except ImportError:
    from base import DataSource

load_dotenv()

FIELDS_ARR = ["orderable", "name", "onSale", "regularPrice", "salePrice", "dollarSavings", "percentSavings", "priceUpdateDate", "url"]
FIELDS = ','.join(FIELDS_ARR)


class BestbuySource(DataSource):
    source_name = "bestbuy"

    def fetch_raw(self, identifier: str, logger) -> dict:
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
            logger.error(e)

        except Exception as e:
            logger.error(e)

        return raw_data.json()

    def parse(self, product: dict) -> dict:
        product["name"] = " ".join(product["name"].split()[:5])  # truncate product name to first 5 words

        return product


if __name__ == "__main__":
    bestbuy = BestbuySource()

    print()

    print(bestbuy.source_name)

    import logging
    logger = logging.getLogger()
    res = bestbuy.fetch_raw(6376563, logger)
