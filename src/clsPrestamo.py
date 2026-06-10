"""
pf_Algoritmos
Módulo: clsPrestamo
Descripción: Clase principal para gestionar préstamos, devoluciones y facturación
"""

import json
import os
import csv
from datetime import datetime, timedelta

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


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
║              CERTIFICADO DE DEVOLUCIÓN - BORROWNMIND             ║
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
  satisfactoriamente a borownmind.

                          _____________________
                                Borrownmind
                                Prestador

╚══════════════════════════════════════════════════════════════════╝
"""
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        return nombre_archivo

    def generar_certificado_devolucion_pdf(self, prestamo: dict) -> str:
        """
        Genera un certificado de devolución en formato PDF usando reportlab.
        Nombre del archivo: NombreUsuario_FechaDevolucion_IDPrestamo.pdf
        """
        if not REPORTLAB_OK:
            raise ImportError("reportlab no está instalado. Ejecute: pip install reportlab")

        os.makedirs("certificados", exist_ok=True)
        fecha_dev = prestamo.get("fecha_devolucion", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        fecha_safe = fecha_dev.replace(":", "-").replace(" ", "_")
        nombre_safe = prestamo["nombre_usuario"].replace(" ", "_")
        ruta_pdf = f"certificados/{nombre_safe}_{fecha_safe}_{prestamo['id_prestamo']}.pdf"

        fecha_prestamo_dt = datetime.strptime(prestamo["fecha_prestamo"], "%Y-%m-%d %H:%M:%S")
        fecha_devolucion_dt = datetime.strptime(prestamo["fecha_devolucion"], "%Y-%m-%d %H:%M:%S")
        dias_usados = (fecha_devolucion_dt - fecha_prestamo_dt).days
        a_tiempo = dias_usados <= prestamo["dias_prestamo"]

        # ── Estilos ──
        doc = SimpleDocTemplate(ruta_pdf, pagesize=letter,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        AZUL = colors.HexColor("#1A3E6F")
        VERDE = colors.HexColor("#1A7A4A") if a_tiempo else colors.HexColor("#B22222")
        GRIS = colors.HexColor("#F0F4F8")

        st_titulo = ParagraphStyle("titulo", parent=styles["Title"],
                                   textColor=AZUL, fontSize=20, spaceAfter=4,
                                   alignment=TA_CENTER)
        st_subtitulo = ParagraphStyle("subtitulo", parent=styles["Normal"],
                                      textColor=colors.white, fontSize=10,
                                      alignment=TA_CENTER)
        st_seccion = ParagraphStyle("seccion", parent=styles["Heading2"],
                                    textColor=AZUL, fontSize=11, spaceBefore=12, spaceAfter=4)
        st_normal = ParagraphStyle("normal", parent=styles["Normal"], fontSize=10, leading=16)
        st_estado = ParagraphStyle("estado", parent=styles["Normal"],
                                   textColor=VERDE, fontSize=13, alignment=TA_CENTER,
                                   spaceBefore=8, spaceAfter=8)
        st_firma = ParagraphStyle("firma", parent=styles["Normal"],
                                  fontSize=10, alignment=TA_CENTER, spaceBefore=6)

        story = []

        # Encabezado con fondo azul simulado via tabla
        header_data = [[Paragraph("CERTIFICADO DE DEVOLUCIÓN", st_titulo)],
                       [Paragraph("Sistema de Préstamos BORROWNMIND", st_subtitulo)]]
        header_tbl = Table(header_data, colWidths=[17*cm])
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZUL),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#2C5F9E")),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, 1), colors.white),
            ("ROUNDEDCORNERS", [6]),
        ]))
        story.append(header_tbl)
        story.append(Spacer(1, 14))

        # Info del documento
        info_rows = [
            ["Fecha de emisión:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "ID Préstamo:", prestamo["id_prestamo"]],
        ]
        info_tbl = Table(info_rows, colWidths=[4*cm, 6*cm, 3.5*cm, 3.5*cm])
        info_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GRIS),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ]))
        story.append(info_tbl)
        story.append(Spacer(1, 12))

        # Sección: Prestatario
        story.append(Paragraph("Datos del Prestatario", st_seccion))
        story.append(HRFlowable(width="100%", thickness=1, color=AZUL))
        story.append(Spacer(1, 6))
        datos_usuario = [
            ["Nombre completo:", prestamo["nombre_usuario"]],
            ["Documento:", prestamo["documento_usuario"]],
            ["Correo electrónico:", prestamo["correo_usuario"]],
        ]
        tbl_u = Table(datos_usuario, colWidths=[5*cm, 12*cm])
        tbl_u.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, GRIS]),
        ]))
        story.append(tbl_u)
        story.append(Spacer(1, 10))

        # Sección: Ítem
        story.append(Paragraph("Ítem Devuelto", st_seccion))
        story.append(HRFlowable(width="100%", thickness=1, color=AZUL))
        story.append(Spacer(1, 6))
        datos_item = [
            ["ID del ítem:", prestamo["id_item"]],
            ["Nombre:", prestamo["nombre_item"]],
            ["Categoría:", prestamo["categoria_item"]],
        ]
        tbl_i = Table(datos_item, colWidths=[5*cm, 12*cm])
        tbl_i.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, GRIS]),
        ]))
        story.append(tbl_i)
        story.append(Spacer(1, 10))

        # Sección: Detalles del préstamo
        story.append(Paragraph("Detalles del Préstamo", st_seccion))
        story.append(HRFlowable(width="100%", thickness=1, color=AZUL))
        story.append(Spacer(1, 6))
        datos_prestamo = [
            ["Fecha de préstamo:", prestamo["fecha_prestamo"],
             "Días acordados:", str(prestamo["dias_prestamo"])],
            ["Fecha límite:", prestamo["fecha_limite"],
             "Días utilizados:", str(dias_usados)],
            ["Fecha de devolución:", prestamo["fecha_devolucion"], "", ""],
        ]
        tbl_p = Table(datos_prestamo, colWidths=[4.5*cm, 6*cm, 3.5*cm, 3*cm])
        tbl_p.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, GRIS]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
        ]))
        story.append(tbl_p)
        story.append(Spacer(1, 14))

        # Estado de la devolución
        estado_texto = "✔  Ítem devuelto EN EL TIEMPO ACORDADO" if a_tiempo \
            else "⚠  Ítem devuelto FUERA DEL TIEMPO ACORDADO"
        estado_tbl = Table([[Paragraph(estado_texto, st_estado)]],
                            colWidths=[17*cm])
        estado_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1),
             colors.HexColor("#E8F5E9") if a_tiempo else colors.HexColor("#FFEBEE")),
            ("BOX", (0, 0), (-1, -1), 1,
             VERDE),
            ("ROUNDEDCORNERS", [4]),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(estado_tbl)
        story.append(Spacer(1, 20))

        # Firma
        firma_data = [
            ["", "_____________________________", ""],
            ["", "      BORROWNMIND", ""],
            ["", "Prestador — BORROWNMIND", ""],
        ]
        tbl_f = Table(firma_data, colWidths=[5*cm, 7*cm, 5*cm])
        tbl_f.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(tbl_f)

        doc.build(story)
        return ruta_pdf

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
║                  FACTURA DE VENTA - BORROWMIND                     ║
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
  debe adquirir los ítems al precio de compra original de BOROWMIND,
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
                                Brwmain
                               Prestador
╚══════════════════════════════════════════════════════════════════╝
"""
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        return nombre_archivo

    def generar_factura_venta_pdf(self, prestamos_vender: list) -> str:
        """
        Genera una factura de venta en formato PDF usando reportlab.
        Aplica impuesto por conchudez del 23%.
        Nombre del archivo: NombreUsuario_IDPrestamo.pdf
        """
        if not REPORTLAB_OK:
            raise ImportError("reportlab no está instalado. Ejecute: pip install reportlab")
        if not prestamos_vender:
            return ""

        os.makedirs("facturas", exist_ok=True)
        fecha_ahora = datetime.now()
        nombre_usuario = prestamos_vender[0]["nombre_usuario"].replace(" ", "_")
        id_primero = prestamos_vender[0]["id_prestamo"]
        ruta_pdf = f"facturas/{nombre_usuario}_{id_primero}.pdf"

        subtotal = sum(p["precio_compra"] for p in prestamos_vender)
        impuesto = subtotal * self.IMPUESTO_CONCHUDEZ
        total = subtotal + impuesto

        # Marcar como vendido
        for p in prestamos_vender:
            for pr in self._prestamos:
                if pr["id_prestamo"] == p["id_prestamo"]:
                    pr["facturado"] = True
                    pr["estado"] = "vendido"
        self._guardar_prestamos()

        # ── Estilos ──
        doc = SimpleDocTemplate(ruta_pdf, pagesize=letter,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        ROJO = colors.HexColor("#B22222")
        ROJO_CLARO = colors.HexColor("#8B0000")
        GRIS = colors.HexColor("#F5F5F5")
        GRIS_OSC = colors.HexColor("#CCCCCC")

        st_titulo = ParagraphStyle("titulo", parent=styles["Title"],
                                   textColor=colors.white, fontSize=20,
                                   alignment=TA_CENTER)
        st_subtitulo = ParagraphStyle("subtitulo", parent=styles["Normal"],
                                      textColor=colors.HexColor("#FFCCCC"), fontSize=10,
                                      alignment=TA_CENTER)
        st_seccion = ParagraphStyle("seccion", parent=styles["Heading2"],
                                    textColor=ROJO, fontSize=11, spaceBefore=12, spaceAfter=4)
        st_motivacion = ParagraphStyle("motiv", parent=styles["Normal"],
                                       fontSize=10, leading=16, textColor=colors.HexColor("#333333"))
        st_total = ParagraphStyle("total", parent=styles["Normal"],
                                  fontSize=13, fontName="Helvetica-Bold",
                                  textColor=ROJO, alignment=TA_RIGHT)

        story = []

        # Header rojo
        header_data = [
            [Paragraph("FACTURA DE VENTA", st_titulo)],
            [Paragraph("BORROWNMIND — Sistema de Préstamos", st_subtitulo)],
        ]
        header_tbl = Table(header_data, colWidths=[17*cm])
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ROJO),
            ("BACKGROUND", (0, 1), (-1, 1), ROJO_CLARO),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(header_tbl)
        story.append(Spacer(1, 12))

        # Metadatos factura
        meta_rows = [
            ["Factura N°:", id_primero,
             "Fecha:", fecha_ahora.strftime("%Y-%m-%d %H:%M:%S")],
        ]
        meta_tbl = Table(meta_rows, colWidths=[3.5*cm, 6*cm, 3*cm, 4.5*cm])
        meta_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GRIS),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, GRIS_OSC),
        ]))
        story.append(meta_tbl)
        story.append(Spacer(1, 10))

        # Cliente
        story.append(Paragraph("Cliente", st_seccion))
        story.append(HRFlowable(width="100%", thickness=1, color=ROJO))
        story.append(Spacer(1, 6))
        cliente_rows = [
            ["Nombre:", prestamos_vender[0]["nombre_usuario"]],
            ["Documento:", prestamos_vender[0]["documento_usuario"]],
            ["Correo:", prestamos_vender[0]["correo_usuario"]],
        ]
        tbl_c = Table(cliente_rows, colWidths=[4*cm, 13*cm])
        tbl_c.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, GRIS]),
        ]))
        story.append(tbl_c)
        story.append(Spacer(1, 10))

        # Motivación
        story.append(Paragraph("Motivación", st_seccion))
        story.append(HRFlowable(width="100%", thickness=1, color=ROJO))
        story.append(Spacer(1, 6))
        motiv_texto = (
            f"Los siguientes ítems han superado los <b>{self.DIAS_VENTA} días</b> de préstamo acordados. "
            f"Según el acuerdo entre las partes, el prestatario debe adquirir los ítems al precio de "
            f"compra original, más un <b>impuesto por conchudez del {int(self.IMPUESTO_CONCHUDEZ*100)}%</b>."
        )
        story.append(Paragraph(motiv_texto, st_motivacion))
        story.append(Spacer(1, 10))

        # Detalle de ítems
        story.append(Paragraph("Detalle de Ítems", st_seccion))
        story.append(HRFlowable(width="100%", thickness=1, color=ROJO))
        story.append(Spacer(1, 6))

        tabla_encabezado = [["ID Ítem", "Nombre del Ítem", "Categoría", "Días", "Precio"]]
        tabla_filas = []
        for p in prestamos_vender:
            dias = self.dias_transcurridos(p)
            tabla_filas.append([
                p["id_item"],
                p["nombre_item"],
                p["categoria_item"],
                str(dias),
                f"${p['precio_compra']:,.2f}",
            ])
        tabla_items = tabla_encabezado + tabla_filas
        tbl_items = Table(tabla_items, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 2*cm, 2.5*cm])
        tbl_items.setStyle(TableStyle([
            # Encabezado
            ("BACKGROUND", (0, 0), (-1, 0), ROJO),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (3, 0), (4, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS]),
            ("GRID", (0, 0), (-1, -1), 0.4, GRIS_OSC),
        ]))
        story.append(tbl_items)
        story.append(Spacer(1, 14))

        # Resumen financiero
        resumen_rows = [
            ["Subtotal:", f"${subtotal:,.2f}"],
            [f"Impuesto por conchudez ({int(self.IMPUESTO_CONCHUDEZ*100)}%):", f"${impuesto:,.2f}"],
            ["TOTAL A PAGAR:", f"${total:,.2f}"],
        ]
        tbl_res = Table(resumen_rows, colWidths=[13*cm, 4*cm])
        tbl_res.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
            ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 1), 10),
            ("FONTSIZE", (0, 2), (-1, 2), 13),
            ("TEXTCOLOR", (0, 2), (-1, 2), ROJO),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEABOVE", (0, 2), (-1, 2), 1.5, ROJO),
            ("ROWBACKGROUNDS", (0, 0), (-1, 1), [colors.white, GRIS]),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#FFEBEE")),
        ]))
        story.append(tbl_res)
        story.append(Spacer(1, 20))

        # Nota al pie
        nota = Paragraph(
            "<i>¡Gracias por comprar lo que debías devolver!</i>",
            ParagraphStyle("nota", parent=styles["Normal"],
                           fontSize=9, textColor=colors.HexColor("#888888"),
                           alignment=TA_CENTER)
        )
        story.append(nota)
        story.append(Spacer(1, 16))

        # Firma
        firma_rows = [
            ["", "_____________________________", ""],
            ["", "Michael Jackson Gamboa", ""],
            ["", "Prestador — BORROWNMIND", ""],
        ]
        tbl_f = Table(firma_rows, colWidths=[5*cm, 7*cm, 5*cm])
        tbl_f.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(tbl_f)

        doc.build(story)
        return ruta_pdf

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
