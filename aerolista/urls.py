# aerolista/urls.py · Direcciones de la aplicación (en Flask eran los @app.route)
from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),                                              # la página
    path("api/vuelos", views.vuelos, name="vuelos"),                                    # GET lista · POST registrar
    path("api/vuelos/<str:codigo>", views.ver_vuelo, name="ver_vuelo"),                 # GET un vuelo
    path("api/vuelos/<str:codigo>/resumen", views.resumen, name="resumen"),             # GET longitud / esta_vacia
    path("api/vuelos/<str:codigo>/reservas", views.reservas, name="reservas"),          # GET listar · POST reservar
    path("api/vuelos/<str:codigo>/reservas/<int:numero>", views.reserva, name="reserva"),  # GET · PUT · DELETE
    path("api/vuelos/<str:codigo>/asientos/<str:asiento>", views.por_asiento, name="por_asiento"),
    path("api/vuelos/<str:codigo>/cedulas/<str:cedula>", views.por_cedula, name="por_cedula"),
]
