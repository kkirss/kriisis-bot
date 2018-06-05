from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1"]
SITE_URL = "127.0.0.1:8000"

# INSTALLED_APPS += ['django_extensions']

SECRET_KEY = 'z^rzbglpq)iul5ec7rjj0kw2ak$2gdr$3gghz2ajhkzc!qcvib'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('DB_NAME'),
        'USER': env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# DJOSER['SEND_ACTIVATION_EMAIL'] = True
# DJOSER['SEND_CONFIRMATION_EMAIL'] = True

if DJOSER['SEND_ACTIVATION_EMAIL'] or DJOSER['SEND_CONFIRMATION_EMAIL']:
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = env('EMAIL_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = ''
