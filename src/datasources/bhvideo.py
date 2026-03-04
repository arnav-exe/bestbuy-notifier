import asyncio
import json
import logging
import os
import platform
import re
import sys
import time
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

try:
    from .base import DataSource
except ImportError:
    from base import DataSource
from ..schema import Product
from .registry import SourceRegistry



PROFILE_DIR = Path(__file__).parent / ".browser_profile"

IN_STOCK_SUFFIXES = frozenset({"/InStock", "/LimitedAvailability", "/OnlineOnly", "/BackOrder"})

JSON_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>\s*(.*?)\s*</script>',
    re.DOTALL | re.IGNORECASE,
)
LIST_PRICE_LABEL_RE = re.compile(
    r'(?:list\s+price|msrp|manufacturer[\'s]*\s+(?:suggested\s+)?(?:retail\s+)?price'
    r'|regular\s+price|orig(?:inal)?\s+price|was\s*:?|before\s+discount)'
    r'[^$\d]{0,30}\$\s*([\d,]+(?:\.\d{1,2})?)',
    re.IGNORECASE,
)
DOLLAR_RE = re.compile(r'\$\s*([\d,]+(?:\.\d{1,2})?)')


def _extract_product_jsonld(html):
    for m in JSON_LD_RE.finditer(html):
        try:
            data = json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            continue
        for obj in (data if isinstance(data, list) else [data]):
            if isinstance(obj, dict) and obj.get("@type") == "Product":
                return obj
    return None


def _find_list_price(html, current_price):
    for m in LIST_PRICE_LABEL_RE.finditer(html):
        try:
            candidate = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        if candidate > current_price:
            return candidate

    # Fall back to scanning all dollar amounts in the pricing container
    idx = html.find('data-selenium="pricingContainer"')
    if idx == -1:
        return None
    start = html.rfind("<", 0, idx)
    if start == -1:
        return None
    region = html[start: start + 2000]
    amounts = [float(m.group(1).replace(",", "")) for m in DOLLAR_RE.finditer(region)]
    if higher := [v for v in amounts if v > current_price * 1.01]:  # walrus operator bomboclaat
        return max(higher)
    return None


# start Xvfb virtual framebuffer on headless Linux so headed browser can open
# returns display object (call .stop() when done) or none
def _start_virtual_display():
    if platform.system() != "Linux" or os.environ.get("DISPLAY"):
        return None
    try:
        from pyvirtualdisplay import Display  # noqa: PLC0415
        display = Display(visible=False, size=(1280, 720))
        display.start()
        return display
    except Exception:
        return None


async def _fetch_html(url, headless):
    async with AsyncWebCrawler(config=BrowserConfig(
        browser_type="chromium",
        headless=headless,
        use_persistent_context=True,
        user_data_dir=str(PROFILE_DIR),
        verbose=False,
    )) as crawler:
        result = await crawler.arun(url=url, config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            delay_before_return_html=4.0,
            page_timeout=60_000,
            verbose=False,
        ))
    if not result.success:
        return None
    html = result.html or ""

    # cloudflare chal page wont have jsonld
    return html if "application/ld+json" in html else None


class BHVideoSource(DataSource):
    source_name = "bhvideo"

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)


    async def fetch_raw(self, identifier: str) -> str:
        PROFILE_DIR.mkdir(exist_ok=True)

        self.logger.debug(f"crawl4ai GET request (headless): {identifier}")
        html = await _fetch_html(identifier, headless=True)

        if html is None:
            self.logger.debug(f"Headless fetch blocked, retrying in headed mode: {identifier}")
            display = _start_virtual_display()
            try:
                html = await _fetch_html(identifier, headless=False)
            finally:
                if display:
                    display.stop()

        return html


    def parse(self, raw_data: str, url: str) -> Product:
        if not (product_ld := _extract_product_jsonld(raw_data)):  # another walrus operator (am i the goat??)
            self.logger.warning("No schema.org/Product JSON-LD found in HTML")
            raise RuntimeError("No schema.org/Product JSON-LD found. The page structure may have changed.")

        offers = product_ld.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        if not isinstance(offers, dict):
            offers = {}

        raw = offers.get("price")
        try:
            current_price = float(str(raw).replace(",", "").replace("$", "").strip()) if raw is not None else None
        except (ValueError, TypeError):
            current_price = None

        if current_price is None:
            self.logger.warning(f"Could not parse price: {raw!r}")

        list_price = _find_list_price(raw_data, current_price) if current_price is not None else None

        return Product(
            identifier=url,
            product_name=product_ld.get("name"),
            in_stock=any(offers.get("availability", "").endswith(s) for s in IN_STOCK_SUFFIXES),
            on_sale=list_price is not None,
            regular_price=list_price if list_price is not None else current_price,
            sale_price=current_price,
            product_url=url,
            retailer_name="B&H Photo Video",
            retailer_logo="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/B%26H_Foto_%26_Electronics_Logo.svg/960px-B%26H_Foto_%26_Electronics_Logo.svg.png",
        )


    def fetch_product(self, identifier: str):
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        retries = 0
        delay = 2
        exp = 0

        try:
            for i in range(retries):
                self.logger.debug(f"Fetching product data for product: {identifier} (attempt: {i})")

                html = asyncio.run(self.fetch_raw(identifier))

                if html is not None:
                    break

                if i >= retries - 1:
                    self.logger.warning("Failed to load page: Cloudflare blocked in both headless and headed modes")
                    return None

                time.sleep((delay ** exp) / 2)
                exp += 1

            return self.parse(html, identifier)

        except Exception as e:
            self.logger.error(f"[{identifier}] Failed to fetch/parse: {e}")
            return None


SourceRegistry.register(BHVideoSource)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    url = "https://www.bhphotovideo.com/c/product/1920305-REG/lenovo_83n0000aus_legion_go_2_handheld.html"

    b = BHVideoSource(logger)
    print(b.fetch_product(url))
