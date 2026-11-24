# ==============================================================
# lista_pasajeros.py · Lista enlazada de pasajeros
# --------------------------------------------------------------
#        head
#         |
#         v
#    +----------+---+    +----------+---+    +----------+---+
#    | #1005    | o-+--->| #1002    | o-+--->| #1009    | o-+---> None
#    | Diana 3C |   |    | Ana 1A   |   |    | Luis 7D  |   |
#    +----------+---+    +----------+---+    +----------+---+
#       data    next        data    next        data    next
#
# Los pasajeros quedan en ORDEN DE LLEGADA (el orden en que reservaron).
# Reglas: se recorre siempre con  actual = self.head / while actual is not None;
# la clase no imprime ni pide datos: RETORNA los valores.
# ==============================================================


class Nodo:
    """Un nodo: lleva un pasajero (data) y la referencia al siguiente nodo (next)."""

    def __init__(self, data):
        self.data = data          # el Pasajero guardado en este nodo
        self.next = None          # al nacer no apunta a ningún nodo


class ListaPasajeros:
    """Lista enlazada simple con todas las reservas de UN vuelo."""

    def __init__(self):
        self.head = None          # primer nodo (None = lista vacía)
        self.cantidad = 0         # cuántas reservas hay

    # Agrega un pasajero NUEVO al final de la lista (orden de llegada)
    def ingresar(self, pasajero):
        nuevo = Nodo(pasajero)                    # 1. creo el nodo con el pasajero
        if self.head is None:                     # 2a. lista vacía: el nuevo es la cabeza
            self.head = nuevo
        else:                                     # 2b. busco el último nodo
            actual = self.head
            while actual.next is not None:
                actual = actual.next
            actual.next = nuevo                   #     el último ahora apunta al nuevo
        self.cantidad = self.cantidad + 1         # 3. hay una reserva más
        return True

    # 1. True si no hay reservas, False si hay al menos una
    def esta_vacia(self):
        return self.head is None

    # 2. Cuántas reservas hay (no se recorre: ingresar y eliminar llevan la cuenta)
    def longitud(self):
        return self.cantidad

    # 3. Retorna una list con todos los Pasajero, desde head hasta el último
    def listar(self):
        resultado = []
        actual = self.head
        while actual is not None:
            resultado.append(actual.data)         # guardo el pasajero, no el nodo
            actual = actual.next
        return resultado

    # 4. Búsqueda lineal por número de reserva. Retorna el Pasajero o None
    def buscar(self, numero):
        actual = self.head
        while actual is not None:
            if actual.data.numero == numero:
                return actual.data
            actual = actual.next
        return None

    # 5. Retorna el Pasajero que ocupa ese asiento ("7D") o None si está libre
    def buscar_por_asiento(self, asiento):
        actual = self.head
        while actual is not None:
            if actual.data.asiento == asiento:
                return actual.data
            actual = actual.next
        return None

    # 6. Retorna el Pasajero con esa cédula (texto) o None
    def buscar_por_cedula(self, cedula):
        actual = self.head
        while actual is not None:
            if actual.data.cedula == cedula:
                return actual.data
            actual = actual.next
        return None

    # 7. Cambia nombre, edad y asiento. Reutiliza buscar(). True si lo modificó, False si no existe
    def modificar(self, numero, nuevo_nombre, nueva_edad, nuevo_asiento):
        pasajero = self.buscar(numero)
        if pasajero is None:
            return False
        pasajero.nombre = nuevo_nombre            # el nodo no cambia de lugar:
        pasajero.edad = nueva_edad                # solo cambian los datos que lleva
        pasajero.asiento = nuevo_asiento
        return True

    # 8. Cancela la reserva. Retorna el Pasajero eliminado o None si no existía
    def eliminar(self, numero):
        # Caso A: lista vacía
        if self.head is None:
            return None

        # Caso B: es la cabeza
        if self.head.data.numero == numero:
            eliminado = self.head.data
            self.head = self.head.next            # la cabeza pasa al segundo nodo
            self.cantidad = self.cantidad - 1
            return eliminado

        # Caso C: está en medio o al final (me paro en el nodo ANTERIOR)
        anterior = self.head
        while anterior.next is not None:
            if anterior.next.data.numero == numero:
                eliminado = anterior.next.data
                anterior.next = anterior.next.next   # el anterior "se salta" el nodo
                self.cantidad = self.cantidad - 1
                return eliminado
            anterior = anterior.next

        # Caso D: no existe
        return None

    # 9. Retorna una list con los pasajeros de esa clase ("Ejecutiva" o "Económica")
    def filtrar_por_clase(self, clase):
        resultado = []
        actual = self.head
        while actual is not None:
            if actual.data.clase() == clase:
                resultado.append(actual.data)
            actual = actual.next
        return resultado
