# ==============================================================
# vuelo.py · Forma del avión (igual para todos los vuelos)
# --------------------------------------------------------------
# El avión tiene 12 filas:
#    - Filas 1 y 2  → clase Ejecutiva (asientos A C | D F       → 4 por fila)
#    - Filas 3 a 12 → clase Económica (asientos A B C | D E F   → 6 por fila)
#    Total: 2 x 4 + 10 x 6 = 68 asientos.
# Un asiento se escribe como fila + letra: "1A", "7D", "12F".
# ==============================================================

AVION = {
    "filas": 12,
    "filas_ejecutiva": 2,
    "letras_ejecutiva": ["A", "C", "D", "F"],
    "letras_economica": ["A", "B", "C", "D", "E", "F"],
}


def total_asientos():
    """Calcula cuántos asientos tiene el avión (68)."""
    ejecutiva = AVION["filas_ejecutiva"] * len(AVION["letras_ejecutiva"])
    economica = (AVION["filas"] - AVION["filas_ejecutiva"]) * len(AVION["letras_economica"])
    return ejecutiva + economica


def separar_asiento(asiento):
    """Separa '12A' en (12, 'A'). Si no tiene forma de asiento, retorna (0, '')."""
    asiento = str(asiento).strip().upper()
    if len(asiento) < 2:
        return 0, ""
    fila_texto = asiento[:-1]          # todo menos la última letra → "12"
    letra = asiento[-1]                # solo la última letra       → "A"
    if not fila_texto.isdigit():
        return 0, ""
    return int(fila_texto), letra


def clase_de_asiento(asiento):
    """'1A' → 'Ejecutiva' · '7D' → 'Económica'."""
    fila, letra = separar_asiento(asiento)
    if fila <= AVION["filas_ejecutiva"]:
        return "Ejecutiva"
    return "Económica"


def asiento_existe(asiento):
    """True si el asiento existe en este avión ('13A' o '1B' no existen)."""
    fila, letra = separar_asiento(asiento)
    if fila < 1 or fila > AVION["filas"]:
        return False
    if fila <= AVION["filas_ejecutiva"]:
        return letra in AVION["letras_ejecutiva"]
    return letra in AVION["letras_economica"]
