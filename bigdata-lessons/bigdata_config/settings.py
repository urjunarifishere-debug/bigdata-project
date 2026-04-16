"""
Django настройки для Big Data веб-сервис жобасы.
Курс: Big Data / Деректерді өңдеу
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-bigdata-rpo1-24k-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# -----------------------------------------------------------------------
# Қосымшалар
# -----------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Біздің қосымша
    'dataprocessor',
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

ROOT_URLCONF = 'bigdata_config.urls'

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

WSGI_APPLICATION = 'bigdata_config.wsgi.application'

# -----------------------------------------------------------------------
# Дерекқор — SQLite (Django әдепкі)
# -----------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -----------------------------------------------------------------------
# Статикалық файлдар
# -----------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# -----------------------------------------------------------------------
# Медиа файлдар (жүктелген файлдар)
# -----------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------------------------------------------------------
# Файл жүктеу шектеулері (ТЗ бойынша: 100 МБ)
# -----------------------------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = 104_857_600   # 100 МБ байтпен
FILE_UPLOAD_MAX_MEMORY_SIZE = 104_857_600   # 100 МБ байтпен

# Рұқсат берілген файл кеңейтімдері
ALLOWED_UPLOAD_EXTENSIONS = ['.csv', '.json', '.txt', '.xlsx']

# -----------------------------------------------------------------------
# Локализация
# -----------------------------------------------------------------------
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
