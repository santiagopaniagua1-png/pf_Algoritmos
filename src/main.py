"""
A
Módulo: main
Descripción: Punto de entrada principal del sistema de préstamos BORROWMIND
Sistema de gestión de préstamos
"""

import os
import sys
import getpass
from clsUsuarios import clsUsuarios
from clsItem import clsItem
from clsPrestamo import clsPrestamo

# ──────────────────────────────────────────────
# Configuración de administradores
# ──────────────────────────────────────────────
ADMINS = {
    "admin": "admin123",
    "santy": "Santy2024",
}

# ──────────────────────────────────────────────
# Utilidades de consola
# ──────────────────────────────────────────────

ANCHO = 68


def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def linea(caracter="-"):
    print(caracter * ANCHO)


def titulo(texto):
    linea()
    print(f"  {texto}")
    linea()


def cabecera():
    limpiar()
    linea("=")
    banner = r"""
██████╗  ██████╗ ██████╗ ██████╗  ██████╗ ██╗    ██╗███╗   ███╗██╗███╗   ██╗██████╗
██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔═══██╗██║    ██║████╗ ████║██║████╗  ██║██╔══██╗
██████╔╝██║   ██║██████╔╝██████╔╝██║   ██║██║ █╗ ██║██╔████╔██║██║██╔██╗ ██║██║  ██║
██╔══██╗██║   ██║██╔══██╗██╔══██╗██║   ██║██║███╗██║██║╚██╔╝██║██║██║╚██╗██║██║  ██║
██████╔╝╚██████╔╝██║  ██║██║  ██║╚██████╔╝╚███╔███╔╝██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
    """
    print(banner)
    print("  Sistema de Gestión de Préstamos — Borrowmind")
    linea("=")


def pausa():
    input("\n  Presione ENTER para continuar...")


def pedir(prompt, obligatorio=True):
    while True:
        valor = input(f"  {prompt}: ").strip()
        if valor or not obligatorio:
            return valor
        print("  ⚠  Este campo es obligatorio.")


def confirmar(pregunta):
    resp = input(f"  {pregunta} (s/n): ").strip().lower()
    return resp == "s"


def imprimir_tabla(filas: list, encabezados: list, anchos: list):
    """Imprime una tabla formateada en consola."""
    fmt = "  " + "  ".join(f"{{:<{a}}}" for a in anchos)
    sep = "  " + "  ".join("-" * a for a in anchos)
    print(fmt.format(*encabezados))
    print(sep)
    for fila in filas:
        print(fmt.format(*[str(v)[:a] for v, a in zip(fila, anchos)]))


# ──────────────────────────────────────────────
# Instancias globales
# ──────────────────────────────────────────────
usuarios_mgr = clsUsuarios()
items_mgr = clsItem()
prestamos_mgr = clsPrestamo()


# ══════════════════════════════════════════════
# MÓDULO 1 — REGISTRAR USUARIO
# ══════════════════════════════════════════════

def menu_registrar_usuario():
    cabecera()
    titulo("1. REGISTRAR USUARIO")

    # Nombre
    while True:
        nombre = pedir("Nombre")
        ok, msg = clsUsuarios.validar_nombre(nombre)
        if ok:
            break
        print(f"  ✗ {msg}")

    # Apellido
    while True:
        apellido = pedir("Apellido")
        ok, msg = clsUsuarios.validar_nombre(apellido)
        if ok:
            break
        print(f"  ✗ {msg}")

    # Documento
    while True:
        documento = pedir("Documento (solo números, 3-15 dígitos)")
        if usuarios_mgr.documento_existe(documento):
            print("  ✗ Ya existe un usuario con ese documento.")
            continue
        ok, msg = clsUsuarios.validar_documento(documento)
        if ok:
            break
        print(f"  ✗ {msg}")

    # Correo
    while True:
        correo = pedir("Correo electrónico")
        ok, msg = clsUsuarios.validar_correo(correo)
        if ok:
            break
        print(f"  ✗ {msg}")

    # Días de préstamo
    print("\n  Opciones de días de préstamo: 5, 10, 15, 30")
    while True:
        dias = pedir("Días de préstamo")
        ok, msg = clsUsuarios.validar_dias_prestamo(dias)
        if ok:
            break
        print(f"  ✗ {msg}")

    usuario = usuarios_mgr.registrar_usuario(nombre, apellido, documento, correo, int(dias))
    linea()
    print(f"\n  ✔ Usuario registrado exitosamente.")
    print(f"    Nombre    : {usuario['nombre']} {usuario['apellido']}")
    print(f"    Documento : {usuario['documento']}")
    print(f"    Correo    : {usuario['correo']}")
    print(f"    Días p.   : {usuario['dias_prestamo']}")
    pausa()


# ══════════════════════════════════════════════
# MÓDULO 1B — REGISTRAR ÍTEM
# ══════════════════════════════════════════════

def menu_registrar_item():
    cabecera()
    titulo("REGISTRAR ÍTEM")

    # Nombre
    while True:
        nombre = pedir("Nombre del ítem (min. 3 caracteres)")
        if len(nombre) >= 3:
            break
        print("  ✗ El nombre debe tener al menos 3 caracteres.")

    # Categoría
    print("\n  Categorías disponibles:")
    for k, (nombre_cat, _) in items_mgr.CATEGORIAS.items():
        print(f"    {k}. {nombre_cat}")
    while True:
        cat = pedir("Seleccione categoría (1-6)")
        if cat in items_mgr.CATEGORIAS:
            break
        print("  ✗ Categoría inválida.")

    # Precio
    while True:
        precio_str = pedir("Precio de compra (ej: 150000.00)")
        try:
            precio = float(precio_str.replace(",", "."))
            if precio <= 0:
                raise ValueError
            break
        except ValueError:
            print("  ✗ Ingrese un precio válido mayor a 0.")

    # Estado difuso
    print("\n  Estado del ítem (valor entre 0 y 100):")
    print("    0-20  → Muy malo  |  21-40 → Malo  |  41-60 → Regular")
    print("    61-80 → Bueno     |  81-100 → Excelente")
    while True:
        estado_str = pedir("Valor de estado (0-100)")
        try:
            estado = float(estado_str)
            if 0 <= estado <= 100:
                break
            raise ValueError
        except ValueError:
            print("  ✗ Ingrese un valor entre 0 y 100.")

    item = items_mgr.registrar_item(nombre, cat, precio, estado)
    linea()
    print(f"\n  ✔ Ítem registrado exitosamente.")
    print(f"    ID        : {item['id']}")
    print(f"    Nombre    : {item['nombre']}")
    print(f"    Categoría : {item['categoria']}")
    print(f"    Precio    : ${item['precio_compra']:,.2f}")
    print(f"    Estado    : {item['estado_difuso']} (grado: {item['grado_pertenencia']})")
    pausa()


# ══════════════════════════════════════════════
# MÓDULO 2 — REGISTRAR PRÉSTAMO
# ══════════════════════════════════════════════

def menu_registrar_prestamo():
    cabecera()
    titulo("2. REGISTRAR PRÉSTAMO")

    # Buscar usuario
    documento = pedir("Documento del prestatario")
    usuario = usuarios_mgr.buscar_por_documento(documento)
    if not usuario:
        print(f"\n  ✗ No existe un usuario con documento '{documento}'.")
        print("    Por favor registre al usuario primero (opción 1).")
        pausa()
        return

    print(f"\n  ✔ Usuario encontrado: {usuario['nombre']} {usuario['apellido']}")
    print(f"    Días de préstamo acordados: {usuario['dias_prestamo']}")

    # Listar ítems disponibles
    disponibles = items_mgr.listar_disponibles()
    if not disponibles:
        print("\n  ✗ No hay ítems disponibles en el inventario.")
        pausa()
        return

    linea()
    print("\n  ÍTEMS DISPONIBLES:\n")
    encabezados = ["ID", "Nombre", "Categoría", "Precio", "Estado"]
    anchos = [16, 28, 18, 14, 12]
    filas = [
        (i["id"], i["nombre"], i["categoria"],
         f"${i['precio_compra']:,.2f}", i["estado_difuso"])
        for i in disponibles
    ]
    imprimir_tabla(filas, encabezados, anchos)

    linea()
    item_id = pedir("\n  ID del ítem a prestar")
    item = items_mgr.buscar_por_id(item_id)
    if not item:
        print(f"  ✗ No existe un ítem con ID '{item_id}'.")
        pausa()
        return
    if not item.get("disponible", True):
        print(f"  ✗ El ítem '{item['nombre']}' no está disponible.")
        pausa()
        return

    if not confirmar(f"  Confirmar préstamo de '{item['nombre']}' a {usuario['nombre']}?"):
        print("  Préstamo cancelado.")
        pausa()
        return

    prestamo = prestamos_mgr.registrar_prestamo(usuario, item)
    items_mgr.marcar_prestado(item["id"])

    linea()
    print(f"\n  ✔ Préstamo registrado exitosamente.")
    print(f"    ID Préstamo : {prestamo['id_prestamo']}")
    print(f"    Usuario     : {prestamo['nombre_usuario']}")
    print(f"    Ítem        : {prestamo['nombre_item']} ({prestamo['id_item']})")
    print(f"    Fecha       : {prestamo['fecha_prestamo']}")
    print(f"    Fecha límite: {prestamo['fecha_limite']}")
    pausa()


# ══════════════════════════════════════════════
# MÓDULO 3 — REGISTRAR DEVOLUCIÓN
# ══════════════════════════════════════════════

def menu_registrar_devolucion():
    cabecera()
    titulo("3. REGISTRAR DEVOLUCIÓN")

    documento = pedir("Documento del prestatario")
    usuario = usuarios_mgr.buscar_por_documento(documento)
    if not usuario:
        print(f"\n  ✗ No existe un usuario con documento '{documento}'.")
        pausa()
        return

    activos = prestamos_mgr.prestamos_activos_usuario(documento)
    if not activos:
        print(f"\n  ✗ {usuario['nombre']} {usuario['apellido']} no tiene préstamos activos.")
        pausa()
        return

    print(f"\n  PRÉSTAMOS ACTIVOS de {usuario['nombre']} {usuario['apellido']}:\n")
    encabezados = ["ID Préstamo", "Ítem", "Fecha préstamo", "Días limit.", "Días transcurridos"]
    anchos = [16, 24, 22, 11, 18]
    filas = []
    for p in activos:
        dias = prestamos_mgr.dias_transcurridos(p)
        filas.append((p["id_prestamo"], p["nombre_item"],
                      p["fecha_prestamo"][:10], p["dias_prestamo"], dias))
    imprimir_tabla(filas, encabezados, anchos)

    linea()
    id_prestamo = pedir("\n  ID del préstamo a devolver")
    prestamo_sel = next((p for p in activos if p["id_prestamo"] == id_prestamo), None)
    if not prestamo_sel:
        print("  ✗ ID de préstamo inválido o no pertenece a este usuario.")
        pausa()
        return

    if not confirmar(f"  Confirmar devolución del ítem '{prestamo_sel['nombre_item']}'?"):
        print("  Devolución cancelada.")
        pausa()
        return

    prestamo_devuelto = prestamos_mgr.registrar_devolucion(id_prestamo)
    items_mgr.marcar_disponible(prestamo_sel["id_item"])

    archivo = prestamos_mgr.generar_certificado_devolucion(prestamo_devuelto)
    linea()
    print(f"\n  ✔ Devolución registrada.")
    print(f"    Certificado generado: {archivo}")
    pausa()


# ══════════════════════════════════════════════
# MÓDULO 4 — ÍTEMS CON MÁS DE 30 DÍAS (VENTA)
# ══════════════════════════════════════════════

def menu_items_mas_30_dias():
    cabecera()
    titulo("4. ÍTEMS CON MÁS DE 30 DÍAS (VENTA)")

    candidatos = prestamos_mgr.prestamos_para_vender()
    if not candidatos:
        print("\n  No hay ítems con más de 30 días de préstamo.")
        pausa()
        return

    print("\n  ÍTEMS CANDIDATOS A VENTA:\n")
    encabezados = ["ID Préstamo", "Usuario", "Ítem", "Precio", "Días"]
    anchos = [14, 24, 24, 14, 6]
    for p in candidatos:
        imprimir_tabla(
            [(p["id_prestamo"], p["nombre_usuario"], p["nombre_item"],
              f"${p['precio_compra']:,.2f}", p["dias_transcurridos"])],
            encabezados, anchos
        )

    linea()
    print("\n  Opciones:")
    print("    1. Generar factura para un usuario específico")
    print("    2. Generar factura para TODOS los que superan 30 días")
    print("    0. Volver")
    opcion = pedir("Seleccione")

    if opcion == "1":
        documento = pedir("Documento del usuario")
        prests_usuario = [p for p in candidatos if p["documento_usuario"] == documento]
        if not prests_usuario:
            print("  ✗ No se encontraron ítems vencidos para ese usuario.")
        else:
            archivo = prestamos_mgr.generar_factura_venta(prests_usuario)
            print(f"\n  ✔ Factura generada: {archivo}")

    elif opcion == "2":
        # Agrupar por usuario
        por_usuario: dict = {}
        for p in candidatos:
            doc = p["documento_usuario"]
            por_usuario.setdefault(doc, []).append(p)
        archivos = []
        for doc, prests in por_usuario.items():
            archivos.append(prestamos_mgr.generar_factura_venta(prests))
        print(f"\n  ✔ {len(archivos)} factura(s) generada(s).")
        for a in archivos:
            print(f"    → {a}")

    pausa()


# ══════════════════════════════════════════════
# MÓDULO 5 — CONSULTAR ARTÍCULOS PRESTADOS
# ══════════════════════════════════════════════

def menu_consultar_prestados():
    cabecera()
    titulo("5. CONSULTAR ARTÍCULOS PRESTADOS")

    activos = prestamos_mgr.listar_ordenados_por_dias()
    if not activos:
        print("\n  No hay préstamos activos actualmente.")
        pausa()
        return

    total_prestados = len(activos)
    dias_valores = [p["dias_transcurridos"] for p in activos]
    promedio = sum(dias_valores) / total_prestados
    maximo = max(dias_valores)
    minimo = min(dias_valores)

    print(f"\n  📊 ESTADÍSTICAS GENERALES")
    print(f"    Total artículos prestados  : {total_prestados}")
    print(f"    Promedio de días prestados : {promedio:.1f} días")
    print(f"    Máximo días prestado       : {maximo} días")
    print(f"    Mínimo días prestado       : {minimo} días")
    linea()

    print("\n  LISTADO (ordenado por días, mayor a menor):\n")
    encabezados = ["ID Préstamo", "Usuario", "Ítem", "Categoría", "Días", "Estado"]
    anchos = [14, 22, 20, 16, 6, 10]
    filas = []
    for p in activos:
        alerta = "⚠ VENTA" if p["dias_transcurridos"] > 30 else (
            "! Notif." if p["dias_transcurridos"] > 20 else "OK")
        filas.append((p["id_prestamo"], p["nombre_usuario"], p["nombre_item"],
                      p["categoria_item"], p["dias_transcurridos"], alerta))
    imprimir_tabla(filas, encabezados, anchos)

    linea()
    if confirmar("\n  ¿Exportar a CSV?"):
        ruta = prestamos_mgr.exportar_csv()
        print(f"  ✔ Exportado: {ruta}")

    pausa()


# ══════════════════════════════════════════════
# MÓDULO 6 — ADMINISTRADOR
# ══════════════════════════════════════════════

def menu_administrador():
    cabecera()
    titulo("6. ACCESO ADMINISTRADOR")

    usuario_adm = pedir("Usuario administrador")
    contrasena = getpass.getpass("  Contraseña: ")

    if ADMINS.get(usuario_adm) != contrasena:
        print("\n  ✗ Credenciales incorrectas. Acceso denegado.")
        pausa()
        return

    print(f"\n  ✔ Bienvenido, {usuario_adm}.")

    while True:
        cabecera()
        titulo("PANEL DE ADMINISTRACIÓN")
        print("  1. Total de préstamos registrados")
        print("  2. Total de ítems devueltos")
        print("  3. Total de ventas realizadas")
        print("  4. Total pagado (ventas)")
        print("  5. Lista de usuarios")
        print("  6. Usuario con más/menos préstamos")
        print("  7. Registrar nuevo ítem")
        print("  8. Exportar todo a CSV")
        print("  0. Volver al menú principal")
        linea()
        op = pedir("Seleccione")

        stats = prestamos_mgr.estadisticas()

        if op == "1":
            print(f"\n  Total préstamos registrados: {stats['total_prestamos']}")
        elif op == "2":
            print(f"\n  Total ítems devueltos: {stats['devueltos']}")
        elif op == "3":
            print(f"\n  Total ventas realizadas: {stats['vendidos']}")
        elif op == "4":
            print(f"\n  Total pagado en ventas: ${stats['total_ventas']:,.2f}")
        elif op == "5":
            us = usuarios_mgr.listar_usuarios()
            if not us:
                print("\n  No hay usuarios registrados.")
            else:
                print("\n  LISTA DE USUARIOS:\n")
                encabezados = ["Documento", "Nombre", "Apellido", "Correo", "Días p."]
                anchos = [15, 18, 18, 28, 7]
                filas = [(u["documento"], u["nombre"], u["apellido"], u["correo"], u["dias_prestamo"])
                         for u in us]
                imprimir_tabla(filas, encabezados, anchos)
        elif op == "6":
            if stats["usuario_max"]:
                print(f"\n  Mayor cantidad de préstamos: {stats['usuario_max']['nombre']} "
                      f"({stats['usuario_max']['cantidad']} préstamos)")
                print(f"  Menor cantidad de préstamos: {stats['usuario_min']['nombre']} "
                      f"({stats['usuario_min']['cantidad']} préstamos)")
            else:
                print("\n  No hay datos de préstamos aún.")
        elif op == "7":
            menu_registrar_item()
            continue
        elif op == "8":
            r1 = usuarios_mgr.exportar_csv()
            r2 = items_mgr.exportar_csv()
            r3 = prestamos_mgr.exportar_csv()
            print(f"\n  ✔ Exportado: {r1}")
            print(f"  ✔ Exportado: {r2}")
            print(f"  ✔ Exportado: {r3}")
        elif op == "0":
            break
        else:
            print("  Opción inválida.")

        pausa()


# ══════════════════════════════════════════════
# MENÚ PRINCIPAL
# ══════════════════════════════════════════════

def menu_principal():
    while True:
        cabecera()
        print("  Bienvenido a BORROWMIND — Sistema de Préstamos\n")
        print("    1. Registrar Usuario")
        print("    2. Registrar Préstamo")
        print("    3. Registrar Devolución")
        print("    4. Consultar Ítems con más de 30 días")
        print("    5. Consultar Artículos Prestados")
        print("    6. Administrador")
        print("    7. Salir")
        linea()
        opcion = pedir("Seleccione una opción")

        if opcion == "1":
            menu_registrar_usuario()
        elif opcion == "2":
            menu_registrar_prestamo()
        elif opcion == "3":
            menu_registrar_devolucion()
        elif opcion == "4":
            menu_items_mas_30_dias()
        elif opcion == "5":
            menu_consultar_prestados()
        elif opcion == "6":
            menu_administrador()
        elif opcion == "7":
            cabecera()
            print("\n  ¡Hasta luego! Gracias por usar BORROWMIND.\n")
            linea()
            sys.exit(0)
        else:
            print("  ✗ Opción inválida. Intente de nuevo.")
            pausa()


# ──────────────────────────────────────────────
# INICIO
# ──────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("datos", exist_ok=True)
    os.makedirs("certificados", exist_ok=True)
    os.makedirs("facturas", exist_ok=True)
    menu_principal()
