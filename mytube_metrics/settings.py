"""
Django settings for mytube_metrics project.

Generated by 'django-admin startproject' using Django 5.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# --- Environment Variables ---
# Load environment variables from .env file at the very beginning.
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


# --- General Settings ---

# A secret key for a particular Django installation. This is used to provide cryptographic signing.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Defines the list of hosts/domains that this Django site can serve.
if os.environ.get('MODE') == 'production':
    ALLOWED_HOSTS = os.environ.get('PROD_ALLOWED_HOSTS', 'mytube-metrics,www.mytube-metrics,18.191.182.193').split(',')
    DEBUG = False

    # HTTPS Security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    ALLOWED_HOSTS = os.environ.get('DEV_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    DEBUG = True

# The Python path to the root URLconf.
ROOT_URLCONF = 'mytube_metrics.urls'

# The URL to redirect to for login if a user is not authenticated.
LOGIN_URL = '/'

if os.environ.get('MODE') == 'production':
    REDIRECT_URI = os.environ.get('PROD_REDIRECT_URI')
else:
    REDIRECT_URI = os.environ.get('DEV_REDIRECT_URI')

# WSGI application entry point.
WSGI_APPLICATION = 'mytube_metrics.wsgi.application'

# Default auto field for models.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField" # autoincrementing id PK


# --- Application Definition ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'metrics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# --- Database Configuration ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

if os.environ.get('MODE') == 'production':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get("PROD_DB_NAME"),
            'USER': os.environ.get("PROD_DB_USER"),
            'PASSWORD': os.environ.get("PROD_DB_PASSWORD"),
            'HOST': os.environ.get("PROD_DB_HOST"),
            'PORT': os.environ.get("PROD_DB_PORT"),
            'OPTIONS': {
                'ssl': {
                    'ca': os.environ.get('PROD_DB_SSL_CA'),
                }
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get("DEV_DB_NAME"),
            'USER': os.environ.get("DEV_DB_USER"),
            'PASSWORD': os.environ.get("DEV_DB_PASSWORD"),
            'HOST': os.environ.get("DEV_DB_HOST"),
            'PORT': os.environ.get("DEV_DB_PORT"),
        }
    }


# --- Password Validation ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- Internationalization ---
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Static Files Configuration ---
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]