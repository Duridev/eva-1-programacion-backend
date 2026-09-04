# Especificación EDD — Proyecto Django: Registro y Login

> **EDD (Expectation Driven Development):** antes de escribir código, se define con precisión qué se espera que pase en cada escenario (formato *Dado / Cuando / Entonces*). Esto guía la implementación y sirve como checklist de pruebas al final. Es primo cercano de BDD (Behavior Driven Development), pero aplicado de forma informal para un proyecto académico.

## 0. Contexto y alcance confirmado con el profesor
- **No se requiere base de datos real.** El login se puede resolver con una función que valide contra un usuario "falso"/precargado.
- El registro puede guardar los datos validados en una **estructura en memoria manejada por Django (Python)**, nunca en JavaScript.
- El bloqueo por intentos fallidos debe vivir en el **backend** (servidor), no solo en JS — esto se resuelve sin base de datos real usando estructuras Python en memoria.

## 1. Objetivo
Cumplir el enunciado y la rúbrica con la menor complejidad técnica posible: sin ORM/DB, con templates de Django, CSS básico y JS solo para experiencia de usuario (nunca como única capa de validación).

## 2. Decisiones de diseño (supuestos — revísalos y ajústalos si algo no calza con lo que pidió tu profesor)
- Los "usuarios registrados" viven en una lista de diccionarios en memoria del servidor, por ejemplo en `accounts/store.py`.
- Los intentos fallidos y el estado de bloqueo también viven en memoria del servidor (dict), no en el navegador.
- Dado que el proyecto es "muy básico", las contraseñas se pueden guardar en texto plano en esa lista. Si quieres un plus fácil, se puede usar `make_password` / `check_password` de Django (vienen incluidos, no requieren base de datos) — lo dejo como opcional, no como base.
- Se precarga un usuario de prueba al iniciar el servidor (ej. `admin` / `Admin1234`) para poder probar el login sin pasar antes por el registro.
- Estas estructuras se reinician cada vez que se reinicia el servidor — es esperable y aceptable, ya que el enunciado no pide persistencia real, solo que el control no sea *únicamente* JavaScript.

## 3. Entorno y configuración del proyecto (setup esperado)
- [ ] Entorno virtual creado y activado
- [ ] Django instalado dentro del entorno virtual
- [ ] Proyecto creado (`django-admin startproject config .`)
- [ ] App creada (`python manage.py startapp accounts`)
- [ ] App agregada a `INSTALLED_APPS` en `settings.py`
- [ ] `templates/` configurado en `TEMPLATES > DIRS`
- [ ] `static/` configurado con `STATICFILES_DIRS` / `STATIC_URL`

## 4. Estructura de carpetas propuesta
```
proyecto_login/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── views.py
│   ├── urls.py
│   └── store.py          # USERS, LOGIN_ATTEMPTS (la "base de datos" en memoria)
├── templates/
│   ├── base.html
│   └── accounts/
│       ├── register.html
│       ├── login.html
│       └── welcome.html
└── static/
    ├── css/styles.css
    ├── js/validaciones.js
    └── img/
```

## 5. "Base de datos" en memoria (`store.py`)
- `USERS`: lista de diccionarios `{ "username": str, "email": str, "password": str }`, con al menos un usuario semilla.
- `LOGIN_ATTEMPTS`: diccionario `{ username: { "intentos": int, "bloqueado": bool } }`, se actualiza en cada intento fallido.

## 6. Rutas esperadas (`urls.py`)
| Ruta | Vista | Métodos | Descripción |
|---|---|---|---|
| `/registro/` | `register_view` | GET, POST | Formulario y procesamiento de registro |
| `/login/` | `login_view` | GET, POST | Formulario y procesamiento de login |
| `/bienvenida/` | `welcome_view` | GET | Mensaje de bienvenida post-login |
| `/` | redirige a `/login/` | GET | Punto de entrada |

## 7. Vistas — comportamiento esperado

### 7.1 Registro (`register_view`)
- **Dado** GET en `/registro/` → **entonces** se muestra el formulario vacío.
- **Dado** POST **cuando** el username ya existe en `USERS` → **entonces** error "El nombre de usuario ya está en uso." y no se guarda.
- **Cuando** el correo ya existe en `USERS` → **entonces** error "El correo ya está registrado." y no se guarda.
- **Cuando** la contraseña tiene menos de 8 caracteres, no tiene mayúscula o no tiene número → **entonces** se muestra el error correspondiente y no se guarda.
- **Cuando** contraseña y confirmación no coinciden → **entonces** error "Las contraseñas no coinciden." (se valida también en JS antes de enviar, pero la validación definitiva es en Django).
- **Cuando** todas las validaciones pasan → **entonces** se agrega el usuario a `USERS` y se redirige a `/login/` con mensaje de éxito.

### 7.2 Login (`login_view`)
- **Dado** GET en `/login/` → **entonces** se muestra el formulario.
- **Dado** el usuario está bloqueado → **entonces** se muestra "Clave bloqueada. Ha superado el máximo de intentos permitidos." y no se procesa el intento aunque los datos sean correctos.
- **Cuando** usuario/contraseña no coinciden con `USERS` → **entonces** se incrementa el contador de intentos.
  - **Y si** el contador llega a 3 → se marca `bloqueado = True` y se muestra el mensaje de bloqueo.
  - **Si no** → se muestra "Usuario o contraseña incorrectos. Intento X de 3."
- **Cuando** usuario/contraseña coinciden y no está bloqueado → **entonces** se reinicia el contador a 0, se guarda el username en `request.session` y se redirige a `/bienvenida/`.

### 7.3 Bienvenida (`welcome_view`)
- **Dado** existe `username` en `request.session` → **entonces** se muestra "Bienvenido, {username}".
- **Dado** no hay sesión activa → **entonces** redirige a `/login/`.

## 8. Validaciones — resumen técnico
**Registro:** usuario único y correo único (recorrer `USERS`), `len(password) >= 8`, `any(c.isupper() for c in password)`, `any(c.isdigit() for c in password)`, coincidencia de contraseñas.
**Login:** verificar credenciales contra `USERS`, verificar/actualizar `LOGIN_ATTEMPTS`.

## 9. Templates y herencia
- `base.html`: estructura común, carga de CSS, `{% block content %}`, carga de JS al final del `body`.
- `register.html`, `login.html`, `welcome.html`: heredan con `{% extends "base.html" %}`.
- Tags de Django en el HTML: `{% if errors %}`, `{% for error in errors %}`, `{{ mensaje }}`, `{% csrf_token %}`, `{% load static %}`.
- Uso de `context` (diccionario) desde las vistas hacia `render()` para errores, valores del formulario y contador de intentos.

## 10. Archivos estáticos esperados
**CSS (`styles.css`):** contenedor del login/registro, inputs, botones (con hover), mensajes de error.
**JS (`validaciones.js`):**
- Verificar coincidencia de contraseñas antes de enviar (`submit`, `preventDefault()` si no coinciden).
- Botón mostrar/ocultar contraseña (`type="password"` ↔ `type="text"`).
- Advertencias en vivo de requisitos de contraseña mientras se escribe.

⚠️ Todo lo anterior en JS es solo **experiencia de usuario**. La validación que realmente decide si se guarda el usuario o si el login se bloquea **siempre ocurre en Django**, nunca solo en JS — es justo lo que pide el punto 3c del enunciado.

## 11. Mapeo con la rúbrica
| Criterio | Dónde se cumple |
|---|---|
| Proyecto Django con entorno virtual | Sección 3 |
| Vistas, `urls.py`, `views.py`, `settings.py` | Secciones 3, 6, 7 |
| Templates con template/context | Sección 9 |
| Python dentro de HTML (tags) | Sección 9 |
| Loaders, shortcuts, herencia | `{% extends %}`, `{% load static %}`, `render()` |
| Archivos estáticos (CSS/JS/IMG) | Sección 10 |
| Servidor funcionando | Checklist sección 13 |
| Explicación del código | Preparar comentarios + explicación breve por sección |

## 12. Plan de implementación sugerido
1. Entorno virtual + instalar Django
2. `startproject` + `startapp accounts`
3. Configurar `settings.py` (apps, templates, static)
4. Crear `store.py` con `USERS`, `LOGIN_ATTEMPTS` y usuario semilla
5. `base.html` + CSS base
6. `register_view` + `register.html` + validaciones
7. `login_view` + `login.html` + control de intentos
8. `welcome_view` + `welcome.html`
9. JS (mostrar/ocultar, coincidencia, advertencias)
10. Pruebas manuales (sección 13)
11. Preparar explicación del código

## 13. Casos de prueba manuales (checklist final)
- [ ] Registro con usuario existente → error correcto
- [ ] Registro con correo existente → error correcto
- [ ] Registro con contraseña corta / sin mayúscula / sin número → error correcto
- [ ] Registro con contraseñas que no coinciden → error correcto
- [ ] Registro exitoso → aparece en `USERS`, redirige a login
- [ ] Login exitoso → "Bienvenido, {usuario}"
- [ ] Login fallido 1 y 2 → mensaje de intento fallido, contador sube
- [ ] Login fallido 3 → mensaje de bloqueo, no permite más intentos aunque los datos sean correctos después
- [ ] Mostrar/ocultar contraseña funciona
- [ ] JS avisa si las contraseñas no coinciden antes de enviar
- [ ] CSS aplicado a formulario, inputs, botones, errores, contenedor
