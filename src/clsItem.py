"""
pf_Algoritmos
Módulo: clsItem
Descripción: Clase para gestionar los ítems del inventario de préstamos
"""

import json
import os
import uuid
import random
from datetime import datetime


class clsItem:
    """
    Clase para gestionar los ítems  del inventario de préstamos.
    
    """

    ARCHIVO_ITEMS = "datos/items.json"

    CATEGORIAS = {
        "1": ("Videojuegos", "VJ"),
        "2": ("Libros", "LB"),
        "3": ("Música y video", "MV"),
        "4": ("Herramientas", "HT"),
        "5": ("Dinero", "DN"),
        "6": ("Misceláneo y varios", "MV2"),
    }

    # etiquetas de estado
    ESTADOS_DIFUSOS = [
        (0,  20,  "Muy malo"),
        (20, 40,  "Malo"),
        (40, 60,  "Regular"),
        (60, 80,  "Bueno"),
        (80, 100, "Excelente"),
    ]

    def __init__(self):
        """Constructor de la clase clsItem."""
        self._items = []
        self._cargar_items()

    # ──────────────────────────────────────────────
    # Lógica difusa
    # ──────────────────────────────────────────────

    @staticmethod
    def evaluar_estado_difuso(valor: float) -> tuple[str, float]:
        """
        Evalúa el estado del ítem usando lógica difusa simple.
        Retorna la etiqueta lingüística y el grado de pertenencia dominante.
        """
        # Conjuntos
        conjuntos = {
            "Muy malo":  lambda x: max(0.0, min(1.0, (20 - x) / 20)) if x <= 20 else 0.0,
            "Malo":      lambda x: max(0.0, min((x - 10) / 10, (40 - x) / 10)) if 10 <= x <= 40 else 0.0,
            "Regular":   lambda x: max(0.0, min((x - 30) / 10, (60 - x) / 10)) if 30 <= x <= 60 else 0.0,
            "Bueno":     lambda x: max(0.0, min((x - 50) / 10, (80 - x) / 10)) if 50 <= x <= 80 else 0.0,
            "Excelente": lambda x: max(0.0, (x - 70) / 30) if x >= 70 else 0.0,
        }

        grados = {etiq: fn(valor) for etiq, fn in conjuntos.items()}
        etiqueta_max = max(grados, key=grados.get)
        return etiqueta_max, round(grados[etiqueta_max], 2)

    # ──────────────────────────────────────────────
    # Generador de ID único
    # ──────────────────────────────────────────────

    def _generar_id(self, prefijo_categoria: str) -> str:
        """Genera un ID único para el ítem combinando la categoría y un código."""
        sufijo = uuid.uuid4().hex[:6].upper()
        nuevo_id = f"{prefijo_categoria}-{sufijo}"
        # Asegura unicidad
        ids_existentes = {i["id"] for i in self._items}
        while nuevo_id in ids_existentes:
            sufijo = uuid.uuid4().hex[:6].upper()
            nuevo_id = f"{prefijo_categoria}-{sufijo}"
        return nuevo_id

    # ──────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────

    def registrar_item(self, nombre: str, clave_categoria: str,
                       precio_compra: float, valor_estado: float) -> dict:
        """Registra un nuevo ítem en el inventario."""
        nombre_cat, prefijo = self.CATEGORIAS[clave_categoria]
        etiqueta_estado, grado = self.evaluar_estado_difuso(valor_estado)
        item_id = self._generar_id(prefijo)

        item = {
            "id": item_id,
            "nombre": nombre.strip(),
            "categoria": nombre_cat,
            "precio_compra": round(precio_compra, 2),
            "valor_estado": round(valor_estado, 2),
            "estado_difuso": etiqueta_estado,
            "grado_pertenencia": grado,
            "disponible": True,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._items.append(item)
        self._guardar_items()
        return item

    def buscar_por_id(self, item_id: str) -> dict | None:
        """Busca un ítem por su ID."""
        for i in self._items:
            if i["id"].upper() == item_id.strip().upper():
                return i
        return None

    def listar_disponibles(self) -> list:
        """Retorna los ítems disponibles para préstamo."""
        return [i for i in self._items if i.get("disponible", True)]

    def listar_todos(self) -> list:
        """Retorna todos los ítems del inventario."""
        return self._items

    def marcar_prestado(self, item_id: str):
        """Marca un ítem como no disponible (prestado)."""
        for i in self._items:
            if i["id"].upper() == item_id.strip().upper():
                i["disponible"] = False
                break
        self._guardar_items()

    def marcar_disponible(self, item_id: str):
        """Marca un ítem como disponible (devuelto)."""
        for i in self._items:
            if i["id"].upper() == item_id.strip().upper():
                i["disponible"] = True
                break
        self._guardar_items()

    # ──────────────────────────────────────────────
    # Persistencia
    # ──────────────────────────────────────────────

    def _cargar_items(self):
        """Carga los ítems desde el archivo JSON."""
        os.makedirs("datos", exist_ok=True)
        if os.path.exists(self.ARCHIVO_ITEMS):
            try:
                with open(self.ARCHIVO_ITEMS, "r", encoding="utf-8") as f:
                    self._items = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._items = []
        else:
            self._items = []

    def _guardar_items(self):
        """Guarda los ítems en el archivo JSON."""
        os.makedirs("datos", exist_ok=True)
        with open(self.ARCHIVO_ITEMS, "w", encoding="utf-8") as f:
            json.dump(self._items, f, ensure_ascii=False, indent=4)

    def exportar_csv(self):
        """Exporta el inventario a un archivo CSV."""
        import csv
        ruta = "datos/items.csv"
        campos = ["id", "nombre", "categoria", "precio_compra",
                  "valor_estado", "estado_difuso", "grado_pertenencia",
                  "disponible", "fecha_registro"]
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for item in self._items:
                writer.writerow({k: item.get(k, "") for k in campos})
        return ruta
