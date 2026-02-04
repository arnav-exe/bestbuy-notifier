from dataclasses import dataclass


# use class for explicit shape
@dataclass
class Product:
    identifier: str  # EG: sku code, asin code. etc.
    product_name: str
    in_stock: bool
    on_sale: bool
    sale_price: float
    regular_price: float
    product_url: str
    retailer_name: str
    retailer_logo: str  # retailer logo url

    @property
    def dollar_savings(self) -> float:
        if not self.on_sale:
            return 0.0
        return self.regular_price - self.sale_price

    @property
    def percent_savings(self) -> float:
        if not self.on_sale or self.regular_price == 0:
            return 0.0
        return round(self.dollar_savings / self.regular_price * 100, 1)


if __name__ == "__main__":
    # testing
    p = Product("B0FQFB8FMG", "airpods pro 3", True, True, 199.99, 249.99, "https://amazon.com/dp/airpods-pro-3", "https://www.amazon.com/dp/B0FQFB8FMG", "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg")

    print(p.dollar_savings)
    print(p.percent_savings)
