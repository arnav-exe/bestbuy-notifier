# defines methods and class structure for data sources (bestbuy amazon. etc.)
from abc import ABC, abstractmethod
import logging
import time


class DataSource(ABC):
    source_name: str  # class variable

    def __init__(self, logger: logging.Logger = None):
        # either use provided logger or create null logger
        self.logger = logger or logging.getLogger(self.source_name)

    # return raw data from API
    @abstractmethod
    def fetch_raw(self, identifier: str):
        pass

    # parse raw data into compatible format
    @abstractmethod
    def parse(self, raw_data: dict):
        pass

    # main method for fetching and parsing data
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

    def can_handle(self, retailer_name):
        return self.source_name == retailer_name
