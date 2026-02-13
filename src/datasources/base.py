# defines methods and class structure for data sources (bestbuy amazon. etc.)
from abc import ABC, abstractmethod


class DataSource(ABC):
    source_name: str  # class variable

    @abstractmethod
    def fetch_raw(self, identifier: str):
        # return raw data from API
        pass

    @abstractmethod
    def parse(self, raw_data: dict):
        # parse raw data into compatible format
        pass

    def fetch_product(identifier: str):
        # main method for fetching and parsing data
        # data = self.fetch_raw(identifier).json()
        #
        # return self.parse(data)  # returns Product obj (as defined in schema.py)
        from ..schema import Product

        return Product(
            "B0FQFB8FMG",
            "airpods pro 3",
            True,
            True,
            199.99,
            249.99,
            "https://amazon.com/dp/airpods-pro-3",
            "amazon",
            "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
        )

    def test():
        print("test function triggered!")

    def can_handle(self, retailer_name):
        return self.source_name == retailer_name
