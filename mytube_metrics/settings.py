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

# Set to True to enable Django's debug mode.
# IMPORTANT: Should be False in production for security.
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'

# Defines the list of hosts/domains that this Django site can serve.
# Replace with actual domain and EC2 public IP during production.
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# The Python path to the root URLconf.
ROOT_URLCONF = 'mytube_metrics.urls'

# The URL to redirect to for login if a user is not authenticated.
LOGIN_URL = '/'

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
    'storages',  # For handling S3 storage
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("DB_NAME"),
        'USER': os.environ.get("DB_USER"),
        'PASSWORD': os.environ.get("DB_PASSWORD"),
        'HOST': os.environ.get("DB_HOST"),
        'PORT': os.environ.get("DB_PORT"),
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

# A switch to determine whether to use S3 for static files.
USE_S3 = os.environ.get('USE_S3') == 'True'

if USE_S3:
    # --- S3 Static Storage Settings (Production) ---
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    # The URL that static files will be served from.
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    # The storage backend to use for collectstatic.
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

else:
    # --- Local Static Storage Settings (Development) ---
    # The URL to serve static files from.
    STATIC_URL = 'static/'
    # The absolute path to the directory where collectstatic will gather static files.
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    # Directories where Django will look for static files.
    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]
