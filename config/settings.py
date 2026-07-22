import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: Use environment variable in production, fallback for dev only
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-)#5)s)msn(zd2gs-5y!$d_cs+6p5rjvj269^amccvnu$c7ot8%')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'core',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'core' / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Tesseract OCR - Windows path (auto-detects if not found)
import shutil
import os

_TESSERACT_PATH = shutil.which('tesseract') or r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TESSERACT_CMD = _TESSERACT_PATH

# Poppler - Windows path (auto-detects if not found)
# Check common Poppler install locations on Windows
_POPPLER_SEARCH = [
    r'C:\poppler\Library\bin',
    r'C:\poppler\poppler-26.02.0\Library\bin',
    r'C:\Program Files\poppler\Library\bin',
    r'C:\Program Files (x86)\poppler\Library\bin',
    r'C:\tools\poppler\Library\bin',
    os.path.expandvars(r'%LOCALAPPDATA%\poppler\Library\bin'),
    # Search for any poppler-xx.x.x version folder
    r'C:\poppler',
]
POPPLER_PATH = ''
for _pp in _POPPLER_SEARCH:
    if os.path.isdir(_pp):
        # If it's the base poppler folder, search for Library\bin inside
        if _pp == r'C:\poppler' and not os.path.isfile(os.path.join(_pp, 'Library', 'bin', 'pdftoppm.exe')):
            for entry in os.listdir(_pp):
                candidate = os.path.join(_pp, entry, 'Library', 'bin')
                if os.path.isdir(candidate):
                    POPPLER_PATH = candidate
                    break
        else:
            POPPLER_PATH = _pp
        if POPPLER_PATH:
            break
if not POPPLER_PATH:
    _poppler_bin = shutil.which('pdftoppm')
    if _poppler_bin:
        POPPLER_PATH = os.path.dirname(_poppler_bin)

# BERT Model
BERT_MODEL_NAME = 'HooshvareLab/bert-fa-base-uncased-sentiment-snappfood'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}