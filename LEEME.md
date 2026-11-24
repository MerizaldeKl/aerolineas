# AeroLista · Sistema de reservación de vuelos (Práctica G004)

Proyecto Django con lista enlazada propia (`ListaPasajeros`) y almacenamiento en archivos JSON.

## Estructura
```
aerolista_django/
├── manage.py                      comandos de Django
├── requirements.txt               librerías (solo Django)
├── config/                        configuración del proyecto Django
│   ├── settings.py · urls.py · wsgi.py
└── aerolista/                     aplicación principal
    ├── estructuras/
    │   ├── pasajero.py            clase Pasajero
    │   └── lista_pasajeros.py     Nodo y ListaPasajeros (9 métodos + ingresar)
    ├── vuelo.py                   forma del avión (68 asientos) y clases
    ├── persistencia.py            leer y guardar los JSON
    ├── views.py · urls.py         vistas y direcciones (reemplazan app.py de Flask)
    ├── datos/vuelos.json          vuelos registrados
    ├── datos/reservas.json        reservaciones (por vuelo)
    ├── templates/aerolista/index.html
    ├── static/aerolista/css/estilos.css
    ├── static/aerolista/js/app.js
    └── tests.py                   pruebas automáticas
```

## Instalar y ejecutar
```
python -m venv venv
venv\Scripts\activate          (en Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py runserver
```
Abrir http://127.0.0.1:8000 (necesita internet para cargar Bootstrap).

## Pruebas automáticas
```
python manage.py test aerolista
```

## Cómo se conectan las piezas
Navegador (app.js, fetch) → views.py → ListaPasajeros del vuelo → persistencia.py → reservas.json.
Al encender el servidor, `persistencia.cargar()` lee los JSON y arma una lista enlazada por vuelo con `ingresar()`.
Después de crear, modificar o eliminar, `persistencia.guardar_reservas()` recorre la lista y escribe el JSON.
