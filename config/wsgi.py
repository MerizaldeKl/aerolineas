# config/wsgi.py · Punto de entrada del servidor (lo crea Django por defecto)
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
