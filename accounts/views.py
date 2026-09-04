"""
==============================================================================
ARCHIVO: accounts/views.py
------------------------------------------------------------------------------
¿PARA QUÉ SIRVE ESTE ARCHIVO?
Es el cerebro y controlador (la "C" del patrón MVC/MVT) de la aplicación.
Contiene las funciones que reciben las peticiones HTTP (request), aplican la
lógica de negocio y las validaciones de seguridad, y deciden qué plantilla HTML
mostrar o hacia dónde redirigir al usuario.

¿QUÉ FUNCIONES REALIZA DENTRO DEL PROGRAMA?
1. register_view: Procesa el formulario de registro, valida los requisitos en el
   servidor y guarda al usuario en la lista USERS de store.py.
2. login_view: Verifica credenciales, cuenta los intentos fallidos, bloquea la
   cuenta al 3er error y gestiona la sesión con cookies firmadas.
3. welcome_view: Protege la vista de bienvenida asegurando que solo ingresen
   usuarios con sesión activa.
4. logout_view: Destruye la sesión actual y devuelve al usuario a la pantalla de login.
==============================================================================
"""

from django.shortcuts import render, redirect
from .store import USERS, LOGIN_ATTEMPTS


# ==============================================================================
# VISTA 1: REGISTRO DE USUARIOS (register_view)
# ==============================================================================
def register_view(request):
    """
    Controla el flujo de registro según la metodología EDD (Sección 7.1 y 8):
    - Si el método es GET: El usuario recién entra a la página -> Se muestra el formulario vacío.
    - Si el método es POST: El usuario hizo clic en 'Registrar' -> Se extraen y validan los datos.
    """
    # CASO GET: Solo renderizar la plantilla HTML
    if request.method == 'GET':
        return render(request, 'accounts/register.html')

    # CASO POST: Capturar los datos enviados en el formulario
    # .strip() elimina espacios en blanco accidentales al inicio y final
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')

    errors = []

    # --------------------------------------------------------------------------
    # BLOQUE DE VALIDACIONES EN EL BACKEND (Python)
    # --------------------------------------------------------------------------
    
    # 1. Campos obligatorios: Ningún campo puede llegar en blanco
    if not username:
        errors.append("El nombre de usuario es obligatorio.")
    if not email:
        errors.append("El correo electrónico es obligatorio.")
    if not password:
        errors.append("La contraseña es obligatoria.")

    # 2. Unicidad de nombre de usuario: Comprobar que no exista en la lista USERS
    # any(...) recorre la lista USERS buscando coincidencias exactas (sin importar mayúsculas)
    if username and any(u['username'].lower() == username.lower() for u in USERS):
        errors.append("El nombre de usuario ya está en uso.")

    # 3. Unicidad de correo electrónico: Comprobar que el correo no esté registrado
    if email and any(u['email'].lower() == email for u in USERS):
        errors.append("El correo ya está registrado.")

    # 4. Reglas de complejidad de la contraseña (Sección 8 de la especificación):
    if password:
        # a) Mínimo 8 caracteres
        if len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres.")
        # b) Al menos una letra mayúscula
        if not any(c.isupper() for c in password):
            errors.append("La contraseña debe contener al menos una letra mayúscula.")
        # c) Al menos un dígito numérico
        if not any(c.isdigit() for c in password):
            errors.append("La contraseña debe contener al menos un número.")

    # 5. Coincidencia de contraseñas: Ambas deben ser exactamente iguales
    if password and confirm_password and password != confirm_password:
        errors.append("Las contraseñas no coinciden.")

    # --------------------------------------------------------------------------
    # EVALUACIÓN DE RESULTADOS
    # --------------------------------------------------------------------------
    # Si se detectó algún error, se vuelve a mostrar el formulario con la lista de errores.
    # Se reenvían 'prev_username' y 'prev_email' para que el usuario no tenga que escribirlos otra vez.
    if errors:
        return render(request, 'accounts/register.html', {
            'errors': errors,
            'prev_username': username,
            'prev_email': email
        })

    # Si NO hay errores, el usuario es válido:
    # Se agrega el nuevo usuario como diccionario a la lista USERS en memoria
    USERS.append({
        'username': username,
        'email': email,
        'password': password
    })

    # Se redirige al login con el parámetro en URL '?registrado=1' para mostrar mensaje de éxito
    return redirect('/login/?registrado=1')


# ==============================================================================
# VISTA 2: INICIO DE SESIÓN Y BLOQUEO (login_view)
# ==============================================================================
def login_view(request):
    """
    Controla el login y el bloqueo por intentos fallidos (Sección 7.2 y 8):
    - Al 3er intento fallido: Bloquea permanentemente la cuenta en LOGIN_ATTEMPTS.
    - Credenciales correctas: Reinicia intentos a 0 y guarda el usuario en sesión.
    """
    # Detectar si el usuario viene redirigido desde un registro exitoso
    mensaje_exito = None
    if request.GET.get('registrado') == '1':
        mensaje_exito = "¡Usuario registrado con éxito! Ya puedes iniciar sesión."

    # CASO GET: Mostrar el formulario de login limpio
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {
            'mensaje_exito': mensaje_exito
        })

    # CASO POST: Procesar intento de autenticación
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    # Validación básica de campos vacíos
    if not username or not password:
        return render(request, 'accounts/login.html', {
            'error_login': "Por favor ingresa usuario y contraseña.",
            'prev_username': username
        })

    # --------------------------------------------------------------------------
    # PASO 1: VERIFICAR SI LA CUENTA YA ESTÁ BLOQUEADA
    # --------------------------------------------------------------------------
    # Consultamos el diccionario LOGIN_ATTEMPTS en store.py
    estado_usuario = LOGIN_ATTEMPTS.get(username, {'intentos': 0, 'bloqueado': False})

    # Regla EDD: Si está bloqueado, NO se procesa el intento aunque la contraseña sea correcta
    if estado_usuario.get('bloqueado'):
        return render(request, 'accounts/login.html', {
            'error_login': "Clave bloqueada. Ha superado el máximo de intentos permitidos.",
            'bloqueado': True,
            'prev_username': username
        })

    # --------------------------------------------------------------------------
    # PASO 2: VERIFICAR CREDENCIALES CONTRA LA LISTA USERS
    # --------------------------------------------------------------------------
    usuario_encontrado = None
    for u in USERS:
        if u['username'] == username and u['password'] == password:
            usuario_encontrado = u
            break

    # --------------------------------------------------------------------------
    # PASO 3: RESPUESTA SEGÚN EL RESULTADO
    # --------------------------------------------------------------------------
    if usuario_encontrado:
        # A) CREDENCIALES CORRECTAS:
        # 1. Se reinicia el contador de intentos fallidos para este usuario
        LOGIN_ATTEMPTS[username] = {'intentos': 0, 'bloqueado': False}

        # 2. Se almacena el nombre del usuario en la sesión del navegador
        # Django firma criptográficamente esta cookie gracias a 'signed_cookies'
        request.session['username'] = usuario_encontrado['username']

        # 3. Redirección a la vista de bienvenida protegida
        return redirect('/bienvenida/')
    else:
        # B) CREDENCIALES INCORRECTAS:
        # Si el usuario no estaba en el registro de intentos, se inicializa
        if username not in LOGIN_ATTEMPTS:
            LOGIN_ATTEMPTS[username] = {'intentos': 0, 'bloqueado': False}

        # Se incrementa en 1 el contador de fallos
        LOGIN_ATTEMPTS[username]['intentos'] += 1
        intentos = LOGIN_ATTEMPTS[username]['intentos']

        # Si llegó a 3 intentos fallidos, se activa el bloqueo
        if intentos >= 3:
            LOGIN_ATTEMPTS[username]['bloqueado'] = True
            mensaje_error = "Clave bloqueada. Ha superado el máximo de intentos permitidos."
            bloqueado = True
        else:
            mensaje_error = f"Usuario o contraseña incorrectos. Intento {intentos} de 3."
            bloqueado = False

        # Se devuelve el formulario con el mensaje de advertencia correspondiente
        return render(request, 'accounts/login.html', {
            'error_login': mensaje_error,
            'bloqueado': bloqueado,
            'prev_username': username
        })


# ==============================================================================
# VISTA 3: PANTALLA DE BIENVENIDA (welcome_view)
# ==============================================================================
def welcome_view(request):
    """
    Vista protegida post-login (Sección 7.3):
    - Verifica si existe la clave 'username' en request.session.
    - Si existe: El usuario está autenticado -> Renderiza welcome.html con su nombre.
    - Si NO existe: Intento de acceso no autorizado -> Redirige al login de inmediato.
    """
    # Intentamos leer el usuario guardado en la sesión
    username = request.session.get('username')

    # Si no hay sesión iniciada, protección por redirección
    if not username:
        return redirect('/login/')

    # Si hay sesión, renderizamos la plantilla pasando el nombre en el contexto
    return render(request, 'accounts/welcome.html', {
        'username': username
    })


# ==============================================================================
# VISTA 4: CIERRE DE SESIÓN (logout_view)
# ==============================================================================
def logout_view(request):
    """
    Destruye la sesión activa del usuario:
    - request.session.flush() borra tanto los datos internos de la sesión
      como la cookie en el navegador del cliente.
    - Redirige al formulario de login.
    """
    request.session.flush()
    return redirect('/login/')
