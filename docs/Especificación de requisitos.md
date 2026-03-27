
# Requisitos funcionales

## El sistema debe cumplir con las siguientes funciones:

- Registrar usuarios con nombre, apellido, documento, correo y tiempo de préstamo.
- Validar correctamente los datos ingresados (longitud, formato, números, etc.).
- Registrar ítems con nombre, categoría, precio, ID único y estado.
- Permitir realizar préstamos únicamente a usuarios registrados.
- Registrar devoluciones y generar certificados de devolución.
- Generar facturas de venta cuando el préstamo supere los 30 días.
- Calcular valores de venta incluyendo impuestos.
- Consultar el estado general de los préstamos.
- Permitir acceso a un módulo de administrador con usuario y contraseña.
- Generar reportes como:
  - Total de préstamos
  - Total de devoluciones
  - Total de ventas
  - Total de pagos
  - Lista de usuarios
  - Usuario con más y menos préstamos
 
 ---  -----------
 ## 6.2 Requisitos no funcionales
El sistema debe cumplir con las siguientes características de calidad:
-	Rendimiento:
El sistema debe responder rápidamente a las acciones del usuario sin demoras significativas. 
-	Usabilidad:
Debe contar con un menú claro, sencillo e intuitivo para facilitar su uso. 
-	Seguridad:
El acceso al módulo de administrador debe estar protegido mediante usuario y contraseña. 
-	Fiabilidad:
El sistema debe garantizar el correcto almacenamiento y recuperación de la información. 
-	Compatibilidad:
Debe ejecutarse correctamente en cualquier entorno que soporte Python. 
-	Mantenibilidad:
El código debe estar organizado en clases (como clsPrestamo y clsUsuarios) para facilitar futuras mejoras.


