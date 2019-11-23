from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import datetime

import string
from re import sub
from bson import Decimal128

from server.db import save_html_dump, save_parsed_products, update_product


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)



def all_plugins_update():
    url = "https://www.uaudio.com/uad-plugins/all-plugins.html"

    raw_html = simple_get(url)
    save_html_dump(url, raw_html)

    html = BeautifulSoup(raw_html, 'html.parser')

    products = [product for product in html.select("#products-list")[0].children if hasattr(product, 'attrs')]

    parsed_products = []
    fetch_start_time = datetime.utcnow()

    for product in products:
        try:
            data_name = product.attrs.get("data-name", None)
            data_id = product.attrs.get("data-id", None)
            price_span = product.select("span[id^='product-price']")

            if price_span is not None and len(price_span):
                price = price_span[0].contents[0].translate({ord(c): None for c in string.whitespace})
                if not len(price) or price[0] != '$':
                    price = price_span[1].contents[1].contents[0]

            else:
                price = '$0.00'

            old_price_span = product.select("#old-price-{}".format(data_id))
            if old_price_span is not None and len(old_price_span):
                old_price = old_price_span[0].contents[0].translate({ord(c): None for c in string.whitespace})
            else:
                old_price = 'N/A'

            parsed_products.append({
                "name": data_name,
                "data_id": data_id,
                "old-price": {
                    "string": old_price,
                    "decimal": Decimal128(sub(r'[^\d.]', '', old_price)) if old_price != 'N/A' else None,
                },
                "price": {
                    "string": price,
                    "decimal": Decimal128(sub(r'[^\d.]', '', price or '$0.00')),
                },
                "timestamp": fetch_start_time,
            })
        except (TypeError):
            continue

    save_parsed_products(url, parsed_products)

    operations = []
    for product in parsed_products:
        data_id = product['data_id']
        operations.append(update_product(data_id, product))

    return operations

# STEPS:
# 1: Raw data dump
# 2: Parse products
# 3: Dump parsed products
# 4: Update product histories

# Collections:
#   html_dumps
#   parse_events
#   products



