from pathlib import Path
from decouple import config

import dj_database_url

import cloudinary
import cloudinary.uploader
import cloudinary.api

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG')

ALLOWED_HOSTS = ['taskforge-8i3n.onrender.com','127.0.0.1']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'service',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',
    'service.middleware.TimerMiddleware'
]

ROOT_URLCONF = 'main_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'main_service.wsgi.application'




# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}


# Django caching with Redis.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('EXTERNAL_REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 10 ** 5




# Password validation
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


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

CSRF_TRUSTED_ORIGINS = [
    "https://taskforge-8i3n.onrender.com",
]

# Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET')
}
cloudinary.config(
    cloud_name = config('CLOUDINARY_CLOUD_NAME'),
    api_key = config('CLOUDINARY_API_KEY'),
    api_secret = config('CLOUDINARY_API_SECRET')
)

# DEFAULT FILE STORAGE
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'service': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}




# Endpoints:

# auth:
# AUTH_SERVICE_URL = 'https://taskforge-1.onrender.com'
AUTH_SERVICE_URL = ' http://127.0.0.1:4000'

GET_TOKENS = f'{AUTH_SERVICE_URL}/api/token/'
REGISTER_API = f'{AUTH_SERVICE_URL}/api/register/'
GET_DATA_BY_ID = f'{AUTH_SERVICE_URL}/api/databyid/'
CANGE_PHOTO_API = f'{AUTH_SERVICE_URL}/api/change/photo/'
INFO_BY_ID_LIST = f'{AUTH_SERVICE_URL}/api/infoidlist/'


# group:
# GROUP_SERVICE_URL = 'https://taskforge-1.onrender.com'
GROUP_SERVICE_URL = 'http://127.0.0.1:7000'

MY_GROUPS_API = f'{GROUP_SERVICE_URL}/api/mygroups/'
GET_GROUP_INFO = f'{GROUP_SERVICE_URL}/api/info/group/'
CREATE_GROUP_API = f'{GROUP_SERVICE_URL}/api/create/group/'
DELETE_GROUP_API = f'{GROUP_SERVICE_URL}/api/delete/group/'
GROUP_USER_LIST = f'{GROUP_SERVICE_URL}/api/group/userlist/'
ADD_USER_TO_GROUP = f'{GROUP_SERVICE_URL}/api/adduser/group/'
DELETE_USER_FROM_GROUP = f'{GROUP_SERVICE_URL}/api/deleteuser/group/'


# task:
# TASK_SERVICE_URL = ''
TASK_SERVICE_URL = 'http://127.0.0.1:9000'

CREATE_TASK_API = f'{TASK_SERVICE_URL}/api/create/task/'
GROUP_TASK_LIST = f'{TASK_SERVICE_URL}/api/group/tasks/'
INFO_TASK_API = f'{TASK_SERVICE_URL}/api/task/info/'
TAKE_TASK_API = f'{TASK_SERVICE_URL}/api/task/take/'
FINISH_TASK_API = f'{TASK_SERVICE_URL}/api/task/finish/'
DELETE_TASK_API = f'{TASK_SERVICE_URL}/api/task/delete/'