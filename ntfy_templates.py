from datetime import datetime
from dateutil.parser import parse


def get_days_hours(seconds: float):
    days, seconds = divmod(seconds, 86400)
    hours = round(seconds / 3600)

    return days, hours


def calc_time_diff(time_str):
    time_obj = parse(time_str)
    current_time = parse(datetime.now().isoformat())

    delta_s = (current_time - time_obj).total_seconds()

    return get_days_hours(delta_s)


def sale_ntfy(name, sale_price, regular_price, dollar_savings, percent_savings, url, price_update_date):
    days, hours = calc_time_diff(price_update_date)
    relative_time_str = f"{int(days)} days, {hours} hours ago"

    return f"""### {name} is on sale!

**New Price:** ${sale_price}

**Original Price:** ${regular_price}

**Discount Amount:** ${dollar_savings}

**Discount Percent:** {percent_savings}%

[{url}]({url})

---

Price was last updated on {price_update_date} ({relative_time_str})"""


def non_sale_ntfy(name, regular_price, desired_price, url, price_update_date):
    days, hours = calc_time_diff(price_update_date)
    relative_time_str = f"{int(days)} days, {hours} hours ago"

    if regular_price < desired_price:
        dollar_savings = desired_price - regular_price
        dollar_savings = round(dollar_savings, 2)
        percent_savings = regular_price / desired_price * 100
        percent_savings = round(percent_savings, 1)

        return f"""### {name} is now in stock!

**Price:** ${regular_price}

**Your Desired Price:** ${desired_price}

**Dollar Savings:** ${dollar_savings}

**Percent Savings:** {percent_savings}%

[{url}]({url})

---

Price was last updated on {price_update_date} ({relative_time_str})"""

    else:
        return f"""### {name} is now in stock!

**Price:** ${regular_price}

**Your Desired Price:** ${desired_price}

[{url}]({url})

---

Price was last updated on {price_update_date} ({relative_time_str})"""


if __name__ == "__main__":
    # test send of sale ntfy
    res = sale_ntfy(
        "airpods pro 3",
        199.99,
        249.99,
        50.0,
        "20.0",
        "https://api.bestbuy.com/click/-/6376563/pdp",
        "2026-01-23T00:00:54"
    )

    with open("temp_sale.md", "w", encoding="utf-8") as f:
        f.write(res)

    # test send of non sale ntfy
    res = non_sale_ntfy(
        "LG UltraGear 27",
        349.99,
        400,
        "https://api.bestbuy.com/click/-/6575404/pdp",
        "2025-12-18T02:01:15"
    )

    with open("temp_non_sale.md", "w", encoding="utf-8") as f:
        f.write(res)


# TODO: add type hinting to function defs
