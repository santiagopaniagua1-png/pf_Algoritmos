# BROWMIND — Sistema de Gestión de Préstamos
**pf_Algoritmos**

Sistema de consola para gestionar préstamos de artículos, desarrollado en Python orientado a objetos.

---

## Requisitos

- Python 3.10 o superior (se usan *type hints* con `|`)
- No requiere librerías externas (solo módulos de la biblioteca estándar)

---

## Estructura del proyecto

```
BROWMIND/
│
├── main.py              # Punto de entrada y menús de consola
├── clsUsuarios.py       # Clase clsUsuarios — gestión de usuarios
├── clsItem.py           # Clase clsItem — gestión de ítems/inventario
├── clsPrestamo.py       # Clase clsPrestamo — gestión de préstamos
│
├── datos/               # Archivos de persistencia (JSON y CSV)
│   ├── usuarios.json
│   ├── items.json
│   ├── prestamos.json
│   ├── usuarios.csv
│   ├── items.csv
│   └── prestamos.csv
│
├── certificados/        # Certificados de devolución (.txt)
└── facturas/            # Facturas de venta (.txt)
```

---

## Ejecución

```bash
python main.py
```

---

## Credenciales de administrador (por defecto)

| Usuario | Contraseña |
|---------|------------|
| admin   | admin123   |
| Santy   | Santy2024  |

---

## Funcionalidades

### 1. Registrar Usuario
- Validaciones de nombre, apellido, documento, correo y días de préstamo.
- Días permitidos: 5, 10, 15 o 30.

### 2. Registrar Préstamo
- Solo para usuarios registrados.
- Listado de ítems disponibles con ID, nombre, categoría, precio y estado.
- Generación automática de fecha límite según días acordados.

### 3. Registrar Devolución
- Solo para préstamos activos.
- Genera certificado de devolución en `certificados/`.

### 4. Ítems con más de 30 días (Venta)
- Lista los ítems prestados por más de 30 días.
- Genera factura de venta con impuesto por conchudez del **23%**.
- Calcula subtotal y total.
- Archivos en `facturas/`.

### 5. Consultar Artículos Prestados
- Lista préstamos activos ordenados por días (mayor a menor).
- Muestra estadísticas: total, promedio, máximo y mínimo.
- Exporta a CSV.

### 6. Administrador
- Acceso protegido con usuario y contraseña.
- Reportes: préstamos totales, devueltos, vendidos, total pagado.
- Lista de usuarios y estadísticas de uso.
- Registro de nuevos ítems.
- Exportación completa a CSV.

---

## Lógica difusa — Estado del ítem

El estado del ítem se evalúa con un valor numérico de 0 a 100, usando conjuntos difusos:

| Rango       | Etiqueta    |
|-------------|-------------|
| 0 – 20      | Muy malo    |
| 21 – 40     | Malo        |
| 41 – 60     | Regular     |
| 61 – 80     | Bueno       |
| 81 – 100    | Excelente   |

Se reporta la etiqueta dominante y el grado de pertenencia.

---

## Categorías de ítems e ID

| Categoría         | Prefijo |
|-------------------|---------|
| Videojuegos       | VJ      |
| Libros            | LB      |
| Música y video    | MV      |
| Herramientas      | HT      |
| Dinero            | DN      |
| Misceláneo        | MV2     |

Ejemplo de ID: `VJ-3A1F92`

---

## Reglas de negocio

- Notificación de recuperación: préstamos con **más de 20 días**.
- Factura de venta: préstamos con **más de 30 días**.
- Impuesto por conchudez: **23%** sobre el precio de compra original.
- Los certificados se guardan como:
  `NombreUsuario_FechaDevolucion_IDPrestamo.txt`
- Las facturas se guardan como:
  `NombreUsuario_IDPrestamo.txt`

---

*Desarrollado con py — Santiago Panigua Cano - Olga Lucia Andica Narvaez - Estefania Rivera Castaño*
