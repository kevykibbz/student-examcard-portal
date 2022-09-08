from pathlib import Path
import environ
import os
env=environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
if DEBUG:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = ['192.168.43.106','student-examcard-portal.herokuapp.com','www.student-examcard-portal.herokuapp.com',]

SITE_ID=2
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]
# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'installation.apps.InstallationConfig',
    'django.contrib.humanize',
    'phonenumber_field',
    'errors.apps.ErrorsConfig',
    'manager.apps.ManagerConfig',
    'django.contrib.sites', #social app 
    'allauth', #social app
    'allauth.account', #social app
    'allauth.socialaccount', #social app
    'allauth.socialaccount.providers.google', #social app
    'allauth.socialaccount.providers.twitter', #social app
    'allauth.socialaccount.providers.github', #social app
    'django_cleanup.apps.CleanupConfig',
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

ROOT_URLCONF = 'examcard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'examcard.site_constants.export_vars',
            ],
        },
    },
]

WSGI_APPLICATION = 'examcard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS':
        {
            'min_length':6,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME':'manager.validators.NumberValidator',
        'OPTIONS':
        {
            'min_length':2,
        },
    },
    {
        'NAME':'manager.validators.UpperCaseValidator',
    },
    {
        'NAME':'manager.validators.LowerCaseValidator',
    },
]


#login
LOGIN_URL='/accounts/login'
LOGIN_REDIRECT_URL='/dashboard'
LOGOUT_REDIRECT_URL='/accounts/login'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL='/media/'

#STATICFILES_STORAGE='whitenoise.storage.CompressedManifestStaticFilesStorage'
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG:
    STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]
else:
    STATIC_ROOT=os.path.join(BASE_DIR,'static')


MEDIA_ROOT=os.path.join(BASE_DIR,'media')


BASE_URL=env('BASE_URL')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_HOST=env('EMAIL_HOST')
EMAIL_HOST_USER=env('EMAIL_USER')
EMAIL_HOST_PASSWORD=env('EMAIL_PASSWORD')
EMAIL_USE_TLS=True
EMAIL_PORT=587 
DEFAULT_FROM_EMAIL=EMAIL_HOST_USER


#cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
