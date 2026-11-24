# ==============================================================
# pasajero.py · La clase Pasajero
# Cada reserva del vuelo es un objeto Pasajero.
# La lista enlazada guarda un Pasajero dentro de cada Nodo (nodo.data).
# ==============================================================
from aerolista.vuelo import clase_de_asiento   # dice si un asiento es Ejecutiva o Económica


class Pasajero:
    """Un pasajero con su reserva en un vuelo."""

    def __init__(self, numero, nombre, cedula, edad, asiento):
        self.numero = numero      # int → 1005 (número de reserva: ÚNICO)
        self.nombre = nombre      # str → "Diana"
        self.cedula = cedula      # str → "0923456789" (texto, para no perder el 0 inicial)
        self.edad = edad          # int → 22
        self.asiento = asiento    # str → "3C" (fila + letra)

    def clase(self):
        """Retorna 'Ejecutiva' (filas 1-2) o 'Económica' (filas 3-12)."""
        return clase_de_asiento(self.asiento)

    def a_diccionario(self):
        """Convierte el objeto en un dict para guardarlo en JSON y enviarlo al navegador."""
        return {
            "numero": self.numero,
            "nombre": self.nombre,
            "cedula": self.cedula,
            "edad": self.edad,
            "asiento": self.asiento,
            "clase": self.clase(),
        }

    def __str__(self):
        return f"#{self.numero} | {self.nombre} | {self.cedula} | {self.edad} años | asiento {self.asiento}"
