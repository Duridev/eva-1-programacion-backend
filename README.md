# Sistema de Autenticación y Registro (Django — EDD)

Proyecto introductorio de backend desarrollado en Django para la **Evaluación 1**, siguiendo la metodología **EDD (*Expectation Driven Development*)** descrita en [`especificacion_edd_login_django.md`](./especificacion_edd_login_django.md).

---

## 📌 Características Principales

- **Arquitectura en Memoria (Sin Base de Datos / Sin ORM)**:
  - Los usuarios registrados residen en `accounts/store.py` (`USERS`).
  - El control de intentos fallidos y bloqueo reside en `accounts/store.py` (`LOGIN_ATTEMPTS`).
- **Sesiones Basadas en Cookies Firmadas (`signed_cookies`)**:
  - No requiere `python manage.py migrate` ni bases de datos SQLite/PostgreSQL.
  - La sesión del usuario autenticado se maneja con `request.session`.
- **Validaciones en el Servidor (Django)**:
  - Nombre de usuario único.
  - Correo electrónico único.
  - Contraseña segura: mínimo 8 caracteres, al menos una letra mayúscula y al menos un número.
  - Coincidencia estricta de contraseña y confirmación.
- **Control de Bloqueo por Intentos Fallidos**:
  - Máximo 3 intentos fallidos consecutivos. Al tercer fallo, la cuenta se bloquea en el servidor impidiendo el acceso incluso con la clave correcta.
- **Experiencia de Usuario (UX) con JavaScript y CSS Puro**:
  - Alternador para mostrar u ocultar contraseñas (ícono de ojo).
  - Comprobación visual en vivo de requisitos de contraseña mientras se escribe.
  - Advertencia antes del envío si las contraseñas no coinciden.
  - Diseño responsive y limpio con tipografía Inter.

---

## 📂 Estructura del Proyecto

```text
eva-1/
├── manage.py
├── .gitignore
├── README.md
├── especificacion_edd_login_django.md
├── config/
│   ├── settings.py       # Configuración con signed_cookies y sin BD
│   ├── urls.py           # Redirección raíz '/' a '/login/' e includes
│   └── wsgi.py
├── accounts/
│   ├── store.py          # USERS y LOGIN_ATTEMPTS en memoria
│   ├── views.py          # register_view, login_view, welcome_view, logout_view
│   └── urls.py           # Rutas /registro/, /login/, /bienvenida/, /logout/
├── templates/
│   ├── base.html         # Plantilla base con navbar y footer
│   └── accounts/
│       ├── register.html # Formulario de registro con validaciones visuales
│       ├── login.html    # Formulario de login, contador de intentos y bloqueo
│       └── welcome.html  # Pantalla protegida de bienvenida
└── static/
    ├── css/
    │   └── styles.css    # Estilos CSS puro
    ├── js/
    │   └── validaciones.js # Lógica de interacción en cliente
    └── img/
        └── README.md
```

---

## 🚀 Puesta en Marcha

### 1. Activar el Entorno Virtual

En Windows (PowerShell):
```powershell
.\env\Scripts\activate
```

*(En Linux / macOS: `source env/bin/activate`)*

### 2. Iniciar el Servidor de Desarrollo

```powershell
python manage.py runserver
```

El proyecto estará disponible inmediatamente en:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** (redirige automáticamente a `/login/`).

> [!NOTE]
> No es necesario ejecutar `python manage.py migrate` debido a que el proyecto utiliza el motor de sesiones en cookies criptográficamente firmadas.

---

## 🔑 Credenciales de Prueba Precargadas

| Campo | Valor |
|---|---|
| **Usuario** | `admin` |
| **Contraseña** | `Admin1234` |
| **Correo** | `admin@ejemplo.com` |
