# This file contains default settings for argosy.
# --------------------------------------------------
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/argosy'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Note: this is overridden in production.
SECRET_KEY = '1$\xbc\x11d\xcf\xff?^\xe0\x905\xd4>s(\x02\x9b\xe0\xca\x91F\x99\x9c'