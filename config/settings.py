# config/settings.py · Configuración del proyecto Django
# Este proyecto NO usa base de datos: todo se guarda en archivos JSON.
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "clave-de-practica-g004-no-usar-en-produccion"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",   # para entregar CSS y JavaScript
    "aerolista",                    # nuestra aplicación
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",   # protege los POST/PUT/DELETE
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,           # busca las plantillas en aerolista/templates/
        "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {}                      # sin base de datos (la guía pide archivos JSON)

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Guayaquil"
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
