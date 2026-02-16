def on_sale(product, desired_price: float):
    target_discount = (desired_price - product.sale_price) / desired_price * 100

    return f"""### "{product.product_name}" is in stock and on sale!

**💰 Sale Price:** ${product.sale_price:.2f}  
**🏷️ Original Price:** ${product.regular_price:.2f}  
**🎯 Your Target Price:** ${desired_price:.2f}  

**💵 Sale savings:** ${product.dollar_savings:.2f} ({product.percent_savings:.1f}%)  
**💵 Below your target by:** ${(desired_price - product.sale_price):.2f} ({target_discount:.1f}%)

🔗 [{product.product_url}]({product.product_url})"""


def below_max_price(product, desired_price: float):
    target_discount = (desired_price - product.regular_price) / desired_price * 100

    return f"""### "{product.product_name}" is in stock and within your price target!

**💰 Current Price:** ${product.regular_price:.2f}  
**🎯 Your Target Price:** ${desired_price:.2f}  

**💵 Below your target by:** ${(desired_price - product.regular_price):.2f} ({target_discount:.1f}%)

🔗 [{product.product_url}]({product.product_url})"""


def in_stock(product):
    return f"""### "{product.product_name}" is back in stock!

**💰 Current Price:** ${product.regular_price:.2f}

🔗 [{product.product_url}]({product.product_url})"""


if __name__ == "__main__":
    from .schema import Product
    # test all ntfy templates
    p = Product(
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

    print(on_sale(p, 300.00))
    print()
    print(below_max_price(p, 300))
    print()
    print(in_stock(p))
