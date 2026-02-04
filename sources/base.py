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

    @abstractmethod
    def fetch_product(self):
        # main method for fetching and parsing data
        data = self.fetch_raw()

        return self.parse(data)
