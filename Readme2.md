# Guía de Preparación para la Interrogación Oral — EVA 2
> **Asignatura:** Programación Backend (Django + SQLite)  
> **Objetivo:** Responder con seguridad, claridad técnica y fluidez ante las preguntas del docente sobre el código del proyecto.

---

## Índice Temático
1. [Autenticación y Registro (`accounts`)](#1-autenticación-y-registro-accounts)
2. [Base de Datos, Modelos y Migraciones (`productos/models.py`)](#2-base-de-datos-modelos-y-migraciones)
3. [El CRUD de Productos (`productos/views.py`)](#3-el-crud-de-productos-productosviewspy)
4. [Seguridad y Enlace entre Apps (`@login_required` y Templates)](#4-seguridad-y-enlace-entre-apps)
5. [Configuración del Proyecto (`settings.py` y `urls.py`)](#5-configuración-del-proyecto)
6. [Resumen Rápido: Diferencias entre EVA 1 y EVA 2](#6-resumen-rápido-diferencias-entre-eva-1-y-eva-2)

---

## 1. Autenticación y Registro (`accounts`)

### Pregunta 1: ¿Cuál es la función que realiza la validación del registro y cómo funciona paso a paso?
* **Archivo:** `accounts/views.py`
* **Función:** `register_view(request)`

**Respuesta para explicar:**
> *"La función es `register_view`. Funciona de la siguiente manera:*
> 1. *Si la petición es **GET**, simplemente devuelve el formulario vacío de registro.*
> 2. *Si la petición es **POST**, extrae los valores enviados por el usuario: `username`, `email`, `password` y `confirm_password`.*
> 3. *Realiza 4 validaciones fundamentales acumulando posibles errores en una lista:*
>    - *Revisa que ningún campo venga vacío.*
>    - *Consulta a la base de datos con el ORM (`User.objects.filter(username=username).exists()` y `User.objects.filter(email=email).exists()`) para verificar que el usuario y el correo no existan previamente.*
>    - *Valida las reglas de seguridad de la contraseña: mínimo 8 caracteres (`len >= 8`), al menos una mayúscula (`any(c.isupper())`) y al menos un número (`any(c.isdigit())`).*
>    - *Comprueba que `password` y `confirm_password` sean exactamente iguales.*
> 4. *Si la lista de errores contiene algo, vuelve a renderizar `register.html` mostrando las alertas y conservando lo que el usuario ya había escrito.*
> 5. *Si todo es correcto, ejecuta `User.objects.create_user(username, email, password)`. Este método guarda el usuario en la tabla `auth_user` y se encarga de hashear (encriptar) la clave automáticamente. Finalmente, redirige al login con `?registrado=1`."*

---

### Pregunta 2: ¿Dónde y cómo se realiza el login y el bloqueo tras 3 intentos fallidos?
* **Archivo:** `accounts/views.py` y `accounts/store.py`
* **Función:** `login_view(request)`

**Respuesta para explicar:**
> *"En `login_view`, cuando se recibe un POST con las credenciales:*
> 1. *Primero revisamos el diccionario en memoria `LOGIN_ATTEMPTS` en `store.py`. Si ese usuario ya tiene la marca `bloqueado = True`, rechazamos la petición inmediatamente sin importar si la clave es correcta.*
> 2. *Si no está bloqueado, llamamos a la función nativa de Django `authenticate(request, username=username, password=password)`.*
> 3. *Si devuelve un objeto `user` válido: reiniciamos su contador de intentos a 0, creamos la sesión con `login(request, user)` y lo redirigimos al menú principal del CRUD (`/`).*
> 4. *Si devuelve `None` (credenciales incorrectas): incrementamos su contador en `LOGIN_ATTEMPTS`. Si llega a 3 intentos, marcamos `bloqueado = True` y mostramos el mensaje de bloqueo. Si lleva 1 o 2 intentos, le avisamos cuántos intentos le quedan."*

---

### Pregunta 3: ¿Por qué las contraseñas no se guardan en texto plano en la base de datos?
**Respuesta para explicar:**
> *"Porque usamos `User.objects.create_user()` de Django, el cual aplica un algoritmo criptográfico de un solo sentido (hash PBKDF2 con SHA-256) y un valor aleatorio llamado 'salt'. En la base de datos solo se guarda la cadena resultante del hash. Cuando el usuario inicia sesión, `authenticate()` hashea la clave ingresada y compara ambos hashes; nunca compara contraseñas en texto plano."*

---

### Pregunta 4: ¿Qué hace la función de logout?
* **Archivo:** `accounts/views.py`
* **Función:** `logout_view(request)`

**Respuesta para explicar:**
> *"Llama a `logout(request)` de Django. Esta función limpia los datos del usuario en la petición, elimina el registro correspondiente en la tabla `django_session` de la base de datos SQLite y borra la cookie del navegador, redirigiendo luego a `/login/`."*

---

## 2. Base de Datos, Modelos y Migraciones

### Pregunta 5: ¿Dónde está definido el modelo de datos del CRUD y qué representa cada línea?
* **Archivo:** `productos/models.py`
* **Clase:** `Producto(models.Model)`

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    precio = models.IntegerField()

    def __str__(self):
        return f"{self.nombre} ({self.marca})"
```

**Respuesta para explicar:**
> *"Hereda de `models.Model`, lo que le indica a Django que esta clase debe mapearse como una tabla en la base de datos:*
> - *`nombre`: campo de texto limitado a 100 caracteres (`CharField`).*
> - *`marca`: campo de texto para almacenar la cadena de supermercado (`CharField`).*
> - *`precio`: número entero (`IntegerField`) para guardar el valor en pesos chilenos.*
> - *El método `__str__`: define cómo se representa el objeto como texto legible cuando se imprime o se visualiza en consola."*

---

### Pregunta 6: ¿Por qué no creamos el campo `id` en el modelo `Producto`?
**Respuesta para explicar:**
> *"Porque Django, por convención y de forma predeterminada, agrega automáticamente un campo `id` como clave primaria autoincremental (`INTEGER PRIMARY KEY AUTOINCREMENT` en SQLite) si el desarrollador no define una clave primaria explícita."*

---

### Pregunta 7: ¿Qué diferencia hay entre `makemigrations` y `migrate`?
**Respuesta para explicar:**
> - *`python manage.py makemigrations`: Es un comando que analiza los modelos en `models.py` y genera archivos en Python (como `0001_initial.py` en la carpeta `migrations/`) que contienen el 'plano' o la descripción de los cambios a realizar.*
> - *`python manage.py migrate`: Es el comando que realmente se conecta a SQLite (`db.sqlite3`), lee esos archivos de migración y ejecuta las sentencias SQL necesarias (`CREATE TABLE`, `ALTER TABLE`, etc.) para crear físicamente las tablas en la base de datos.*

---

### Pregunta 8: ¿Qué es el ORM de Django?
**Respuesta para explicar:**
> *"ORM significa Object-Relational Mapping (Mapeo Objeto-Relacional). Es una herramienta de Django que nos permite manipular los datos de SQLite mediante código y objetos de Python (`Producto.objects.all()`, `.create()`, `.filter()`, `.delete()`), sin necesidad de escribir consultas SQL tradicionales (`SELECT * FROM...`, `INSERT INTO...`)."*

---

## 3. El CRUD de Productos (`productos/views.py`)

### Pregunta 9: ¿Cuáles son las 7 funciones del CRUD y qué hace cada una?

| Función | Método HTTP | URL | Qué hace en la base de datos / interfaz |
|---|:---:|---|---|
| `mostrarIndex` | GET | `/` | Muestra el menú principal con botones hacia registrar y catálogo. |
| `mostrarFormRegistrar` | GET | `/form_registrar/` | Renderiza el formulario de alta vacío con la lista de marcas. |
| `insertarProducto` | POST | `/insertar/` | Valida campos y ejecuta `Producto.objects.create(...)` en SQLite. |
| `mostrarListado` | GET | `/listado/` | Consulta `Producto.objects.all()` y muestra la tabla de productos. |
| `mostrarFormActualizar` | GET | `/form_actualizar/<id>/` | Busca el producto por su `id` y carga sus datos en los inputs. |
| `actualizarProducto` | POST | `/actualizar/<id>/` | Modifica los campos del objeto y persiste cambios con `.save()`. |
| `eliminarProducto` | GET | `/eliminar/<id>/` | Busca el producto por su `id` y lo borra con `.delete()`. |

---

### Pregunta 10: Explica en detalle la función `insertarProducto`. ¿Qué validaciones hace?
* **Archivo:** `productos/views.py`

**Respuesta para explicar:**
> *"Recibe por POST los datos enviados desde `form_registrar.html` con los nombres exigidos en la guía: `txtnom`, `cbomar` y `txtpre`:*
> 1. *Verifica que ninguno de los tres campos venga vacío.*
> 2. *Convierte el precio a entero dentro de un bloque `try/except ValueError` para validar que sea numérico y comprueba que esté en un rango lógico (entre 1 y 9.999.999).*
> 3. *Si falla la validación, devuelve la plantilla con el mensaje de error `msjErr` y los valores previos para que el usuario no tenga que reescribir todo.*
> 4. *Si los datos son válidos, llama al ORM: `Producto.objects.create(nombre=nombre, marca=marca, precio=precio)`. Esto inserta la fila en la tabla `productos_producto` y retorna `msjOk` en un alert verde de Bootstrap."*

---

### Pregunta 11: ¿Cómo funciona la actualización de un producto? (Diferencia entre GET y POST)
**Respuesta para explicar:**
> *"Se divide en dos vistas:*
> 1. *`mostrarFormActualizar(request, id)` (GET): Recibe el ID desde la URL, busca el producto con `Producto.objects.get(id=id)` y lo envía a `form_actualizar.html`. En el HTML los campos se rellenan automáticamente con `value="{{ producto.nombre }}"` y en el `<select>` se marca con `selected` la marca guardada.*
> 2. *`actualizarProducto(request, id)` (POST): Recibe los datos modificados del formulario, valida que sean correctos, asigna los nuevos valores a las propiedades del objeto (`producto.nombre = ...`, etc.) y ejecuta `producto.save()`. Luego redirige a `/listado/`."*

---

### Pregunta 12: ¿Cómo funciona la eliminación y cómo evitamos que se borren productos por error?
* **Archivos:** `templates/productos/listado.html` y `productos/views.py`

**Respuesta para explicar:**
> *"En la plantilla `listado.html`, cada fila tiene un botón con ícono de papelera que llama a la función JavaScript `botonEliminar({{ p.id }})`. Esta función ejecuta un `confirm('¿Eliminar este producto?')`. Si el usuario pulsa cancelar, no ocurre nada; si acepta, el navegador redirige a `/eliminar/<id>/`. En `productos/views.py`, la función `eliminarProducto` busca el registro por ID y ejecuta `producto.delete()`, devolviendo al usuario al listado actualizado."*

---

### Pregunta 13: ¿Por qué en buscar/actualizar/eliminar usamos `try / except Producto.DoesNotExist`?
**Respuesta para explicar:**
> *"Porque si un usuario intenta acceder a una URL con un ID que ya no existe (por ejemplo `/form_actualizar/999/`), el método `Producto.objects.get(id=id)` lanzaría una excepción no controlada que provocaría una pantalla de error 500 en el servidor. Al capturar `Producto.DoesNotExist`, podemos redirigir amigablemente al usuario hacia `/listado/` sin que la aplicación se caiga."*

---

## 4. Seguridad y Enlace entre Apps

### Pregunta 14: ¿Cómo se asegura que nadie pueda entrar al CRUD sin haber iniciado sesión?
* **Archivo:** `productos/views.py` y `config/settings.py`

**Respuesta para explicar:**
> *"Usamos el decorador oficial de Django `@login_required(login_url='/login/')` sobre cada una de las 7 vistas de la app `productos`. Si una persona intenta entrar directamente por la URL a `/`, `/listado/` o `/form_registrar/` sin autenticarse, Django intercepta la petición antes de ejecutar la vista y redirige al usuario a la pantalla de login."*

---

### Pregunta 15: ¿Cómo sabe la plantilla `base.html` qué usuario está conectado y si tiene sesión activa?
* **Archivo:** `templates/base.html`

**Respuesta para explicar:**
> *"Gracias a que en `settings.py` está configurado el context processor `'django.contrib.auth.context_processors.auth'`. Este componente inyecta automáticamente la variable `user` en todas las plantillas. En `base.html` usamos condicionales de Django:*
> - *`{% if user.is_authenticated %}`: Muestra el saludo 'Hola, {{ user.username }}', las opciones del menú CRUD y el botón 'Cerrar sesión' hacia `/logout/`.*
> - *`{% else %}`: Muestra solo los enlaces a 'Iniciar sesión' y 'Registrarse'."*

---

### Pregunta 16: ¿Para qué sirve `{% csrf_token %}` en los formularios?
**Respuesta para explicar:**
> *"Es una medida de seguridad obligatoria en Django contra ataques de tipo CSRF (Cross-Site Request Forgery o Falsificación de Petición en Sitios Cruzados). Genera un token único y secreto que viaja en el formulario; cuando el servidor recibe el POST, valida que la petición provenga legítimamente de nuestra propia aplicación y no de un sitio web malicioso externo."*

---

## 5. Configuración del Proyecto

### Pregunta 17: ¿Qué cambios importantes se hicieron en `settings.py` para la EVA 2?
* **Archivo:** `config/settings.py`

**Respuesta para explicar:**
> 1. *`DATABASES`: Se configuró el motor SQLite (`django.db.backends.sqlite3`) apuntando al archivo `BASE_DIR / 'db.sqlite3'`.*
> 2. *`INSTALLED_APPS`: Se mantuvieron las aplicaciones base de Django (`auth`, `contenttypes`, `sessions`, `messages`) y se agregaron las dos apps del proyecto: `'accounts'` y `'productos'`.*
> 3. *`MIDDLEWARE`: Se aseguró la presencia de `AuthenticationMiddleware` (necesario para `request.user` y `@login_required`).*
> 4. *`SESSION_ENGINE`: Se eliminó el motor de cookies firmadas de la EVA 1 para que las sesiones se almacenen de forma persistente en la tabla `django_session` de SQLite.*
> 5. *`LOGIN_URL`: Se definió `LOGIN_URL = '/login/'` para que el decorador `@login_required` sepa a dónde enviar a los usuarios no autenticados.*

---

### Pregunta 18: ¿Cómo están organizadas las URLs en el proyecto?
* **Archivo:** `config/urls.py`

**Respuesta para explicar:**
> *"Seguimos el principio de modularidad usando `include()`. En `config/urls.py` solo incluimos los archivos de rutas de cada app:*
> - *`path('', include('accounts.urls'))`: Gestiona `/registro/`, `/login/` y `/logout/`.*
> - *`path('', include('productos.urls'))`: Gestiona la raíz `/` (menú principal) y las rutas del CRUD.*
> *De esta forma cada app es autónoma y el archivo principal del proyecto se mantiene limpio y ordenado."*

---

## 6. Resumen Rápido: Diferencias entre EVA 1 y EVA 2

Si el profesor te pide resumir la evolución del proyecto en 30 segundos:

| Concepto | EVA 1 | EVA 2 |
|---|---|---|
| **Persistencia** | En memoria RAM (lista `USERS` en `store.py`). Se borraba al reiniciar el servidor. | Base de datos SQLite real (`db.sqlite3`). Los datos persisten siempre. |
| **Contraseñas** | En texto plano en una lista Python. | Encriptadas con algoritmo hash (PBKDF2/SHA256) en la tabla `auth_user`. |
| **Sesiones** | Cookies firmadas en el cliente (`signed_cookies`). | Sesión en base de datos (`django_session`). |
| **Punto de Entrada** | Redirigía a `/bienvenida/`. | Redirige al Menú del CRUD en `/`. |
| **Funcionalidad nueva** | Solo Login y Registro. | App `productos` con CRUD completo (Crear, Listar, Editar, Borrar). |
| **Seguridad de rutas** | Verificación manual de variables en sesión. | Decorador `@login_required` oficial de Django. |
