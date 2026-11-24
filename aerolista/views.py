# ==============================================================
# views.py · Las vistas de Django
# --------------------------------------------------------------
# El navegador (JavaScript) pide datos con fetch() a estas direcciones;
# cada vista usa la LISTA ENLAZADA del vuelo, guarda el JSON y responde en JSON.
#
#   Navegador (fetch) → views.py → ListaPasajeros → persistencia.py → .json
# ==============================================================
import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from . import persistencia
from .estructuras.pasajero import Pasajero
from .vuelo import asiento_existe, total_asientos


# ---------------- Funciones de ayuda ----------------

def respuesta_ok(datos=None, mensaje="", codigo=200):
    """Respuesta correcta en JSON."""
    return JsonResponse({"ok": True, "datos": datos, "mensaje": mensaje}, status=codigo)


def respuesta_error(mensaje, codigo=400):
    """Respuesta de error en JSON (400 = datos incorrectos, 404 = no existe)."""
    return JsonResponse({"ok": False, "mensaje": mensaje}, status=codigo)


def leer_json(request):
    """Convierte el cuerpo del pedido (texto JSON) en un diccionario."""
    try:
        return json.loads(request.body)
    except ValueError:
        return {}


def a_diccionarios(pasajeros):
    """[Pasajero, ...] → [dict, ...] para poder enviarlos como JSON."""
    resultado = []
    for pasajero in pasajeros:
        resultado.append(pasajero.a_diccionario())
    return resultado


def validar_pasajero(nombre, cedula, edad, asiento):
    """Retorna el problema (texto) o "" si los datos están bien."""
    if len(nombre) < 2:
        return "Escribe el nombre del pasajero"
    if not (cedula.isdigit() and len(cedula) == 10):
        return "La cédula debe tener 10 dígitos"
    if not edad.isdigit() or int(edad) > 120:
        return "La edad debe ser un número entre 0 y 120"
    if not asiento_existe(asiento):
        return f"El asiento '{asiento}' no existe en este avión"
    return ""


def validar_vuelo(codigo, origen, destino, fecha, hora):
    """Retorna el problema (texto) o "" si los datos del vuelo están bien."""
    if len(codigo) < 3 or not codigo.replace("-", "").isalnum():
        return "El código debe tener letras, números o guion (ej: AL-450)"
    if len(origen) < 2 or len(destino) < 2:
        return "Escribe el origen y el destino"
    if origen.lower() == destino.lower():
        return "El origen y el destino deben ser distintos"
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        datetime.strptime(hora, "%H:%M")
    except ValueError:
        return "La fecha debe ser AAAA-MM-DD y la hora HH:MM"
    return ""


# ---------------- Página principal ----------------

def inicio(request):
    persistencia.asegurar_cargado()
    return render(request, "aerolista/index.html", {"vuelos": persistencia.vuelos})


# ---------------- Vuelos: registro y consulta ----------------

@require_http_methods(["GET", "POST"])
def vuelos(request):
    persistencia.asegurar_cargado()

    if request.method == "GET":                          # CONSULTAR todos los vuelos
        return respuesta_ok(persistencia.vuelos)

    datos = leer_json(request)                           # POST: REGISTRAR un vuelo nuevo
    codigo = str(datos.get("codigo", "")).strip().upper()
    origen = str(datos.get("origen", "")).strip()
    destino = str(datos.get("destino", "")).strip()
    fecha = str(datos.get("fecha", "")).strip()
    hora = str(datos.get("hora", "")).strip()

    problema = validar_vuelo(codigo, origen, destino, fecha, hora)
    if problema != "":
        return respuesta_error(problema)
    if persistencia.buscar_vuelo(codigo) is not None:
        return respuesta_error(f"Ya existe el vuelo {codigo}")

    vuelo = {"codigo": codigo, "origen": origen, "destino": destino, "fecha": fecha, "hora": hora}
    persistencia.registrar_vuelo(vuelo)                  # guarda en vuelos.json
    return respuesta_ok(vuelo, f"Vuelo {codigo} registrado", 201)


def ver_vuelo(request, codigo):
    """CONSULTAR un vuelo por su código."""
    vuelo = persistencia.buscar_vuelo(codigo.upper())
    if vuelo is None:
        return respuesta_error(f"No existe el vuelo {codigo}", 404)
    return respuesta_ok(vuelo)


def resumen(request, codigo):
    """Tablero: cuántas reservas hay y si la lista está vacía."""
    codigo = codigo.upper()
    if persistencia.buscar_vuelo(codigo) is None:
        return respuesta_error(f"No existe el vuelo {codigo}", 404)
    lista = persistencia.lista_de(codigo)
    return respuesta_ok({"cantidad": lista.longitud(),          # método 2
                         "vacia": lista.esta_vacia(),           # método 1
                         "total_asientos": total_asientos()})


# ---------------- Reservaciones ----------------

@require_http_methods(["GET", "POST"])
def reservas(request, codigo):
    codigo = codigo.upper()
    if persistencia.buscar_vuelo(codigo) is None:
        return respuesta_error(f"No existe el vuelo {codigo}", 404)
    lista = persistencia.lista_de(codigo)

    if request.method == "GET":                          # LISTAR (o filtrar por clase)
        clase = request.GET.get("clase", "")
        if clase == "":
            pasajeros = lista.listar()                   # método 3
        else:
            pasajeros = lista.filtrar_por_clase(clase)   # método 9
        return respuesta_ok(a_diccionarios(pasajeros))

    # POST: CREAR una reservación (validar → crear Pasajero → ingresar → guardar JSON)
    datos = leer_json(request)
    nombre = str(datos.get("nombre", "")).strip()
    cedula = str(datos.get("cedula", "")).strip()
    edad = str(datos.get("edad", "")).strip()
    asiento = str(datos.get("asiento", "")).strip().upper()

    problema = validar_pasajero(nombre, cedula, edad, asiento)
    if problema != "":
        return respuesta_error(problema)
    if lista.buscar_por_asiento(asiento) is not None:    # método 5: asiento ocupado
        return respuesta_error(f"El asiento {asiento} ya está reservado")
    if lista.buscar_por_cedula(cedula) is not None:      # método 6: cédula repetida
        return respuesta_error(f"La cédula {cedula} ya tiene una reserva en este vuelo")

    pasajero = Pasajero(persistencia.nuevo_numero(), nombre, cedula, int(edad), asiento)
    lista.ingresar(pasajero)                             # engancha al final de la lista
    persistencia.guardar_reservas()                      # escribe reservas.json
    return respuesta_ok(pasajero.a_diccionario(),
                        f"Reserva #{pasajero.numero} creada: {nombre} en el asiento {asiento}", 201)


@require_http_methods(["GET", "PUT", "DELETE"])
def reserva(request, codigo, numero):
    codigo = codigo.upper()
    if persistencia.buscar_vuelo(codigo) is None:
        return respuesta_error(f"No existe el vuelo {codigo}", 404)
    lista = persistencia.lista_de(codigo)

    if request.method == "GET":                          # CONSULTAR por número de reserva
        pasajero = lista.buscar(numero)                  # método 4
        if pasajero is None:
            return respuesta_error(f"No existe la reserva #{numero}", 404)
        return respuesta_ok(pasajero.a_diccionario(), f"Reserva #{numero} encontrada")

    if request.method == "PUT":                          # MODIFICAR nombre, edad y/o asiento
        datos = leer_json(request)
        nombre = str(datos.get("nombre", "")).strip()
        edad = str(datos.get("edad", "")).strip()
        asiento = str(datos.get("asiento", "")).strip().upper()

        pasajero = lista.buscar(numero)
        if pasajero is None:
            return respuesta_error(f"No existe la reserva #{numero}", 404)
        problema = validar_pasajero(nombre, pasajero.cedula, edad, asiento)   # la cédula no cambia
        if problema != "":
            return respuesta_error(problema)

        ocupante = lista.buscar_por_asiento(asiento)
        if ocupante is not None and ocupante.numero != numero:   # libre... o ya es suyo
            return respuesta_error(f"El asiento {asiento} ya es de {ocupante.nombre}")

        lista.modificar(numero, nombre, int(edad), asiento)      # método 7
        persistencia.guardar_reservas()
        return respuesta_ok(lista.buscar(numero).a_diccionario(), f"Reserva #{numero} actualizada")

    # DELETE: ELIMINAR (cancelar) la reserva
    eliminado = lista.eliminar(numero)                   # método 8
    if eliminado is None:
        return respuesta_error(f"No existe la reserva #{numero}", 404)
    persistencia.guardar_reservas()
    return respuesta_ok(eliminado.a_diccionario(),
                        f"Reserva #{numero} cancelada: el asiento {eliminado.asiento} quedó libre")


def por_asiento(request, codigo, asiento):
    """¿Quién está sentado en este asiento? Libre no es un error."""
    codigo = codigo.upper()
    asiento = asiento.upper()
    if persistencia.buscar_vuelo(codigo) is None:
        return respuesta_error(f"No existe el vuelo {codigo}", 404)
    pasajero = persistencia.lista_de(codigo).buscar_por_asiento(asiento)   # método 5
    if pasajero is None:
        return respuesta_ok(None, f"El asiento {asiento} está libre")
    return respuesta_ok(pasajero.a_diccionario(), f"En el {asiento} viaja {pasajero.nombre}")


def por_cedula(request, codigo, cedula):
    """Busca un pasajero por cédula."""
    codigo = codigo.upper()
    if persistencia.buscar_vuelo(codigo) is None:
        return respuesta_error(f"No existe el vuelo {codigo}", 404)
    pasajero = persistencia.lista_de(codigo).buscar_por_cedula(cedula)     # método 6
    if pasajero is None:
        return respuesta_error(f"Ningún pasajero tiene la cédula {cedula}", 404)
    return respuesta_ok(pasajero.a_diccionario(), "Pasajero encontrado")
