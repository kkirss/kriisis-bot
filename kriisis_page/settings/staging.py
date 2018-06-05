from .base import *

DEBUG = True

ALLOWED_HOSTS = ['']
SITE_URL = ''

SECRET_KEY = 'z^rzbglpq)iul5ec7rjj0kw2ak$2gdr$3gghz2ajhkzc!qcvib'

DATABASES['default'] = env.db()

# DJOSER['SEND_ACTIVATION_EMAIL'] = True
# DJOSER['SEND_CONFIRMATION_EMAIL'] = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = env('EMAIL_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ''
