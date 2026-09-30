# Especificación SDD — EVA 2: Django + SQLite (Login con BD + CRUD de Productos)

> **Cómo usar este documento:** es la continuación de la EVA 1 (`especificacion_edd_login_django.md`). Se pasa completo a la herramienta/LLM que desarrolle el proyecto. Mantiene el formato *Dado / Cuando / Entonces* de la EVA 1.
>
> **Principio rector:** hacer lo mínimo que cumple la pauta, con código simple, comentado y fácil de explicar en la interrogación oral (30 % de la nota). **Si hay dos formas de hacer algo, se elige la más simple.**

---

## 0. Qué cambia respecto a la EVA 1

| Tema | EVA 1 | EVA 2 |
|---|---|---|
| Usuarios | Lista en memoria (`USERS` en `store.py`) | Tabla `auth_user` de Django (SQLite) |
| Contraseñas | Texto plano | Hasheadas automáticamente (`create_user`) |
| Sesión | `signed_cookies`, sin `migrate` | Sesión por defecto de Django (usa BD, requiere `migrate`) |
| Login | Comparar contra la lista | `authenticate()` + `login()` |
| Logout | Borrar `request.session` | `logout()` |
| Post-login | `/bienvenida/` | Menú del CRUD (`/`) |
| Nuevo | — | App `productos` con CRUD y rutas protegidas |
| Se mantiene | Validaciones de registro, bloqueo a los 3 intentos, CSS/JS, plantilla base | igual |

---

## 1. Alcance (lo que SÍ y lo que NO)

**SÍ:** 2 apps (`accounts`, `productos`), SQLite, `User` de Django, CRUD de Producto, rutas protegidas con `@login_required`, Bootstrap 5.3 por CDN en las plantillas del CRUD.

**NO (fuera de alcance, no agregar):** Django Forms / ModelForms, vistas basadas en clases, Django REST, API, AJAX, modelo de usuario personalizado, `admin` personalizado, paginación, búsqueda, permisos por rol, tests automatizados, Docker, variables de entorno, otro motor de BD.

---

## 2. Configuración del proyecto

- Reutilizar el proyecto de la EVA 1 (carpeta `config/`). Si se parte de cero: `django-admin startproject config .`
- Crear la app nueva: `python manage.py startapp productos`
- `settings.py`:
  - `INSTALLED_APPS`: agregar `'accounts'` y `'productos'` (además de las apps por defecto, que **no se quitan**: `auth`, `sessions`, etc. son necesarias).
  - `DATABASES`: dejar la configuración por defecto de SQLite (`django.db.backends.sqlite3`, `BASE_DIR / 'db.sqlite3'`).
  - `TEMPLATES > DIRS`: `[BASE_DIR / 'templates']`.
  - `STATIC_URL` y `STATICFILES_DIRS` como en la EVA 1.
  - **Eliminar** `SESSION_ENGINE = '...signed_cookies'` (usar el motor por defecto).
  - Agregar `LOGIN_URL = '/login/'`, para que `@login_required` redirija ahí.
  - Agregar `LOGIN_REDIRECT_URL = '/'` (opcional, por claridad).
- Comandos obligatorios, en este orden: `python manage.py makemigrations` → `python manage.py migrate`. Esto crea `auth_user`, `django_session` y `productos_producto`.
- Crear un superusuario **no** es requisito. Usuario de prueba: se registra desde `/registro/` o se crea con `python manage.py createsuperuser`.

---

## 3. Estructura de carpetas

```
proyecto/
├── manage.py
├── db.sqlite3                  # se genera con migrate
├── config/
│   ├── settings.py
│   ├── urls.py                 # include de accounts y productos
│   └── wsgi.py
├── accounts/
│   ├── store.py                # SOLO LOGIN_ATTEMPTS (se elimina USERS)
│   ├── views.py                # register_view, login_view, logout_view
│   └── urls.py
├── productos/
│   ├── models.py               # Producto
│   ├── views.py                # 7 vistas del CRUD
│   ├── urls.py
│   └── migrations/
├── templates/
│   ├── base.html               # navbar con usuario y "Cerrar sesión"
│   ├── accounts/
│   │   ├── register.html
│   │   └── login.html
│   └── productos/
│       ├── index.html
│       ├── form_registrar.html
│       ├── listado.html
│       └── form_actualizar.html
└── static/
    ├── css/styles.css
    └── js/validaciones.js
```

Se elimina `welcome.html` y `welcome_view` (el post-login pasa a ser el menú del CRUD).

---

## 4. Etapa 1 — App `accounts` con BD

### 4.1 Reglas generales
- Usar **`django.contrib.auth.models.User`**. No se crea ninguna tabla de usuarios propia.
- Importar: `from django.contrib.auth.models import User` y `from django.contrib.auth import authenticate, login, logout`.
- Las validaciones del registro siguen haciéndose **a mano en la vista** (igual que en la EVA 1). No usar `AUTH_PASSWORD_VALIDATORS` ni Django Forms.
- El campo de usuario del formulario se llama `username`; el de correo, `email`.

### 4.2 Registro (`register_view`)
- **Dado** GET en `/registro/` → **entonces** se muestra el formulario vacío.
- **Cuando** POST y `User.objects.filter(username=username).exists()` → error "El nombre de usuario ya está en uso." y no se guarda.
- **Cuando** `User.objects.filter(email=email).exists()` → error "El correo ya está registrado." y no se guarda.
- **Cuando** la contraseña tiene menos de 8 caracteres, no tiene mayúscula o no tiene número → error correspondiente (mismas reglas de la EVA 1).
- **Cuando** contraseña y confirmación no coinciden → error "Las contraseñas no coinciden."
- **Cuando** todo es válido → `User.objects.create_user(username=..., email=..., password=...)` y redirección a `/login/` con mensaje de éxito.

### 4.3 Login (`login_view`)
- **Dado** GET en `/login/` → se muestra el formulario.
- **Dado** el usuario está bloqueado en `LOGIN_ATTEMPTS` → mensaje "Clave bloqueada. Ha superado el máximo de intentos permitidos." y no se procesa el intento, aunque los datos sean correctos.
- **Cuando** `authenticate(request, username=..., password=...)` devuelve `None` → se incrementa el contador en `LOGIN_ATTEMPTS`.
  - Si llega a 3 → `bloqueado = True` y mensaje de bloqueo.
  - Si no → "Usuario o contraseña incorrectos. Intento X de 3."
- **Cuando** `authenticate` devuelve un usuario y no está bloqueado → se reinicia el contador, se llama `login(request, user)` y se redirige a `/`.
- **Dado** un usuario ya autenticado que entra a `/login/` → (opcional) redirigir a `/`.

> **Decisión de diseño:** el bloqueo por 3 intentos se mantiene tal como en la EVA 1 (diccionario en memoria `LOGIN_ATTEMPTS` en `store.py`), porque ya funciona y no exige cambiar nada. Se reinicia al reiniciar el servidor. Si el profesor no lo exige en la EVA 2 y se quiere simplificar, se puede eliminar sin afectar el resto.

### 4.4 Logout (`logout_view`)
- **Cuando** se accede a `/logout/` → `logout(request)` y redirección a `/login/`.

---

## 5. Etapa 2 — App `productos` (CRUD)

### 5.1 Modelo (`productos/models.py`)

```python
from django.db import models

class Producto(models.Model):
    # 'id' lo crea Django solo (clave primaria autoincremental)
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    precio = models.IntegerField()

    def __str__(self):
        return f"{self.nombre} ({self.marca})"
```

Se usa `CharField` (no `TextField`) porque `max_length` es propio de `CharField`.

### 5.2 Nombres de campos en los formularios (según Guías 2 y 3)

| Campo | `name` | Tipo HTML | Notas |
|---|---|---|---|
| Nombre | `txtnom` | `text` | `required`, `maxlength="100"` |
| Marca | `cbomar` | `select` | opciones: `A cuenta`, `Jumbo`, `Lider`, `Unimarc`, `Santa Isabel` |
| Precio | `txtpre` | `number` | `required`, `min="1"`, `max="9999999"` |

### 5.3 Vistas (`productos/views.py`)

**Todas** llevan `@login_required` (ver sección 6). Cada vista con un comentario breve de qué hace.

| Vista | Método | Comportamiento |
|---|---|---|
| `mostrarIndex(request)` | GET | Renderiza `index.html` (menú con enlaces a registrar y listado). |
| `mostrarFormRegistrar(request)` | GET | Renderiza `form_registrar.html` vacío. |
| `insertarProducto(request)` | POST | Lee `request.POST['txtnom']`, `['cbomar']`, `['txtpre']`. Si son válidos: `Producto.objects.create(...)` y `msjOk`. Si falla o vienen vacíos: `msjErr`. Vuelve a `form_registrar.html` con el mensaje. |
| `mostrarListado(request)` | GET | `productos = Producto.objects.all()` y renderiza `listado.html`. |
| `mostrarFormActualizar(request, id)` | GET | `Producto.objects.get(id=id)` y renderiza `form_actualizar.html` con los datos cargados. |
| `actualizarProducto(request, id)` | POST | Busca el producto, actualiza `nombre`, `marca`, `precio`, hace `.save()` y redirige a `/listado/`. |
| `eliminarProducto(request, id)` | GET | Busca el producto, hace `.delete()` y redirige a `/listado/`. |

**Escenarios esperados:**
- **Dado** que se envía un producto válido → **entonces** se guarda y se ve un `alert-success` con `{{ msjOk }}`.
- **Dado** que hay un error (campo vacío, precio no numérico) → **entonces** no se guarda y se ve un `alert-danger` con `{{ msjErr }}`.
- **Dado** que el listado está vacío → **entonces** se muestra la tabla solo con encabezados o un texto "No hay productos".
- **Cuando** se hace clic en el ícono de basurero → **entonces** aparece `confirm()` de JavaScript; si se acepta, se va a `/eliminar/<id>/`.
- **Cuando** el `id` no existe → **entonces** redirigir al listado (usar `try/except Producto.DoesNotExist`; no `get_object_or_404`, para mantenerlo explicable).

### 5.4 Plantillas (`templates/productos/`)

Todas heredan de `base.html` (`{% extends "base.html" %}`), que carga Bootstrap 5.3 por CDN (`bootstrap.min.css`, `bootstrap.bundle.min.js`, `bootstrap-icons.css`).

1. **`index.html`** — Menú con dos botones/enlaces: "Registrar producto" (`/form_registrar/`) y "Listado de productos" (`/listado/`).
2. **`form_registrar.html`** — `<form action="/insertar/" method="post">` con `{% csrf_token %}`, los 3 campos, botón guardar, alertas Bootstrap (`{% if msjOk %}` → `alert-success`, `{% if msjErr %}` → `alert-danger`), y enlaces "Volver al Menú" (`/`).
3. **`listado.html`** — Tabla Bootstrap con columnas `ID`, `NOMBRE`, `MARCA`, `PRECIO`, `EDITAR`, `ELIMINAR`, recorrida con `{% for p in productos %}`.
   - EDITAR: ícono lápiz (`bi-pencil`) con enlace a `/form_actualizar/{{ p.id }}/`.
   - ELIMINAR: ícono basurero (`bi-trash`) con `onclick="botonEliminar({{ p.id }})"`.
   - Script: `function botonEliminar(id){ if(confirm("¿Eliminar este producto?")){ window.location.href = "/eliminar/" + id + "/"; } }`
4. **`form_actualizar.html`** — `<form action="/actualizar/{{ producto.id }}/" method="post">` con `{% csrf_token %}`, campos precargados (`value="{{ producto.nombre }}"`, opción `selected` en la marca actual, `value="{{ producto.precio }}"`).

---

## 6. Etapa 3 — Enlace entre apps (seguridad de rutas)

- Todas las vistas de `productos` usan `@login_required(login_url='/login/')` (`from django.contrib.auth.decorators import login_required`).
- **Dado** un usuario no autenticado → **cuando** entra a `/`, `/listado/`, `/form_registrar/`, etc. → **entonces** es redirigido a `/login/`.
- **Dado** un usuario autenticado → **cuando** entra a `/` → **entonces** ve el menú del CRUD.
- El flujo completo: `/registro/` → `/login/` → `/` (menú) → CRUD → `/logout/` → `/login/`.
- `base.html` muestra, solo si `user.is_authenticated`: "Hola, {{ user.username }}" y un botón/enlace visible **"Cerrar sesión"** hacia `/logout/`. Si no está autenticado, muestra enlaces a Login y Registro.
- Django ya entrega `user` a las plantillas gracias al context processor de `auth`, por lo que no hay que pasarlo desde la vista.

---

## 7. Mapa de rutas

`config/urls.py` incluye ambas apps: `path('', include('accounts.urls'))` y `path('', include('productos.urls'))`. El orden no genera conflicto porque las rutas son distintas.

| App | Ruta | Vista | Protegida | Descripción |
|---|---|---|---|---|
| accounts | `/registro/` | `register_view` | No | Alta de usuario en BD |
| accounts | `/login/` | `login_view` | No | Inicio de sesión |
| accounts | `/logout/` | `logout_view` | No | Cierre de sesión |
| productos | `/` | `mostrarIndex` | **Sí** | Menú del CRUD |
| productos | `/form_registrar/` | `mostrarFormRegistrar` | **Sí** | Formulario de alta |
| productos | `/insertar/` | `insertarProducto` | **Sí** | Guarda producto (POST) |
| productos | `/listado/` | `mostrarListado` | **Sí** | Tabla de productos |
| productos | `/form_actualizar/<int:id>/` | `mostrarFormActualizar` | **Sí** | Formulario de edición |
| productos | `/actualizar/<int:id>/` | `actualizarProducto` | **Sí** | Guarda edición (POST) |
| productos | `/eliminar/<int:id>/` | `eliminarProducto` | **Sí** | Elimina y vuelve al listado |

---

## 8. Reglas de código (para la interrogación oral)

- Comentar **cada vista** con 1–2 líneas en español: qué recibe y qué devuelve.
- Comentar en `settings.py` cada cambio hecho (apps, BD, `LOGIN_URL`).
- Nombres de variables simples y en español o inglés coherente (no mezclar estilos en un mismo archivo).
- Sin funciones auxiliares ni abstracciones: cada vista se lee de arriba a abajo.
- No usar librerías adicionales: solo Django y Bootstrap por CDN.

---

## 9. Mapeo con la pauta de evaluación

| Criterio (puntos) | Dónde se cumple |
|---|---|
| Formularios, templates, CSS (10) | Sección 5.4, `base.html`, Bootstrap + `styles.css` |
| Configuración APP (10) | `accounts` y `productos`: `views.py`, `urls.py`, `models.py`, plantillas |
| Configuración PROYECTO (10) | Sección 2: `settings.py`, `config/urls.py` |
| Conexión BD y migraciones (20) | Sección 2 (SQLite, `makemigrations`, `migrate`) y 5.1 (modelo) |
| CRUD tablas (20) | Sección 5.3 (Create, Read, Update, Delete con ORM) |
| Interrogación del código (30) | Sección 8 y Anexo A |

---

## 10. Checklist de pruebas manuales

**Accounts**
- [ ] Registro con usuario existente → error
- [ ] Registro con correo existente → error
- [ ] Contraseña corta / sin mayúscula / sin número → error
- [ ] Contraseñas distintas → error
- [ ] Registro exitoso → el usuario aparece en `auth_user` (se puede revisar con `python manage.py shell`) y redirige a login
- [ ] Login correcto → llega al menú `/`
- [ ] Login fallido 1 y 2 → mensaje con contador
- [ ] Login fallido 3 → bloqueo, incluso con datos correctos después
- [ ] Logout → vuelve a `/login/`

**Seguridad**
- [ ] Sin sesión, `/listado/` redirige a `/login/`
- [ ] Sin sesión, `/eliminar/1/` redirige a `/login/`
- [ ] Con sesión, el nombre de usuario y "Cerrar sesión" se ven en el encabezado

**Productos**
- [ ] Crear producto válido → `alert-success`
- [ ] Crear con datos inválidos → `alert-danger`
- [ ] El producto aparece en el listado
- [ ] Editar → el formulario viene precargado y el cambio se refleja en el listado
- [ ] Eliminar → aparece `confirm()`; al aceptar, desaparece del listado
- [ ] Tabla `productos_producto` creada tras `migrate`

---

## Anexo A — Preguntas que probablemente haga el profesor (y respuesta corta)

1. **¿Qué hace `makemigrations` y qué hace `migrate`?** — `makemigrations` genera el archivo que describe los cambios en los modelos; `migrate` los aplica a la BD y crea las tablas.
2. **¿De dónde salen los usuarios?** — De la tabla `auth_user`, que Django crea al migrar; se manejan con `User.objects.create_user`.
3. **¿Por qué las contraseñas no se ven en texto plano?** — `create_user` las guarda hasheadas; `authenticate` compara contra el hash.
4. **¿Qué hace `@login_required`?** — Antes de ejecutar la vista, revisa si hay sesión; si no, redirige a `LOGIN_URL`.
5. **¿Para qué sirve `{% csrf_token %}`?** — Protege los formularios POST contra envíos falsos desde otros sitios.
6. **¿Qué es el ORM?** — Permite usar la BD con código Python (`Producto.objects.all()`) en vez de escribir SQL.
7. **¿Por qué la vista de eliminar recibe `id`?** — Viene desde la URL (`<int:id>`) y se usa para buscar el registro.
8. **¿Qué cambió respecto a la EVA 1?** — Los usuarios pasaron de una lista en memoria a la BD, y se agregó el CRUD protegido por login.
9. **¿Qué pasa si se reinicia el servidor?** — Usuarios y productos persisten (están en SQLite); solo se reinicia el contador de intentos fallidos (está en memoria).

## Anexo B — Orden de implementación sugerido

1. Copiar el proyecto EVA 1 y ajustar `settings.py` (sección 2).
2. `startapp productos` y registrar ambas apps.
3. Modelo `Producto` → `makemigrations` → `migrate`.
4. Adaptar `accounts`: registro con `create_user`, login con `authenticate`/`login`, logout con `logout`; quitar `USERS` de `store.py` y `welcome`.
5. `base.html` con navbar (usuario + cerrar sesión) y Bootstrap.
6. Vistas y plantillas del CRUD: index → registrar/insertar → listado → actualizar → eliminar.
7. Agregar `@login_required` a todas las vistas de `productos`.
8. Pruebas manuales (sección 10).
9. Repasar el Anexo A y revisar los comentarios del código.
