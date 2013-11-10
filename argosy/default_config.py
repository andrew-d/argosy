import os

DEBUG = True
SECRET_KEY = os.urandom(20)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

IMAGE_STORE_DIR = os.path.join(DATA_DIR, 'images')
THUMB_STORE_DIR = os.path.join(DATA_DIR, 'thumbs')

DATABASE = {
    'name': os.path.join(DATA_DIR, 'local.db'),
    'engine': 'peewee.SqliteDatabase',
    'threadlocals': True
}

ITEMS_PER_PAGE = 20
