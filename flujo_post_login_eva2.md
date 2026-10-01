# Flujo de Trabajo Post-Login — EVA 2 (Django + SQLite)

Este documento detalla el recorrido que realiza un usuario una vez que inicia sesión correctamente en el sistema, explicando **qué funciones se ejecutan**, **en qué archivos se ubican** y **cómo interactúan las vistas con la base de datos y las plantillas**.

---

## Diagrama General del Flujo

```mermaid
flowchart TD
    Login["1. Login Exitoso<br><code>login_view</code><br>(accounts/views.py)"] -->|redirect '/'| Menu["2. Menú Principal<br><code>mostrarIndex</code><br>(productos/views.py)"]
    
    Menu -->|Clic 'Registrar'| FormReg["3. Formulario Alta<br><code>mostrarFormRegistrar</code><br>(productos/views.py)"]
    FormReg -->|POST '/insertar/'| InsProd["4. Guardar Producto<br><code>insertarProducto</code><br>(productos/views.py)"]
    InsProd -->|Producto.objects.create| BD[(SQLite: productos_producto)]
    InsProd -->|msjOk / msjErr| FormReg
    
    Menu -->|Clic 'Listado'| Listado["5. Ver Catálogo<br><code>mostrarListado</code><br>(productos/views.py)"]
    Listado -->|Producto.objects.all| BD
    
    Listado -->|Clic 'Editar'| FormAct["6. Formulario Edición<br><code>mostrarFormActualizar</code><br>(productos/views.py)"]
    FormAct -->|POST '/actualizar/id/'| ActProd["7. Guardar Cambios<br><code>actualizarProducto</code><br>(productos/views.py)"]
    ActProd -->|producto.save| BD
    ActProd -->|redirect '/listado/'| Listado
    
    Listado -->|Clic 'Eliminar' + confirm()| ElimProd["8. Borrar Registro<br><code>eliminarProducto</code><br>(productos/views.py)"]
    ElimProd -->|producto.delete| BD
    ElimProd -->|redirect '/listado/'| Listado

    Menu & Listado & FormReg & FormAct -.->|Clic 'Cerrar sesión'| Logout["9. Logout<br><code>logout_view</code><br>(accounts/views.py)"]
    Logout -->|logout() + redirect| LoginView["Pantalla Login<br>(/login/)"]
```

---

## 1. El Salto Inicial: Del Login al Menú del CRUD

1. **¿Dónde ocurre el login?**  
   * **Archivo:** `accounts/views.py`  
   * **Función:** `login_view(request)`
2. **¿Qué hace?**  
   Al validar las credenciales correctas con `authenticate()`, ejecuta `login(request, user)` para crear la sesión en SQLite y retorna:
   ```python
   return redirect('/')
   ```
3. **¿A dónde llega?**  
   Al llegar a la raíz `/`, Django consulta `config/urls.py`, que delega la ruta a `productos/urls.py`.

---

## 2. Menú Principal (Dashboard)

* **Ruta URL:** `/`
* **Archivo de vista:** `productos/views.py`
* **Función:** `mostrarIndex(request)`
* **Plantilla renderizada:** `templates/productos/index.html`
* **Seguridad:** `@login_required(login_url='/login/')`

**¿Qué hace la función?**
* Verifica que el usuario tenga una sesión válida activa. Si no la tiene, lo expulsa automáticamente a `/login/`.
* Si está autenticado, responde con la plantilla `index.html`, la cual muestra las dos tarjetas principales del sistema:
  1. Botón para ir al formulario de registro (`/form_registrar/`).
  2. Botón para ir a ver el listado de productos (`/listado/`).

---

## 3. Funcionalidad: Registrar un Nuevo Producto (CREATE)

Esta funcionalidad trabaja en dos etapas coordinadas:

### Paso 3.1: Desplegar el Formulario Vacío (GET)
* **Ruta URL:** `/form_registrar/`
* **Archivo de vista:** `productos/views.py`
* **Función:** `mostrarFormRegistrar(request)`
* **Plantilla renderizada:** `templates/productos/form_registrar.html`

**¿Qué hace la función?**
* Envía al template la lista `MARCAS_DISPONIBLES` (`Acuenta`, `Jumbo`, `Lider`, `Unimarc`, `Santa Isabel`) para que se dibujen como opciones en el elemento `<select name="cbomar">`.
* Renderiza el formulario vacío con los campos `txtnom`, `cbomar` y `txtpre`.

---

### Paso 3.2: Procesar e Insertar en Base de Datos (POST)
* **Ruta URL:** `/insertar/`
* **Archivo de vista:** `productos/views.py`
* **Función:** `insertarProducto(request)`
* **Plantilla renderizada:** `templates/productos/form_registrar.html`

**¿Qué hace la función?**
1. Lee los valores enviados por POST:
   * `nombre = request.POST.get('txtnom')`
   * `marca = request.POST.get('cbomar')`
   * `precio_str = request.POST.get('txtpre')`
2. **Valida los datos:** comprueba que no vengan vacíos y que el precio sea un número entero positivo (entre 1 y 9.999.999).
3. **Interacción con la BD:** Si todo es correcto, ejecuta el ORM de Django:
   ```python
   Producto.objects.create(nombre=nombre, marca=marca, precio=precio)
   ```
   Esto crea físicamente una nueva fila en la tabla `productos_producto` de SQLite.
4. Devuelve la plantilla con un mensaje de éxito `msjOk` en una alerta verde de Bootstrap (o `msjErr` si falló la validación).

---

## 4. Funcionalidad: Ver el Catálogo de Productos (READ)

* **Ruta URL:** `/listado/`
* **Archivo de vista:** `productos/views.py`
* **Función:** `mostrarListado(request)`
* **Plantilla renderizada:** `templates/productos/listado.html`

**¿Qué hace la función?**
1. **Consulta la BD:** Utiliza el ORM para traer todos los registros existentes:
   ```python
   productos = Producto.objects.all()
   ```
2. Envía la colección `productos` al template `listado.html`.
3. El template recorre los datos con un ciclo `{% for p in productos %}` y dibuja una tabla con:
   * Columnas: `ID`, `NOMBRE`, `MARCA`, `PRECIO`.
   * Enlace con ícono de lápiz para editar (`/form_actualizar/{{ p.id }}/`).
   * Botón con ícono de basurero que activa la confirmación de borrado.
   * Si la tabla está vacía, la etiqueta `{% empty %}` muestra un aviso amigable invitando a crear el primer producto.

---

## 5. Funcionalidad: Modificar un Producto (UPDATE)

Al igual que la creación, se divide en dos etapas:

### Paso 5.1: Cargar el Formulario con Datos Existentes (GET)
* **Ruta URL:** `/form_actualizar/<int:id>/`
* **Archivo de vista:** `productos/views.py`
* **Función:** `mostrarFormActualizar(request, id)`
* **Plantilla renderizada:** `templates/productos/form_actualizar.html`

**¿Qué hace la función?**
1. Recibe el `id` desde la URL y busca el registro específico en SQLite:
   ```python
   producto = Producto.objects.get(id=id)
   ```
   *(Si el ID no existe, el bloque `try/except Producto.DoesNotExist` redirige al listado sin que se caiga el servidor).*
2. Envía el objeto `producto` a `form_actualizar.html`.
3. En el formulario, los inputs aparecen precargados con `value="{{ producto.nombre }}"`, `value="{{ producto.precio }}"` y en el `<select>` la marca actual aparece con el atributo `selected`.

---

### Paso 5.2: Guardar los Cambios Realizados (POST)
* **Ruta URL:** `/actualizar/<int:id>/`
* **Archivo de vista:** `productos/views.py`
* **Función:** `actualizarProducto(request, id)`

**¿Qué hace la función?**
1. Recupera el objeto de la BD con `Producto.objects.get(id=id)`.
2. Lee los datos nuevos del formulario POST (`txtnom`, `cbomar`, `txtpre`) y los valida.
3. Asigna los nuevos valores a las propiedades del objeto:
   ```python
   producto.nombre = nombre
   producto.marca = marca
   producto.precio = precio
   producto.save()  # Ejecuta UPDATE en SQLite
   ```
4. Finaliza redirigiendo al listado (`/listado/`) para que el usuario aprecie los cambios de inmediato.

---

## 6. Funcionalidad: Eliminar un Producto (DELETE)

Esta acción cuenta con una capa de protección en frontend y otra en backend:

### Paso 6.1: Confirmación en Navegador (JavaScript)
* **Archivo:** `templates/productos/listado.html`
* **Script:** Función `botonEliminar(id)`
* **Qué hace:** Al hacer clic en el basurero, se dispara:
  ```javascript
  function botonEliminar(id) {
      if (confirm("¿Eliminar este producto?")) {
          window.location.href = "/eliminar/" + id + "/";
      }
  }
  ```
  Si el usuario hace clic en "Cancelar", no se realiza ninguna petición.

---

### Paso 6.2: Borrado en Base de Datos (GET)
* **Ruta URL:** `/eliminar/<int:id>/`
* **Archivo de vista:** `productos/views.py`
* **Función:** `eliminarProducto(request, id)`

**¿Qué hace la función?**
1. Recibe el `id` por la URL.
2. Localiza el producto en SQLite y ejecuta la eliminación:
   ```python
   producto = Producto.objects.get(id=id)
   producto.delete()  # Ejecuta DELETE en SQLite
   ```
3. Redirige automáticamente a `/listado/`, mostrando la tabla actualizada sin el registro eliminado.

---

## 7. Cierre de Sesión (LOGOUT)

* **Ruta URL:** `/logout/`
* **Archivo de vista:** `accounts/views.py`
* **Función:** `logout_view(request)`
* **Origen visual:** Botón "Cerrar sesión" en la barra de navegación ([templates/base.html](file:///c:/Users/durib/Desktop/programacion-backend/eva-2/templates/base.html)).

**¿Qué hace la función?**
1. Ejecuta la función oficial de Django `logout(request)`.
2. Elimina la sesión activa de la tabla `django_session` en SQLite y limpia las cookies del navegador.
3. Redirige al usuario a la pantalla de login (`/login/`). Si el usuario intenta regresar usando el botón "Atrás" del navegador hacia cualquier página del CRUD, el decorador `@login_required` le bloqueará el paso y lo forzará a autenticarse de nuevo.

---

## Mapa Resumen de Archivos y Responsabilidades

| Funcionalidad | Ruta URL | Archivo de la Vista | Función en Python | Plantilla Asociada |
|---|---|---|---|---|
| **Menú Principal** | `/` | `productos/views.py` | `mostrarIndex` | `templates/productos/index.html` |
| **Formulario Alta** | `/form_registrar/` | `productos/views.py` | `mostrarFormRegistrar` | `templates/productos/form_registrar.html` |
| **Insertar Producto** | `/insertar/` | `productos/views.py` | `insertarProducto` | `templates/productos/form_registrar.html` |
| **Listar Catálogo** | `/listado/` | `productos/views.py` | `mostrarListado` | `templates/productos/listado.html` |
| **Formulario Edición** | `/form_actualizar/<id>/` | `productos/views.py` | `mostrarFormActualizar` | `templates/productos/form_actualizar.html` |
| **Guardar Edición** | `/actualizar/<id>/` | `productos/views.py` | `actualizarProducto` | *(Redirige a `/listado/`)* |
| **Eliminar Producto** | `/eliminar/<id>/` | `productos/views.py` | `eliminarProducto` | *(Redirige a `/listado/`)* |
| **Cerrar Sesión** | `/logout/` | `accounts/views.py` | `logout_view` | *(Redirige a `/login/`)* |
