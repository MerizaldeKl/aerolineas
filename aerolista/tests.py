# ==============================================================
# tests.py · Pruebas automáticas (python manage.py test)
# Usan COPIAS temporales de los JSON: los datos reales no se tocan.
# ==============================================================
import json
import os
import shutil
import tempfile

from django.test import SimpleTestCase

from . import persistencia
from .estructuras.lista_pasajeros import ListaPasajeros
from .estructuras.pasajero import Pasajero


def lista_de_prueba():
    """Lista con 4 pasajeros: Diana(1005) · Ana(1002) · Luis(1009) · Beto(1004)."""
    lista = ListaPasajeros()
    lista.ingresar(Pasajero(1005, "Diana", "0923456789", 22, "3C"))
    lista.ingresar(Pasajero(1002, "Ana", "0912345678", 28, "1A"))
    lista.ingresar(Pasajero(1009, "Luis", "0987654321", 35, "7D"))
    lista.ingresar(Pasajero(1004, "Beto", "0934567890", 16, "7E"))
    return lista


def numeros(pasajeros):
    resultado = []
    for p in pasajeros:
        resultado.append(p.numero)
    return resultado


class PruebasListaEnlazada(SimpleTestCase):
    """Los 9 métodos de ListaPasajeros."""

    def test_1_esta_vacia(self):
        self.assertTrue(ListaPasajeros().esta_vacia())
        self.assertFalse(lista_de_prueba().esta_vacia())

    def test_2_longitud(self):
        self.assertEqual(ListaPasajeros().longitud(), 0)
        self.assertEqual(lista_de_prueba().longitud(), 4)

    def test_3_listar_en_orden_de_llegada(self):
        self.assertEqual(ListaPasajeros().listar(), [])
        self.assertEqual(numeros(lista_de_prueba().listar()), [1005, 1002, 1009, 1004])

    def test_4_buscar(self):
        lista = lista_de_prueba()
        self.assertEqual(lista.buscar(1009).nombre, "Luis")
        self.assertIsNone(lista.buscar(9999))

    def test_5_buscar_por_asiento(self):
        lista = lista_de_prueba()
        self.assertEqual(lista.buscar_por_asiento("7E").nombre, "Beto")
        self.assertIsNone(lista.buscar_por_asiento("9C"))

    def test_6_buscar_por_cedula(self):
        lista = lista_de_prueba()
        self.assertEqual(lista.buscar_por_cedula("0912345678").nombre, "Ana")
        self.assertIsNone(lista.buscar_por_cedula("0000000000"))

    def test_7_modificar(self):
        lista = lista_de_prueba()
        self.assertTrue(lista.modificar(1009, "Luis A.", 36, "11A"))
        p = lista.buscar(1009)
        self.assertEqual((p.nombre, p.edad, p.asiento), ("Luis A.", 36, "11A"))
        self.assertEqual(numeros(lista.listar()), [1005, 1002, 1009, 1004])   # no cambia de lugar
        self.assertFalse(lista.modificar(9999, "X", 1, "1A"))

    def test_8_eliminar_los_4_casos(self):
        # A: lista vacía
        self.assertIsNone(ListaPasajeros().eliminar(1))
        # B: la cabeza
        lista = lista_de_prueba()
        self.assertEqual(lista.eliminar(1005).nombre, "Diana")
        self.assertEqual(numeros(lista.listar()), [1002, 1009, 1004])
        self.assertEqual(lista.longitud(), 3)
        # C: en medio y al final
        self.assertEqual(lista.eliminar(1009).nombre, "Luis")
        self.assertEqual(lista.eliminar(1004).nombre, "Beto")
        self.assertEqual(numeros(lista.listar()), [1002])
        self.assertEqual(lista.longitud(), 1)
        # D: no existe
        self.assertIsNone(lista.eliminar(9999))
        self.assertEqual(lista.longitud(), 1)
        # eliminar el único nodo deja la lista vacía
        lista.eliminar(1002)
        self.assertTrue(lista.esta_vacia())

    def test_9_filtrar_por_clase(self):
        lista = lista_de_prueba()
        self.assertEqual(numeros(lista.filtrar_por_clase("Ejecutiva")), [1002])
        self.assertEqual(numeros(lista.filtrar_por_clase("Económica")), [1005, 1009, 1004])
        self.assertEqual(ListaPasajeros().filtrar_por_clase("Ejecutiva"), [])


class PruebasAplicacion(SimpleTestCase):
    """Páginas, API y archivos JSON (con copias temporales)."""

    def setUp(self):
        self.carpeta = tempfile.mkdtemp()
        self.original = (persistencia.RUTA_VUELOS, persistencia.RUTA_RESERVAS)
        for nombre in ("vuelos.json", "reservas.json"):
            shutil.copy(os.path.join(persistencia.CARPETA, nombre), self.carpeta)
        persistencia.RUTA_VUELOS = os.path.join(self.carpeta, "vuelos.json")
        persistencia.RUTA_RESERVAS = os.path.join(self.carpeta, "reservas.json")
        persistencia.cargar()

    def tearDown(self):
        persistencia.RUTA_VUELOS, persistencia.RUTA_RESERVAS = self.original
        persistencia.cargado = False
        shutil.rmtree(self.carpeta)

    def enviar(self, metodo, url, datos=None):
        cuerpo = json.dumps(datos) if datos is not None else ""
        r = getattr(self.client, metodo)(url, data=cuerpo, content_type="application/json")
        return r.status_code, r.json()

    def nueva_reserva(self, asiento="9C", cedula="0912121212", nombre="Zoe", edad=20):
        return self.enviar("post", "/api/vuelos/AL-204/reservas",
                           {"nombre": nombre, "cedula": cedula, "edad": edad, "asiento": asiento})

    def test_pagina_principal_y_asientos(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "AL-204")
        self.assertContains(r, 'id="avion"')

    def test_consulta_de_vuelos(self):
        codigo, r = self.enviar("get", "/api/vuelos")
        self.assertEqual(len(r["datos"]), 2)
        codigo, r = self.enviar("get", "/api/vuelos/AL-204")
        self.assertEqual(r["datos"]["destino"], "Quito")
        codigo, r = self.enviar("get", "/api/vuelos/XX-000")
        self.assertEqual(codigo, 404)

    def test_registrar_vuelo(self):
        datos = {"codigo": "al-450", "origen": "Guayaquil", "destino": "Loja",
                 "fecha": "2026-12-30", "hora": "09:15"}
        codigo, r = self.enviar("post", "/api/vuelos", datos)
        self.assertEqual(codigo, 201)
        self.assertEqual(r["datos"]["codigo"], "AL-450")
        self.assertEqual(self.enviar("post", "/api/vuelos", datos)[0], 400)      # repetido
        malo = dict(datos, codigo="AL-451", fecha="30/12/2026")
        self.assertEqual(self.enviar("post", "/api/vuelos", malo)[0], 400)       # fecha mal
        with open(persistencia.RUTA_VUELOS, encoding="utf-8") as f:
            self.assertEqual(len(json.load(f)["vuelos"]), 3)                     # quedó en el JSON

    def test_resumen_y_listar(self):
        codigo, r = self.enviar("get", "/api/vuelos/AL-204/resumen")
        self.assertEqual(r["datos"], {"cantidad": 12, "vacia": False, "total_asientos": 68})
        codigo, r = self.enviar("get", "/api/vuelos/AL-204/reservas")
        self.assertEqual(len(r["datos"]), 12)
        self.assertEqual(r["datos"][0]["nombre"], "Diana")
        codigo, r = self.enviar("get", "/api/vuelos/AL-204/reservas?clase=Ejecutiva")
        nombres = [p["nombre"] for p in r["datos"]]
        self.assertEqual(nombres, ["Ana", "Elena", "Pedro"])

    def test_crear_reserva(self):
        codigo, r = self.nueva_reserva()
        self.assertEqual(codigo, 201)
        self.assertEqual(r["datos"]["numero"], 1013)
        self.assertEqual(self.enviar("get", "/api/vuelos/AL-204/resumen")[1]["datos"]["cantidad"], 13)

    def test_no_asiento_ocupado(self):
        codigo, r = self.nueva_reserva(asiento="7D", cedula="0911111111")
        self.assertEqual(codigo, 400)
        self.assertIn("ya está reservado", r["mensaje"])

    def test_no_cedula_repetida(self):
        self.nueva_reserva()
        codigo, r = self.nueva_reserva(asiento="9D")
        self.assertEqual(codigo, 400)
        self.assertIn("ya tiene una reserva", r["mensaje"])

    def test_validaciones(self):
        self.assertEqual(self.nueva_reserva(asiento="13A")[0], 400)              # no existe
        self.assertEqual(self.nueva_reserva(asiento="1B")[0], 400)               # Ejecutiva no tiene B
        self.assertEqual(self.nueva_reserva(cedula="123")[0], 400)
        self.assertEqual(self.nueva_reserva(nombre="")[0], 400)
        self.assertEqual(self.nueva_reserva(edad="abc")[0], 400)

    def test_buscar_por_numero_asiento_y_cedula(self):
        self.assertEqual(self.enviar("get", "/api/vuelos/AL-204/reservas/1002")[1]["datos"]["nombre"], "Ana")
        self.assertEqual(self.enviar("get", "/api/vuelos/AL-204/reservas/9999")[0], 404)
        self.assertEqual(self.enviar("get", "/api/vuelos/AL-204/asientos/7d")[1]["datos"]["nombre"], "Luis")
        self.assertIsNone(self.enviar("get", "/api/vuelos/AL-204/asientos/9C")[1]["datos"])
        self.assertEqual(self.enviar("get", "/api/vuelos/AL-204/cedulas/0934567890")[1]["datos"]["nombre"], "Beto")
        self.assertEqual(self.enviar("get", "/api/vuelos/AL-204/cedulas/0000000000")[0], 404)

    def test_modificar_reserva(self):
        self.nueva_reserva()
        datos = {"nombre": "Zoe P.", "edad": 21, "asiento": "11A"}
        codigo, r = self.enviar("put", "/api/vuelos/AL-204/reservas/1013", datos)
        self.assertEqual(codigo, 200)
        self.assertEqual(r["datos"]["asiento"], "11A")
        # el asiento 9C quedó libre y 11A ocupado
        self.assertIsNone(self.enviar("get", "/api/vuelos/AL-204/asientos/9C")[1]["datos"])
        # no se puede pasar a un asiento de otro
        self.assertEqual(self.enviar("put", "/api/vuelos/AL-204/reservas/1013",
                                     {"nombre": "Zoe", "edad": 21, "asiento": "7D"})[0], 400)
        self.assertEqual(self.enviar("put", "/api/vuelos/AL-204/reservas/9999", datos)[0], 404)

    def test_eliminar_reserva(self):
        codigo, r = self.enviar("delete", "/api/vuelos/AL-204/reservas/1005")
        self.assertEqual(codigo, 200)
        self.assertIsNone(self.enviar("get", "/api/vuelos/AL-204/asientos/3C")[1]["datos"])
        self.assertEqual(self.enviar("get", "/api/vuelos/AL-204/resumen")[1]["datos"]["cantidad"], 11)
        self.assertEqual(self.enviar("delete", "/api/vuelos/AL-204/reservas/9999")[0], 404)

    def test_datos_se_guardan_en_json_y_sobreviven_al_reinicio(self):
        self.nueva_reserva()                                                      # crear
        self.enviar("put", "/api/vuelos/AL-204/reservas/1002",
                    {"nombre": "Ana María", "edad": 29, "asiento": "1A"})         # modificar
        self.enviar("delete", "/api/vuelos/AL-204/reservas/1005")                 # eliminar

        with open(persistencia.RUTA_RESERVAS, encoding="utf-8") as f:             # lo que quedó en el disco
            en_disco = json.load(f)["reservas"]["AL-204"]
        self.assertEqual(len(en_disco), 12)                                       # 12 + 1 - 1

        persistencia.cargar()                                                     # "reiniciar el servidor"
        lista = persistencia.lista_de("AL-204")
        self.assertEqual(lista.longitud(), 12)
        self.assertEqual(lista.buscar(1013).nombre, "Zoe")
        self.assertEqual(lista.buscar(1002).nombre, "Ana María")
        self.assertIsNone(lista.buscar(1005))
        self.assertEqual(numeros(lista.listar())[-1], 1013)                       # conserva el orden
        self.assertEqual(self.nueva_reserva(asiento="9D", cedula="0922222222")[1]["datos"]["numero"], 1014)

    def test_cada_vuelo_tiene_su_lista(self):
        # la misma cédula puede viajar en otro vuelo, pero el asiento 7D de AL-204 sigue ocupado
        codigo, r = self.enviar("post", "/api/vuelos/AL-310/reservas",
                                {"nombre": "Luis", "cedula": "0987654321", "edad": 35, "asiento": "7D"})
        self.assertEqual(codigo, 201)
        self.assertEqual(self.enviar("get", "/api/vuelos/AL-204/asientos/7D")[1]["datos"]["nombre"], "Luis")
