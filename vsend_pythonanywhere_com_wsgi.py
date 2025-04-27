import os
import sys

# Add your project directory to the Python path
path = '/home/vsend/PokeTrade'
if path not in sys.path:
    sys.path.append(path)

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'poketrade.settings'

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 