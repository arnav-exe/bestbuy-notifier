# defines methods and class structure for data sources (bestbuy amazon. etc.)
from abc import ABC, abstractmethod
import logging


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
        try:
            self.logger.debug(f"Fetching product data for product: {identifier}")
            response = self.fetch_raw(identifier)

            if not response.ok:
                self.logger.warning(f"[{identifier}] HTTP {response.status_code}: {response.reason}")
                return None

            product = self.parse(response.json())
            return product

        except Exception as e:
            self.logger.error(f"[{identifier}] Failed to fetch/parse: {e}")
            return None

    def can_handle(self, retailer_name):
        return self.source_name == retailer_name
