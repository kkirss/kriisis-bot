import datetime
import os

import environ
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = environ.Env(DEBUG=(bool, False), )

DEBUG = env.bool('DEBUG')

SECRET_KEY = 'z^rzbglpq)iul5ec7rjj0kw2ak$2gdr$3gghz2ajhkzc!qcvib'

TELEGRAM_AUTH_TOKEN = env.str('TELEGRAM_AUTH_TOKEN')

HASHID_FIELD_SALT = 'I8cOQl8/7PPWG+fAz;|zOaAZWmF8w]"0:@"GG-sg+0@H03eIZc'

ALLOWED_HOSTS = []

# ADMINS = [('Kristofer Kirss', 'kristofer.kirss@gmail.com')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'knox',

    'kriisis_page',
    'accounts',
    'scraper',
    'telegram_bot',
    'frontend',

    'rest_framework',
    'djoser',
    'django_filters',
    # 'corsheaders',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 'knox.auth.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'kriisis_page.pagination.StandardResultsSetPagination',
}

JWT_AUTH = {
    'JWT_PAYLOAD_HANDLER': 'accounts.utils.hashid_jwt_payload_handler',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1)
}

# REST_KNOX = {
#     'TOKEN_TTL': datetime.timedelta(weeks=1),  # Amount of time until a login token expires
#     'USER_SERIALIZER': 'accounts.serializers.UserSerializer'
# }

DJOSER = {
    'SITE_NAME': 'Kriisis Page',
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'SERIALIZERS': {
        'user_create': 'accounts.serializers.UserCreateSerializer',
    }
}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Enable per-user language selection (order is important)
    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kriisis_page.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(BASE_DIR, 'frontend/build')
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kriisis_page.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kriisis_page',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.User'

# USER_SERIALIZER = 'accounts.serializers.UserSerializer'

LANGUAGE_CODE = 'en'  # Default language
LANGUAGES = [
    ('et', _('Estonian')),
    ('en', _('English')),
]

CORS_ORIGIN_ALLOW_ALL = True

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Tallinn'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend/build/static'),
)
