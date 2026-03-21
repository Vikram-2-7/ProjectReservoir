"""
Django settings for weather_project project.
Generated and optimized for BrookStream.Ai dashboard (Weather + Dam Control + ML).
"""

import os
from pathlib import Path

# ------------------------------------------------
# BASE DIRECTORY
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------
# SECURITY
# ------------------------------------------------
SECRET_KEY = 'django-insecure-change-this-key-in-production'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


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
