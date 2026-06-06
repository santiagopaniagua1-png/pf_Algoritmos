"""
pf_Algoritmos
Módulo: clsPrestamo
Descripción: Clase principal para gestionar préstamos, devoluciones y facturación
"""

import json
import os
import csv
from datetime import datetime, timedelta


class clsPrestamo:
    """
    Clase para gestionar los préstamos del sistema.
    Maneja registro, devolución, certificados y facturación.
    """

    ARCHIVO_PRESTAMOS = "datos/prestamos.json"
    IMPUESTO_CONCHUDEZ = 0.23  # impuesto
    DIAS_VENTA = 30
    DIAS_NOTIFICACION = 20

    def __init__(self):
        """Constructor de la clase clsPrestamo."""
        self._prestamos = []
        self._cargar_prestamos()

    # ──────────────────────────────────────────────
    # Registro de préstamo
    # ──────────────────────────────────────────────

    def registrar_prestamo(self, usuario: dict, item: dict) -> dict:
        """Registra un nuevo préstamo."""
        fecha_prestamo = datetime.now()
        fecha_limite = fecha_prestamo + timedelta(days=usuario["dias_prestamo"])

        prestamo = {
            "id_prestamo": self._generar_id_prestamo(),
            "documento_usuario": usuario["documento"],
            "nombre_usuario": f"{usuario['nombre']} {usuario['apellido']}",
            "correo_usuario": usuario["correo"],
            "id_item": item["id"],
            "nombre_item": item["nombre"],
            "categoria_item": item["categoria"],
            "precio_compra": item["precio_compra"],
            "dias_prestamo": usuario["dias_prestamo"],
            "fecha_prestamo": fecha_prestamo.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_limite": fecha_limite.strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo",
            "fecha_devolucion": None,
            "facturado": False,
        }
        self._prestamos.append(prestamo)
        self._guardar_prestamos()
        return prestamo

    def _generar_id_prestamo(self) -> str:
        """Genera un ID único para el préstamo."""
        import uuid
        ids = {p["id_prestamo"] for p in self._prestamos}
        nuevo = f"PR-{uuid.uuid4().hex[:8].upper()}"
        while nuevo in ids:
            nuevo = f"PR-{uuid.uuid4().hex[:8].upper()}"
        return nuevo

    # ──────────────────────────────────────────────
    # Consultas
    # ──────────────────────────────────────────────

    def prestamos_activos_usuario(self, documento: str) -> list:
        """Retorna los préstamos activos de un usuario."""
        return [p for p in self._prestamos
                if p["documento_usuario"] == documento and p["estado"] == "activo"]

    def todos_activos(self) -> list:
        """Retorna todos los préstamos activos."""
        return [p for p in self._prestamos if p["estado"] == "activo"]

    def prestamos_por_mas_de_dias(self, dias: int) -> list:
        """Retorna préstamos activos con más de N días transcurridos."""
        ahora = datetime.now()
        resultado = []
        for p in self._prestamos:
            if p["estado"] == "activo":
                fecha_p = datetime.strptime(p["fecha_prestamo"], "%Y-%m-%d %H:%M:%S")
                delta = (ahora - fecha_p).days
                if delta > dias:
                    p_copia = dict(p)
                    p_copia["dias_transcurridos"] = delta
                    resultado.append(p_copia)
        return resultado

    def prestamos_para_notificar(self) -> list:
        """Retorna préstamos activos con más de 20 días (candidatos a notificación)."""
        return self.prestamos_por_mas_de_dias(self.DIAS_NOTIFICACION)

    def prestamos_para_vender(self) -> list:
        """Retorna préstamos activos con más de 30 días (candidatos a venta)."""
        return self.prestamos_por_mas_de_dias(self.DIAS_VENTA)

    def dias_transcurridos(self, prestamo: dict) -> int:
        """Calcula los días transcurridos de un préstamo."""
        fecha_p = datetime.strptime(prestamo["fecha_prestamo"], "%Y-%m-%d %H:%M:%S")
        return (datetime.now() - fecha_p).days

    def listar_ordenados_por_dias(self) -> list:
        """Lista todos los préstamos activos ordenados por días transcurridos (mayor a menor)."""
        activos = self.todos_activos()
        for p in activos:
            p["dias_transcurridos"] = self.dias_transcurridos(p)
        return sorted(activos, key=lambda x: x["dias_transcurridos"], reverse=True)

    # ──────────────────────────────────────────────
    # Devolución
    # ──────────────────────────────────────────────

    def registrar_devolucion(self, id_prestamo: str) -> dict | None:
        """Registra la devolución de un préstamo activo."""
        for p in self._prestamos:
            if p["id_prestamo"] == id_prestamo and p["estado"] == "activo":
                p["estado"] = "devuelto"
                p["fecha_devolucion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._guardar_prestamos()
                return p
        return None

    def generar_certificado_devolucion(self, prestamo: dict) -> str:
        """
        Genera un certificado de devolución en texto plano.
        Nombre del archivo: NombreUsuario_FechaDevolucion_IDPrestamo.txt
        """
        os.makedirs("certificados", exist_ok=True)
        fecha_dev = prestamo.get("fecha_devolucion", datetime.now().strftime("%Y-%m-%d"))
        fecha_safe = fecha_dev.replace(":", "-").replace(" ", "_")
        nombre_safe = prestamo["nombre_usuario"].replace(" ", "_")
        nombre_archivo = f"certificados/{nombre_safe}_{fecha_safe}_{prestamo['id_prestamo']}.txt"

        fecha_prestamo = datetime.strptime(prestamo["fecha_prestamo"], "%Y-%m-%d %H:%M:%S")
        fecha_devolucion = datetime.strptime(prestamo["fecha_devolucion"], "%Y-%m-%d %H:%M:%S")
        dias_usados = (fecha_devolucion - fecha_prestamo).days

        contenido = f"""
╔══════════════════════════════════════════════════════════════════╗
║              CERTIFICADO DE DEVOLUCIÓN - BROWNMIND                ║
╚══════════════════════════════════════════════════════════════════╝

  Fecha de emisión  : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
  ID de Préstamo    : {prestamo['id_prestamo']}

─────────────────────────────────────────────────────────────────
  DATOS DEL PRESTATARIO
─────────────────────────────────────────────────────────────────
  Nombre            : {prestamo['nombre_usuario']}
  Documento         : {prestamo['documento_usuario']}
  Correo            : {prestamo['correo_usuario']}

─────────────────────────────────────────────────────────────────
  DATOS DEL ÍTEM DEVUELTO
─────────────────────────────────────────────────────────────────
  ID Ítem           : {prestamo['id_item']}
  Nombre            : {prestamo['nombre_item']}
  Categoría         : {prestamo['categoria_item']}

─────────────────────────────────────────────────────────────────
  DETALLES DEL PRÉSTAMO
─────────────────────────────────────────────────────────────────
  Fecha de préstamo : {prestamo['fecha_prestamo']}
  Fecha de límite   : {prestamo['fecha_limite']}
  Fecha devolución  : {prestamo['fecha_devolucion']}
  Días utilizados   : {dias_usados} día(s)
  Días acordados    : {prestamo['dias_prestamo']} día(s)

─────────────────────────────────────────────────────────────────
  El ítem fue devuelto {'en el tiempo acordado' if dias_usados <= prestamo['dias_prestamo'] else 'FUERA del tiempo acordado'}.

  Este certificado confirma que el ítem ha sido devuelto
  satisfactoriamente a BROWNMIND.

                          _____________________
                                BROWNMIND
                                Prestador

╚══════════════════════════════════════════════════════════════════╝
"""
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        return nombre_archivo

    # ──────────────────────────────────────────────
    # Facturación
    # ──────────────────────────────────────────────

    def generar_factura_venta(self, prestamos_vender: list) -> str:
        """
        Genera una factura de venta para ítems prestados por más de 30 días.
        Aplica impuesto por conchudez del 23%.
        """
        os.makedirs("facturas", exist_ok=True)
        if not prestamos_vender:
            return ""

        fecha_ahora = datetime.now()
        nombre_usuario = prestamos_vender[0]["nombre_usuario"].replace(" ", "_")
        id_primero = prestamos_vender[0]["id_prestamo"]
        nombre_archivo = f"facturas/{nombre_usuario}_{id_primero}.txt"

        subtotal = sum(p["precio_compra"] for p in prestamos_vender)
        impuesto = subtotal * self.IMPUESTO_CONCHUDEZ
        total = subtotal + impuesto

        lineas_items = ""
        for p in prestamos_vender:
            dias = self.dias_transcurridos(p)
            lineas_items += (
                f"  {p['id_item']:<15} {p['nombre_item']:<30} "
                f"${p['precio_compra']:>10,.2f}   {dias} días\n"
            )
            # Marcar como facturado
            for pr in self._prestamos:
                if pr["id_prestamo"] == p["id_prestamo"]:
                    pr["facturado"] = True
                    pr["estado"] = "vendido"
            self._guardar_prestamos()

        contenido = f"""
╔══════════════════════════════════════════════════════════════════╗
║                  FACTURA DE VENTA - BROWNMIND                     ║
╚══════════════════════════════════════════════════════════════════╝

  Fecha              : {fecha_ahora.strftime("%Y-%m-%d %H:%M:%S")}
  Factura N°         : {id_primero}

─────────────────────────────────────────────────────────────────
  CLIENTE
─────────────────────────────────────────────────────────────────
  Nombre             : {prestamos_vender[0]['nombre_usuario']}
  Documento          : {prestamos_vender[0]['documento_usuario']}
  Correo             : {prestamos_vender[0]['correo_usuario']}

─────────────────────────────────────────────────────────────────
  MOTIVACIÓN
─────────────────────────────────────────────────────────────────
  Los siguientes ítems han superado los {self.DIAS_VENTA} días de préstamo
  acordados. Según el acuerdo entre las partes, el prestatario
  debe adquirir los ítems al precio de compra original de MJ,
  más un impuesto por conchudez del {int(self.IMPUESTO_CONCHUDEZ*100)}%.

─────────────────────────────────────────────────────────────────
  DETALLE DE ÍTEMS
─────────────────────────────────────────────────────────────────
  {'ID':<15} {'Nombre':<30} {'Precio':>12}   {'Días'}
  {'-'*70}
{lineas_items}
─────────────────────────────────────────────────────────────────
  RESUMEN
─────────────────────────────────────────────────────────────────
  Subtotal                         : ${subtotal:>12,.2f}
  Impuesto por conchudez (23%)     : ${impuesto:>12,.2f}
  ─────────────────────────────────────────────────
  TOTAL A PAGAR                    : ${total:>12,.2f}
─────────────────────────────────────────────────────────────────

  ¡Gracias por comprar lo que debías devolver! 😄

                          _____________________
                               BROWNMIND
                               Prestador
╚══════════════════════════════════════════════════════════════════╝
"""
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        return nombre_archivo

    # ──────────────────────────────────────────────
    # Estadísticas
    # ──────────────────────────────────────────────

    def estadisticas(self) -> dict:
        """Retorna estadísticas generales de los préstamos."""
        total = len(self._prestamos)
        activos = len([p for p in self._prestamos if p["estado"] == "activo"])
        devueltos = len([p for p in self._prestamos if p["estado"] == "devuelto"])
        vendidos = len([p for p in self._prestamos if p["estado"] == "vendido"])
        total_ventas = sum(
            p["precio_compra"] * (1 + self.IMPUESTO_CONCHUDEZ)
            for p in self._prestamos if p["estado"] == "vendido"
        )

        conteo_usuarios: dict = {}
        for p in self._prestamos:
            doc = p["documento_usuario"]
            nombre = p["nombre_usuario"]
            conteo_usuarios[doc] = conteo_usuarios.get(doc, {"nombre": nombre, "cantidad": 0})
            conteo_usuarios[doc]["cantidad"] += 1

        usuario_max = max(conteo_usuarios.values(), key=lambda x: x["cantidad"]) if conteo_usuarios else None
        usuario_min = min(conteo_usuarios.values(), key=lambda x: x["cantidad"]) if conteo_usuarios else None

        return {
            "total_prestamos": total,
            "activos": activos,
            "devueltos": devueltos,
            "vendidos": vendidos,
            "total_ventas": round(total_ventas, 2),
            "usuario_max": usuario_max,
            "usuario_min": usuario_min,
            "lista_usuarios": list(conteo_usuarios.values()),
        }

    # ──────────────────────────────────────────────
    # Persistencia
    # ──────────────────────────────────────────────

    def _cargar_prestamos(self):
        """Carga los préstamos desde el archivo JSON."""
        os.makedirs("datos", exist_ok=True)
        if os.path.exists(self.ARCHIVO_PRESTAMOS):
            try:
                with open(self.ARCHIVO_PRESTAMOS, "r", encoding="utf-8") as f:
                    self._prestamos = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._prestamos = []
        else:
            self._prestamos = []

    def _guardar_prestamos(self):
        """Guarda los préstamos en el archivo JSON."""
        os.makedirs("datos", exist_ok=True)
        with open(self.ARCHIVO_PRESTAMOS, "w", encoding="utf-8") as f:
            json.dump(self._prestamos, f, ensure_ascii=False, indent=4)

    def exportar_csv(self):
        """Exporta los préstamos a un archivo CSV."""
        ruta = "datos/prestamos.csv"
        campos = ["id_prestamo", "documento_usuario", "nombre_usuario", "id_item",
                  "nombre_item", "categoria_item", "precio_compra", "dias_prestamo",
                  "fecha_prestamo", "fecha_limite", "estado", "fecha_devolucion", "facturado"]
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for p in self._prestamos:
                writer.writerow({k: p.get(k, "") for k in campos})
        return ruta
