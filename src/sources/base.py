# defines methods and class structure for data sources (bestbuy amazon. etc.)
from abc import ABC, abstractmethod


class DataSource(ABC):
    source_name: str

    @abstractmethod
    def fetch_raw(self):
        # return raw data from API
        pass

    @abstractmethod
    def parse(self, raw_data: dict):
        # parse raw data into compatible format
        pass

    def fetch_product(self):
        # main method for fetching and parsing data
        data = self.fetch_raw().json()

        return self.parse(data)

    def can_handle(self, retailer_name):
        return self.source_name == retailer_name
