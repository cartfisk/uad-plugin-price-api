from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
from datetime import datetime
from decimal import Decimal

from server.constants import MONGO_ADDRESS, MONGO_PORT

COLLECTIONS = {
    'HTML_DUMPS': 'html_dumps',
    'PARSED_PRODUCTS': 'parsed_products',
    'PRODUCTS': 'products',
}

HTML_DUMP_FIELDS = [
    'timestamp',
    'html_data',
    'url',
]

PARSED_PRODUCT_FIELDS = [
    'timestamp',
    'product_json_data',
    'url',
]

PRODUCT_FIELDS = [
    'name', # string
    'data_id', #datetime
    'current_price', #decimal
    'lowest_price', # { decimal, datetime }
    'price_history' # list[{ decimal, datetime }]
    'is_lowest', # boolean
    'first_seen', # datetime
]


def get_collection(collection):
    client = MongoClient('{}:{}'.format(MONGO_ADDRESS, MONGO_PORT))
    db=client.universal_audio
    return db[collection]


def save_html_dump(url, raw_html):
    col = get_collection(COLLECTIONS['HTML_DUMPS'])

    doc = {
        'timestamp': datetime.utcnow(),
        'html_data': raw_html,
        'url': url,
    }

    insert = col.insert_one(doc)
    return insert


def save_parsed_products(url, parsed_products):
    col = get_collection(COLLECTIONS['PARSED_PRODUCTS'])

    doc = {
        'timestamp': datetime.utcnow(),
        'product_json_data': parsed_products,
        'url': url,
    }

    insert = col.insert_one(doc)
    return insert


def update_product(data_id, product_data):
    col = get_collection(COLLECTIONS['PRODUCTS'])

    doc = col.find_one({'data_id': data_id})

    timestamp = product_data['timestamp']
    new_price = {
        'price': product_data['price']['decimal'],
        'timestamp': timestamp,
    }

    if doc is not None:

        last_price = doc['price_history'][-1]

        if new_price['price'].to_decimal() != last_price['price'].to_decimal():
            doc['price_history'].append(new_price)
            doc['current_price'] = product_data['price']['decimal']
            doc['last_price_change'] = timestamp

        lowest_price = doc['lowest_price']

        if new_price['price'].to_decimal() < lowest_price['price'].to_decimal():
            doc['lowest_price'] = new_price
            doc['is_lowest'] = True

        if new_price['price'].to_decimal() > lowest_price['price'].to_decimal():
            doc['is_lowest'] = False

        doc['last_updated'] = timestamp

        update = col.update_one({'data_id': data_id}, {"$set": doc})
        return update

    else:

        doc = {
            'name': product_data['name'],
            'data_id': product_data['data_id'],
            'current_price': product_data['price']['decimal'],
            'lowest_price': new_price,
            'price_history': [new_price],
            'is_lowest': True,
            'first_seen': timestamp,
            'last_price_change': timestamp,
            'last_updated': timestamp,
        }

        insert = col.insert_one(doc)
        return insert


