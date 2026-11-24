# config/urls.py · Direcciones principales: todo lo maneja la app aerolista
from django.urls import include, path

urlpatterns = [
    path("", include("aerolista.urls")),
]
