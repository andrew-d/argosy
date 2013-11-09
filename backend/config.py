import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

IMAGE_STORE_DIR = os.path.join(ROOT_DIR, 'data')
THUMB_STORE_DIR = os.path.join(ROOT_DIR, 'thumbs')

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production').lower()
DEBUG = ENVIRONMENT == 'debug'
TESTING = ENVIRONMENT == 'testing'
PRODUCTION = ENVIRONMENT == 'production'


def get_db():
    import peewee

    if DEBUG:
        db = peewee.SqliteDatabase(os.path.join(ROOT_DIR, 'local.db'))
    elif TESTING:
        db = peewee.SqliteDatabase(':memory:')
    elif PRODUCTION:
        db = peewee.PostgresqlDatabase('prod_db_goes_here')
    else:
        raise Exception("Invalid environment, cannot create database!")

    return db
