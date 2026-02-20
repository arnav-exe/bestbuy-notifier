import subprocess
import logging
import time
import json
from pathlib import Path

try:
    from .base import DataSource
except ImportError:
    from base import DataSource
from ..schema import Product
from .registry import SourceRegistry

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AMAZON_BUDDY_CLI = str(PROJECT_ROOT / "node_modules" / "amazon-buddy" / "bin" / "cli.js")


class AmazonSource(DataSource):
    source_name = "amazon"

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

    def fetch_raw(self, identifier: str) -> subprocess.CompletedProcess:
        cmd = ["node",
               AMAZON_BUDDY_CLI,
               "asin",
               f"{identifier}",
               "--random-ua"]

        self.logger.debug(f"Amazon-buddy GET request: {' '.join(cmd)}")

        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

        return res

    # assume input is stdout (errors shouldve been handled before this point)
    def parse(self, res) -> Product:
        return Product(
            identifier=res["asin"],
            product_name=" ".join(res["title"].split()[:5]),
            in_stock=res["item_available"],
            on_sale=res["price"]["discounted"],
            sale_price=res["price"]["current_price"],
            regular_price=res["price"]["before_price"],
            product_url=res["url"],
            retailer_name="Amazon",
            retailer_logo="https://upload.wikimedia.org/wikipedia/commons/4/41/Amazon_PNG6.png"
        )


    def fetch_product(self, identifier: str):
        # exponential backoff params
        retries = 10
        delay = 2
        exp = 0

        try:
            for i in range(retries):
                self.logger.debug(f"Fetching product data for product: {identifier} (attempt: {i})")

                try:
                    response = self.fetch_raw(identifier)
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"[{identifier}] Subprocess timed out (attempt {i})")
                    if i == retries - 1:
                        return None
                    sleep_time = (delay ** exp) / 2
                    time.sleep(sleep_time)
                    exp += 1
                    continue

                if response.stderr or response.stdout.startswith("Error:"):
                    if i == retries - 1:  # if max retries reached log and move on
                        self.logger.warning(f"[{identifier}] amazon-buddy error: stderr={response.stderr.strip()}, stdout={response.stdout.strip()}")
                        return None

                    else:  # exp backoff wait
                        sleep_time = (delay ** exp) / 2
                        time.sleep(sleep_time)
                        exp += 1

                else:  # if response
                    break

            # parse the JSON output — amazon-buddy returns a JSON array
            data = json.loads(response.stdout)
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            product = self.parse(data)
            return product

        except Exception as e:
            self.logger.error(f"[{identifier}] Failed to fetch/parse: {e}")
            return None


SourceRegistry.register(AmazonSource)


if __name__ == "__main__":
    from ..utils import jprint

    cmd = ["node",
           AMAZON_BUDDY_CLI,
           "asin",
           "1259642232",
           "--random-ua"]

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    jprint(res.stdout)
    print()
    jprint(res.stderr)
