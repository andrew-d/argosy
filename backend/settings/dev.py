"""Development settings for Argosy."""

from .default import *

# Set debug on.
DEBUG = True

# Hosts allowed to see debug toolbar.
# DEBUG_TB_HOSTS = ('127.0.0.1',)

# Use a local PostgreSQL database for development.
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/argosy'

# Argosy-specific settings.
ARGOSY_DATA_STORE    = 'dir'
ARGOSY_DATA_LOCATION = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
