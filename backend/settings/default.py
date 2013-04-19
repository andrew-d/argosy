"""Default settings for Argosy."""
import os

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/argosy'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Note: this MUST BE overridden in production.
SECRET_KEY = '1$\xbc\x11d\xcf\xff?^\xe0\x905\xd4>s(\x02\x9b\xe0\xca\x91F\x99\x9c'

# Argosy-specific settings.
ARGOSY_DATA_STORE    = 'memory'
#ARGOSY_DATA_LOCATION = '/tmp'
