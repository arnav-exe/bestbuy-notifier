import asyncio
import json
import re
import sys
import logging
import time
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

try:
    from .base import DataSource
except ImportError:
    from base import DataSource
from ..schema import Product
from .registry import SourceRegistry


IN_STOCK_URIS = frozenset({
    "http://schema.org/InStock",
    "https://schema.org/InStock",
    "http://schema.org/LimitedAvailability",
    "https://schema.org/LimitedAvailability",
})

NOT_IN_STOCK_RE = re.compile(
    r"available\s+soon|coming\s+soon|notify\s+me|out\s+of\s+stock"
    r"|sold\s+out|no\s+longer\s+available|unavailable",
    re.IGNORECASE,
)
EST_VALUE_RE = re.compile(r"Est\s+Value[^$]*\$([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)
PERCENT_OFF_RE = re.compile(r"\d+\s*%\s*off", re.IGNORECASE)

SCAN_WINDOW = 1000  # product info usually appears within first 400 chars of <main> - restrict around that

INJECTED_RE = re.compile(
    r'<script[^>]+type=["\']text/x-scraper-data["\'][^>]*>([\s\S]*?)</script>',
    re.IGNORECASE,
)

_JS = """
(async () => {
    Array.from(document.querySelectorAll('button, [role="button"]')).forEach(btn => {
        const lbl = (btn.getAttribute('aria-label') || btn.textContent || '')
                    .toLowerCase().trim();
        if (lbl.includes('close') || lbl === 'x' || lbl === '\u00d7') {
            try { btn.click(); } catch (_) {}
        }
    });

    // wait for popups and smartsales.lenovo.com price widget to render
    await new Promise(r => setTimeout(r, 1500));

    const out = { name: null, price: null, availability: null, mainText: '' };

    for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
        let d;
        try { d = JSON.parse(s.textContent); } catch (_) { continue; }
        // get Product block from pdp
        if (d['@type'] === 'Product' && d.offers) {
            out.name         = d.name                ?? null;
            out.price        = d.offers.price        ?? null;
            out.availability = d.offers.availability ?? null;
            break;
        }
    }

    // exclude header/footer/popup text (sometimes returns other product prices)
    const mainEl = document.querySelector('main');
    out.mainText = mainEl ? mainEl.innerText : document.body.innerText;

    const tag = document.createElement('script');
    tag.type        = 'text/x-scraper-data';
    tag.textContent = JSON.stringify(out);
    document.body.appendChild(tag);
})();
"""


def _parse_price(value):
    if value is None:
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


class LenovoSource(DataSource):
    source_name = "lenovo"

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)


    async def fetch_raw(self, identifier: str) -> dict:
        browser_cfg = BrowserConfig(
            browser_type="undetected",  # avoid bot detection
            headless=True,
            verbose=False
        )

        run_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            js_code=_JS,
            delay_before_return_html=3.0,
            page_timeout=60_000,
            verbose=False,
        )

        self.logger.debug(f"crawl4ai GET request: {identifier}")

        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=identifier, config=run_cfg)

        return result


    def parse(self, raw_data, url):
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as exc:
            self.logger.warning(f"Failed to parse injected json: {exc}")

        if data.get("price") is None:
            self.logger.warning("No price found in json-ld")

        scan = data.get("mainText", "")[:SCAN_WINDOW]
        em = EST_VALUE_RE.search(scan)
        is_on_sale = bool(em or PERCENT_OFF_RE.search(scan))
        current_price = _parse_price(data["price"])
        regular_price = _parse_price(em.group(1)) if (is_on_sale and em) else current_price

        return Product(
            identifier=url,
            product_name=" ".join(data.get("name").split()[:5]),
            in_stock=(data.get("availability") in IN_STOCK_URIS) and not NOT_IN_STOCK_RE.search(scan),
            on_sale=is_on_sale,
            regular_price=regular_price,
            sale_price=current_price,
            product_url=url,
            retailer_name="Lenovo",
            retailer_logo="https://upload.wikimedia.org/wikipedia/commons/b/bd/Branding_lenovo-logo_lenovologoposred_low_res.png"
        )


    def fetch_product(self, identifier: str):
        # enforce utf-8 encoding
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        retries = 10
        delay = 2
        exp = 0

        try:
            m = None

            for i in range(retries):
                self.logger.debug(f"Fetching product data for product: {identifier} (attempt: {i})")

                response = asyncio.run(self.fetch_raw(identifier))

                if not response.success:
                    if i == retries - 1:
                        self.logger.warning(f"Failed to load page: {response.error_message}")
                        return None
                    else:
                        sleep_time = (delay ** exp) / 2
                        time.sleep(sleep_time)
                        exp += 1
                        continue

                if not (m := INJECTED_RE.search(response.html or "")):  # holy walrus operator
                    if i == retries - 1:
                        self.logger.warning("Injected data not found in html")
                        return None
                    else:
                        sleep_time = (delay ** exp) / 2
                        time.sleep(sleep_time)
                        exp += 1
                        continue

                # success
                break

            if m is None:
                self.logger.warning("No valid response after all retries")
                return None

            product = self.parse(m.group(1), identifier)

            return product

        except Exception as e:
            self.logger.error(f"[{identifier}] Failed to fetch/parse: {e}")
            return None


# register as DataSource
SourceRegistry.register(LenovoSource)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    l = LenovoSource(logger)

    url = "https://www.lenovo.com/us/en/p/handheld/legion-go-gen-2/83n0000aus"
    print(l.fetch_product(url))
