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


def sale_email(name, sale_price, regular_price, dollar_savings, percent_savings, url, price_update_date):
    days, hours = calc_time_diff(price_update_date)
    relative_time_str = f"{int(days)} days, {hours} hours ago"

    return f"""
<div style="margin-left: 2em; margin-right: 2em;">
    <h1>{name} is on sale!</h1>

    <p>New Price: ${sale_price}</p>
    <p>Original Price: ${regular_price}</p>
    <p>Discount Amount: ${dollar_savings}</p>
    <p>Discount Percent: ${percent_savings}</p>

    <a href="{url}">Click here to visit product page</a>

    <br>
    <br>

    <p>Price was last updated on {price_update_date} ({relative_time_str})</p>
</div>
"""


def non_sale_email(name, regular_price, desired_price, url, price_update_date):
    days, hours = calc_time_diff(price_update_date)
    relative_time_str = f"{int(days)} days, {hours} hours ago"

    return f"""
<div style="margin-left: 2em; margin-right: 2em;">
    <h1>{name} is in stock!</h1>

    <p>Price: ${regular_price}</p>
    <p>Your Desired Price: ${desired_price}</p>

    <a href="{url}">Click here to visit product page</a>

    <br>
    <br>

    <p>The price was last updated on {price_update_date} ({relative_time_str}).</p>
</div>
"""


if __name__ == "__main__":
    res = sale_email(
        "airpods pro 3",
        199.99,
        249.99,
        50.0,
        "20.0",
        "https://api.bestbuy.com/click/-/6376563/pdp",
        "2026-01-23T00:00:54"
    )

    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(res)

# TODO: add type hinting to function defs
