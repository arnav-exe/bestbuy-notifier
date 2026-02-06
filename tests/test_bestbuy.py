import logging

from src.sources.bestbuy import BestbuySource


def get_raw_res():
    bb = BestbuySource()

    logger = logging.getLogger()

    return bb.fetch_raw(6376563, logger)


def get_parsed_res():
    bb = BestbuySource()

    return bb.parse(get_raw_res())


# test that bestbuy class object source_name == "bestbuy"
def test_source_name():
    bb = BestbuySource()

    assert bb.source_name == "bestbuy"


# check that all expected keys are present in response
def test_raw_result_contains_all_keys():
    expected_keys = ['orderable', 'name', 'onSale', 'regularPrice', 'salePrice', 'dollarSavings', 'percentSavings', 'priceUpdateDate', 'url']

    missing = set(expected_keys) - set(get_raw_res())

    assert not missing, f"Missing keys: {missing}"


# check that no item from response is empty str or None
def test_no_res_items_are_empty():
    res = get_raw_res()
    empty = False
    empty_objs = []

    for i in res.items():
        if i[1] == "" or i[1] is None:
            empty = True
            empty_objs.append(i)

    assert not empty, f"API returned 1 or more empty objects: {empty_objs}"


# check that parser is correctly truncating name to 5 words or less
def test_res_parser():
    parsed = get_parsed_res()

    name = parsed["name"].split(" ")

    assert len(name) <= 5, "Name is longer than 5 words, parser failed to truncate"


# test can_handle returns correct bool
def test_can_handle():
    bb = BestbuySource()

    retailer1 = "bestbuy"
    assert bb.can_handle(retailer1), f"{retailer1} can_handle() returned False for {retailer1} (expected: True)"

    retailer2 = "amazon"
    assert not bb.can_handle(retailer2), f"{retailer1} can_handle() returned True for {retailer2} (expected: False)"
