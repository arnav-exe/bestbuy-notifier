import json
import logging
import re
import sys
import time

import requests

try:
    from .base import DataSource
except ImportError:
    from base import DataSource
from ..schema import Product
from .registry import SourceRegistry


NEXT_DATA_RE = re.compile(
    r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
    re.DOTALL,
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def _get_price(price_block):
    if not isinstance(price_block, dict):
        return None
    return price_block.get("price")


class WalmartSource(DataSource):
    source_name = "walmart"

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

    def fetch_raw(self, identifier: str) -> requests.Response:
        self.logger.debug(f"GET request from URL: {identifier}")
        return requests.get(identifier, headers=HEADERS, timeout=30)

    def parse(self, raw_data: str, url: str) -> Product:
        match = NEXT_DATA_RE.search(raw_data)
        if not match:
            raise RuntimeError("Walmart __NEXT_DATA__ payload not found")

        data = json.loads(match.group(1))
        product = data["props"]["pageProps"]["initialData"]["data"]["product"]
        price_info = product.get("priceInfo") or {}

        current_price = _get_price(price_info.get("currentPrice"))
        regular_price = _get_price(price_info.get("wasPrice"))
        if regular_price is None:
            regular_price = current_price

        availability = product.get("availabilityStatusV2") or {}

        return Product(
            identifier=url,
            product_name=" ".join(product["name"].split()[:5]),  # truncate to first 5 worsd
            in_stock=availability.get("value") == "IN_STOCK",
            on_sale=bool(price_info.get("isPriceReduced") and regular_price and current_price and regular_price > current_price),
            sale_price=current_price,
            regular_price=regular_price,
            product_url=f"https://www.walmart.com{product.get('canonicalUrl')}" if product.get("canonicalUrl") else url,
            retailer_name="Walmart",
            retailer_logo="https://upload.wikimedia.org/wikipedia/commons/b/b1/Walmart_logo_%282008%29.svg",
        )

    def fetch_product(self, identifier: str):
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        # exponential backoff params
        retries = 5
        delay = 2
        exp = 0

        try:
            for i in range(retries):
                self.logger.debug(f"Fetching product data for product: {identifier} (attempt: {i})")
                response = self.fetch_raw(identifier)

                if not response.ok:
                    if i >= retries - 1:  # if max retries reached, log error and return None
                        self.logger.warning(f"[{identifier}] HTTP {response.status_code}: {response.reason}")
                        return None

                    # otherwise proceed with exponential backoff
                    time.sleep((delay ** exp) / 2)
                    exp += 1
                    continue

                try:
                    return self.parse(response.text, identifier)
                except Exception as exc:  # retry parsing except if retries is exceeded
                    if i >= retries - 1:
                        self.logger.warning(f"[{identifier}] Failed to parse Walmart page: {exc}")
                        return None
                    time.sleep((delay ** exp) / 2)
                    exp += 1

        except Exception as e:
            self.logger.error(f"[{identifier}] Failed to fetch/parse: {e}")
            return None


# register as DataSource
SourceRegistry.register(WalmartSource)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    url1 = "https://www.walmart.com/ip/50-HISENSE-4K-GOOGLE-TV/17309421750?classType=REGULAR&athbdg=L1300&from=/search"  # out of stock ,on sale
    url2 = "https://www.walmart.com/ip/Microsoft-Xbox-Wireless-Controller-Carbon-Black/15060559533?classType=VARIANT&athbdg=L1200&from=/search"  # in stock on sale

    w = WalmartSource(logger)

    print(w.fetch_product(url1))
    print()
    print(w.fetch_product(url2))
