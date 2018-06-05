from .base import *

DEBUG = False

ALLOWED_HOSTS = ['']
SITE_URL = ''

SECRET_KEY = env('SECRET_KEY')

HASHID_FIELD_SALT = env('HASHID_FIELD_SALT')

DATABASES['default'] = env.db()

DJOSER['SEND_ACTIVATION_EMAIL'] = True
DJOSER['SEND_CONFIRMATION_EMAIL'] = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = env('EMAIL_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ''
