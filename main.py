import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import importlib
import multiprocessing
import logging
from logging.handlers import QueueHandler, QueueListener

from src.send_ntfy import post_ntfy
from src.ntfy_templates import on_sale, below_max_price, in_stock
from src.log_handler import init_logger
from src.datasources.registry import SourceRegistry

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
DATASOURCE_PATH = PROJECT_ROOT / "src" / "datasources"

# ensure project root is on sys.path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WATCHLIST = [
    {  # lenovo legion go 2 1TB
        "identifiers": {
            "bestbuy": "6643145",
            "amazon": "B0G573TMZS"
        },
        "user_max_price": None,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },
    {  # lenovo legion go 2 2TB
        "identifiers": {
            "bestbuy": "6666376",
            "amazon": "B0FYR2V7ZB",
            "lenovo": "https://www.lenovo.com/us/en/p/handheld/legion-go-gen-2/83n0000aus"
        },
        "user_max_price": None,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    },
    {  # LG 27 inch 1440p 180hz monitor (TESTING)
        "identifiers": {
            "bestbuy": 6575404,
        },
        "user_max_price": 350,
        "ntfy_topic": os.getenv("NTFY_TOPIC_URL")
    }
]


# auto import all modules inside 'src/datasources' to trigger source registry
def import_datasources(logger):
    SourceRegistry.set_logger(logger)

    for file in os.listdir(DATASOURCE_PATH):
        if file.endswith("py") and "_" not in file and file not in ["__init__.py", "base.py", "implementation-test.py", "registry.py"]:
            module_name = f"src.datasources.{file.split('.')[0]}"
            importlib.import_module(module_name)
            logger.info(f"Registered datasource: {file.split('.')[0]}")


# create child logger that sends all records to parent via queue system
def _init_child_logger(log_queue: multiprocessing.Queue, name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(QueueHandler(log_queue))
    logger.propagate = False

    return logger


# worker func - re imports the datasource, fetches product and sends noti
def _process_identifier(log_queue, src_name, identifier, user_max_price, ntfy_topic):
    pid = os.getpid()
    logger = _init_child_logger(log_queue, f"bestbuy-notifier.{src_name}.{identifier}")

    logger.info(f"[PID {pid}] Child process started for {src_name}:{identifier}")

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    # re register datasource in this child process
    SourceRegistry.set_logger(logger)

    try:
        importlib.import_module(f"src.datasources.{src_name}")

    except ModuleNotFoundError:
        logger.error(f"[PID {pid}] Could not import datasource module for '{src_name}'")
        return

    if src_name not in SourceRegistry.all():
        logger.error(f"[PID {pid}] Datasource '{src_name}' did not register after import")
        return

    logger.info(f"[PID {pid}] Processing: {src_name} | {identifier}")
    logger.info("-" * 60)

    # fetch product data
    data_fetcher = SourceRegistry.get(src_name)
    product = data_fetcher.fetch_product(identifier)

    if product is None:
        logger.warning(f"[PID {pid}] fetch_product returned None, skipping")
        return

    logger.info(f"[PID {pid}] Fetched: {product.product_name} | Retailer: {product.retailer_name}")

    if not product.in_stock:
        logger.info(f"[PID {pid}] Out of stock, skipping")
        return

    # check if data meets user reqs
    if user_max_price is not None:
        if product.on_sale and product.sale_price <= user_max_price:
            on_sale_body = on_sale(product, user_max_price)
            post_ntfy(on_sale_body, product.product_url, product.retailer_name, product.retailer_logo, ntfy_topic)
            logger.info(f"[PID {pid}] Sent ON SALE notification for {identifier}")

        elif product.regular_price <= user_max_price:
            below_max_price_body = below_max_price(product, user_max_price)
            post_ntfy(below_max_price_body, product.product_url, product.retailer_name, product.retailer_logo, ntfy_topic)
            logger.info(f"[PID {pid}] Sent BELOW MAX PRICE notification for {identifier}")

        else:
            logger.info(f"[PID {pid}] Price ${product.regular_price} exceeds max ${user_max_price}, skipping")

    else:
        in_stock_body = in_stock(product)
        post_ntfy(in_stock_body, product.product_url, product.retailer_name, product.retailer_logo, ntfy_topic)
        logger.info(f"[PID {pid}] Sent IN STOCK notification for {identifier}")

    logger.info(f"[PID {pid}] Child process finished for {src_name}:{identifier}")


def main(logger):
    main_pid = os.getpid()
    sources = SourceRegistry.all()
    logger.info(f"[PID {main_pid}] Available datasources: {list(sources.keys())}")

    # set up log queue + listener
    # listener runs in main process and drains queue into existing file handler(s)
    log_queue = multiprocessing.Queue()
    listener = QueueListener(log_queue, *logger.handlers, respect_handler_level=True)
    listener.start()

    try:
        for idx, item in enumerate(WATCHLIST):
            logger.info("")
            logger.info(f"[PID {main_pid}] WATCHLIST item {idx + 1}/{len(WATCHLIST)}")

            processes: list[multiprocessing.Process] = []

            for src_name, identifier in item["identifiers"].items():
                if src_name not in sources:
                    logger.debug(f"No datasource for '{src_name}', skipping")
                    continue

                p = multiprocessing.Process(
                    target=_process_identifier,
                    args=(
                        log_queue,
                        src_name,
                        identifier,
                        item["user_max_price"],
                        item["ntfy_topic"],
                    ),
                    name=f"{src_name}-{identifier}",
                )
                processes.append(p)
                p.start()
                logger.info(f"[PID {main_pid}] Spawned '{p.name}' (PID {p.pid})")

            logger.info(f"[PID {main_pid}] Waiting for {len(processes)} process(es)...")

            # wait for all identifier processes to finish before moving to next watchlist item
            for p in processes:
                p.join()
                status = "OK" if p.exitcode == 0 else f"FAILED (exit code {p.exitcode})"
                logger.info(f"[PID {main_pid}] Process '{p.name}' (PID {p.pid}) joined — {status}")

            logger.info(f"[PID {main_pid}] All processes for WATCHLIST item {idx + 1} complete")

    finally:
        listener.stop()


if __name__ == "__main__":
    logger = init_logger()

    import_datasources(logger)
    main(logger)
