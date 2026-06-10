"""
pf_Algoritmos
Módulo: clsUsuarios
Descripción: Clase para gestionar usuarios del sistema de préstamos
"""

import re
import json
import os
from datetime import datetime


class clsUsuarios:
    """
    Clase para gestionar los usuarios del sistema de préstamos.
    Permite registrar, buscar y listar usuarios.
    """

    ARCHIVO_USUARIOS = "datos/usuarios.json"

    def __init__(self):
        """Constructor de la clase clsUsuarios."""
        self._usuarios = []
        self._cargar_usuarios()

    # ──────────────────────────────────────────────
    # Validaciones
    # ──────────────────────────────────────────────

    @staticmethod
    def validar_nombre(nombre: str) -> tuple[bool, str]:
        """Valida que el nombre tenga al menos 3 letras y no contenga números."""
        if len(nombre.strip()) < 3:
            return False, "El nombre debe tener al menos 3 caracteres."
        if any(c.isdigit() for c in nombre):
            return False, "El nombre no puede contener números."
        return True, ""

    @staticmethod
    def validar_documento(doc: str) -> tuple[bool, str]:
        """Valida que el documento tenga entre 3 y 15 dígitos numéricos."""
        if not doc.isdigit():
            return False, "El documento solo puede contener números."
        if not (3 <= len(doc) <= 15):
            return False, "El documento debe tener entre 3 y 15 dígitos."
        return True, ""

    @staticmethod
    def validar_correo(correo: str) -> tuple[bool, str]:
        """Valida el formato básico del correo electrónico."""
        patron = r'^[\w\.-]+@[\w\.-]+\.com$'
        if re.match(patron, correo):
            return True, ""
        return False, "Correo inválido. Debe contener '@' y terminar en '.com'."

    @staticmethod
    def validar_dias_prestamo(dias: str) -> tuple[bool, str]:
        """Valida que los días de préstamo sean 5, 10, 15 o 30."""
        opciones = {"5", "10", "15", "30"}
        if dias in opciones:
            return True, ""
        return False, "Días de préstamo inválido. Opciones: 5, 10, 15, 30."

    # ──────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────

    def registrar_usuario(self, nombre: str, apellido: str, documento: str,
                          correo: str, dias_prestamo: int) -> dict:
        """Registra un nuevo usuario en el sistema."""
        usuario = {
            "id": documento,
            "nombre": nombre.strip(),
            "apellido": apellido.strip(),
            "documento": documento.strip(),
            "correo": correo.strip().lower(),
            "dias_prestamo": int(dias_prestamo),
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._usuarios.append(usuario)
        self._guardar_usuarios()
        return usuario

    def buscar_por_documento(self, documento: str) -> dict | None:
        """Busca un usuario por su número de documento."""
        for u in self._usuarios:
            if u["documento"] == documento.strip():
                return u
        return None

    def listar_usuarios(self) -> list:
        """Retorna la lista completa de usuarios."""
        return self._usuarios

    def documento_existe(self, documento: str) -> bool:
        """Verifica si un documento ya está registrado."""
        return self.buscar_por_documento(documento) is not None

    # ──────────────────────────────────────────────
    # Persistencia
    # ──────────────────────────────────────────────

    def _cargar_usuarios(self):
        """Carga los usuarios desde el archivo JSON."""
        os.makedirs("datos", exist_ok=True)
        if os.path.exists(self.ARCHIVO_USUARIOS):
            try:
                with open(self.ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
                    self._usuarios = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._usuarios = []
        else:
            self._usuarios = []

    def _guardar_usuarios(self):
        """Guarda los usuarios en el archivo JSON."""
        os.makedirs("datos", exist_ok=True)
        with open(self.ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(self._usuarios, f, ensure_ascii=False, indent=4)

    def exportar_csv(self):
        """Exporta la lista de usuarios a un archivo CSV."""
        import csv
        ruta = "datos/usuarios.csv"
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            campos = ["documento", "nombre", "apellido", "correo", "dias_prestamo", "fecha_registro"]
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for u in self._usuarios:
                writer.writerow({k: u.get(k, "") for k in campos})
        return ruta
