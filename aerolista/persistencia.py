# ==============================================================
# persistencia.py · Guardar y leer los datos en archivos JSON
# --------------------------------------------------------------
#   RAM (se borra)                              DISCO (permanece)
#   lista enlazada de cada vuelo --guardar--> datos/reservas.json
#   lista de vuelos              --guardar--> datos/vuelos.json
#                                <--cargar---
# Cada vuelo tiene SU propia ListaPasajeros (se guardan en el diccionario "listas").
# ==============================================================
import json
import os

from aerolista.estructuras.lista_pasajeros import ListaPasajeros
from aerolista.estructuras.pasajero import Pasajero

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
RUTA_VUELOS = os.path.join(CARPETA, "vuelos.json")
RUTA_RESERVAS = os.path.join(CARPETA, "reservas.json")

vuelos = []                 # lista de diccionarios con los datos de cada vuelo
listas = {}                 # {"AL-204": ListaPasajeros, ...}
siguiente_numero = 1001     # próximo número de reserva que se entregará
cargado = False             # para leer los archivos solo una vez


def cargar():
    """Lee los dos archivos JSON y arma las listas enlazadas con ingresar()."""
    global vuelos, listas, siguiente_numero, cargado
    vuelos = []
    listas = {}

    if os.path.exists(RUTA_VUELOS):
        with open(RUTA_VUELOS, "r", encoding="utf-8") as archivo:
            vuelos = json.load(archivo)["vuelos"]

    for vuelo in vuelos:                          # cada vuelo empieza con su lista vacía
        listas[vuelo["codigo"]] = ListaPasajeros()

    if os.path.exists(RUTA_RESERVAS):
        with open(RUTA_RESERVAS, "r", encoding="utf-8") as archivo:
            contenido = json.load(archivo)
        for codigo in contenido["reservas"]:
            if codigo not in listas:
                listas[codigo] = ListaPasajeros()
            for d in contenido["reservas"][codigo]:
                pasajero = Pasajero(d["numero"], d["nombre"], d["cedula"], d["edad"], d["asiento"])
                listas[codigo].ingresar(pasajero)  # ✅ el ingresar de la lista enlazada
        siguiente_numero = contenido["siguiente_numero"]

    cargado = True


def asegurar_cargado():
    """Carga los archivos la primera vez que se necesitan."""
    if not cargado:
        cargar()


def guardar_vuelos():
    """Escribe la lista de vuelos en datos/vuelos.json."""
    os.makedirs(CARPETA, exist_ok=True)
    with open(RUTA_VUELOS, "w", encoding="utf-8") as archivo:
        json.dump({"vuelos": vuelos}, archivo, ensure_ascii=False, indent=2)


def guardar_reservas():
    """Pasa cada lista enlazada a diccionarios y los escribe en datos/reservas.json."""
    reservas = {}
    for codigo in listas:
        reservas[codigo] = []
        for pasajero in listas[codigo].listar():      # recorre la lista enlazada
            d = pasajero.a_diccionario()
            d.pop("clase")                            # la clase se calcula, no se guarda
            reservas[codigo].append(d)
    os.makedirs(CARPETA, exist_ok=True)
    with open(RUTA_RESERVAS, "w", encoding="utf-8") as archivo:
        json.dump({"siguiente_numero": siguiente_numero, "reservas": reservas},
                  archivo, ensure_ascii=False, indent=2)


def buscar_vuelo(codigo):
    """Retorna el diccionario del vuelo con ese código, o None."""
    asegurar_cargado()
    for vuelo in vuelos:
        if vuelo["codigo"] == codigo:
            return vuelo
    return None


def registrar_vuelo(vuelo):
    """Agrega un vuelo nuevo (con su lista enlazada vacía) y guarda el JSON."""
    asegurar_cargado()
    vuelos.append(vuelo)
    listas[vuelo["codigo"]] = ListaPasajeros()
    guardar_vuelos()
    guardar_reservas()


def lista_de(codigo):
    """Retorna la ListaPasajeros del vuelo."""
    asegurar_cargado()
    return listas[codigo]


def nuevo_numero():
    """Entrega un número de reserva que nunca se ha usado."""
    global siguiente_numero
    numero = siguiente_numero
    siguiente_numero = siguiente_numero + 1
    return numero
