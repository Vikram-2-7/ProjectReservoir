"""
Django settings for weather_project project.
Generated and optimized for BrookStream.Ai dashboard (Weather + Dam Control + ML).
"""

import os
from pathlib import Path

# Import our configuration
from config import config

# ------------------------------------------------
# BASE DIRECTORY
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------
# SECURITY
# ------------------------------------------------
SECRET_KEY = config.SECRET_KEY
DEBUG = config.DEBUG
ALLOWED_HOSTS = config.ALLOWED_HOSTS


# ------------------------------------------------
# APPLICATION DEFINITION
# ------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',   # ✅ Required for request.session
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'weather',
    'dam',
    'hydroalert',
                                          # ✅ Your weather app
]
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # ✅ Session middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'weather_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # optional: global template folder
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

WSGI_APPLICATION = 'weather_project.wsgi.application'


# ------------------------------------------------
# DATABASE
# ------------------------------------------------
if config.DATABASE_URL:
    # Use PostgreSQL or other database if configured
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(config.DATABASE_URL)
    }
else:
    # Default to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------
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


# ------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# ------------------------------------------------
# STATIC & MEDIA FILES
# ------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # ✅ if you keep static files locally
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ------------------------------------------------
# SESSION CONFIGURATION
# ------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # ✅ store in DB
SESSION_COOKIE_AGE = 3600           # 1 hour session lifetime
SESSION_SAVE_EVERY_REQUEST = True   # refresh on each request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# ------------------------------------------------
# DEFAULT AUTO FIELD
# ------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ------------------------------------------------
# EMAIL CONFIGURATION
# ------------------------------------------------
if config.EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config.EMAIL_HOST
    EMAIL_PORT = config.EMAIL_PORT
    EMAIL_HOST_USER = config.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    DEFAULT_FROM_EMAIL = config.EMAIL_HOST_USER or 'noreply@brookstream.ai'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ------------------------------------------------
# CACHING CONFIGURATION
# ------------------------------------------------
if config.REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config.REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }


# ------------------------------------------------
# LOGGING CONFIGURATION
# ------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': config.LOG_DIR / 'django.log',
            'formatter': 'detailed',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'brookstream': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# ------------------------------------------------
# SECURITY SETTINGS
# ------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'


# ------------------------------------------------
# FILE UPLOAD SETTINGS
# ------------------------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = config.MAX_UPLOAD_SIZE
DATA_UPLOAD_MAX_MEMORY_SIZE = config.MAX_UPLOAD_SIZE
UPLOAD_FILE_MAX_SIZE = config.MAX_UPLOAD_SIZE


# ------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# ------------------------------------------------
# STATIC & MEDIA FILES
# ------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ------------------------------------------------
# SESSION CONFIGURATION
# ------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.cache' if config.REDIS_URL else 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# ------------------------------------------------
# MIDDLEWARE FOR SECURITY
# ------------------------------------------------
if not DEBUG:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
else:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
