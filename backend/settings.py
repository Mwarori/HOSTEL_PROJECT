from pathlib import Path
import sys
import os
from decouple import config
from datetime import timedelta
import mongoengine

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'api',
]

# Note: We use MongoDB for the api app, so no custom AUTH_USER_MODEL needed

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'backend.urls'

# MongoDB Connection Configuration
MONGODB_HOST = config('MONGODB_HOST', default='mongodb://localhost:27017')
MONGODB_DB = config('MONGODB_DB', default='hostel_db')
MONGODB_USERNAME = config('MONGODB_USERNAME', default='')
MONGODB_PASSWORD = config('MONGODB_PASSWORD', default='')

# Build MongoDB URI with credentials if provided
if MONGODB_USERNAME and MONGODB_PASSWORD:
    # URI format: mongodb://username:password@host:port/database
    # Extract host from MONGODB_HOST if it already includes protocol
    if MONGODB_HOST.startswith('mongodb://'):
        mongodb_uri = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST[10:]}"
    else:
        mongodb_uri = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}"
else:
    mongodb_uri = MONGODB_HOST

# Connect to MongoDB using mongoengine
mongoengine.connect(
    db=MONGODB_DB,
    host=mongodb_uri,
    connect=False,
    retryWrites=True,
    connectTimeoutMS=5000
)

# Disable Django's default database - we use MongoDB via mongoengine
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Disable database migrations warnings for MongoDB
DATABASE_ROUTERS = ['api.router.MongoDBRouter']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:5500',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
]

CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins including file:// for local testing
CORS_ALLOW_CREDENTIALS = True

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.auth_backend.MongoDBJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}
