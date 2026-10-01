from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .store import LOGIN_ATTEMPTS


def register_view(request):
    """
    Vista de registro de usuario.
    Recibe por GET el formulario y por POST valida datos y crea un nuevo usuario
    con contraseña encriptada en la tabla auth_user mediante create_user.
    """
    if request.method == 'GET':
        return render(request, 'accounts/register.html')

    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')

    errors = []

    # Validaciones de campos obligatorios
    if not username:
        errors.append("El nombre de usuario es obligatorio.")
    if not email:
        errors.append("El correo electrónico es obligatorio.")
    if not password:
        errors.append("La contraseña es obligatoria.")

    # Validación de usuario y correo únicos consultando el ORM de Django en SQLite
    if username and User.objects.filter(username=username).exists():
        errors.append("El nombre de usuario ya está en uso.")

    if email and User.objects.filter(email=email).exists():
        errors.append("El correo ya está registrado.")

    # Validaciones de seguridad de contraseña
    if password:
        if len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres.")
        if not any(c.isupper() for c in password):
            errors.append("La contraseña debe contener al menos una letra mayúscula.")
        if not any(c.isdigit() for c in password):
            errors.append("La contraseña debe contener al menos un número.")

    # Validación de coincidencia de contraseñas
    if password and confirm_password and password != confirm_password:
        errors.append("Las contraseñas no coinciden.")

    if errors:
        return render(request, 'accounts/register.html', {
            'errors': errors,
            'prev_username': username,
            'prev_email': email
        })

    # create_user hashea automáticamente la contraseña antes de guardarla en auth_user
    User.objects.create_user(username=username, email=email, password=password)

    return redirect('/login/?registrado=1')


def login_view(request):
    """
    Vista de inicio de sesión.
    Recibe credenciales por POST, consulta intentos en LOGIN_ATTEMPTS, valida con authenticate()
    y crea la sesión en base de datos con login() redirigiendo a la raíz '/'.
    """
    # Si el usuario ya está autenticado, se redirige directamente al menú principal
    if request.user.is_authenticated:
        return redirect('/')

    mensaje_exito = None
    if request.GET.get('registrado') == '1':
        mensaje_exito = "¡Usuario registrado con éxito! Ya puedes iniciar sesión."

    if request.method == 'GET':
        return render(request, 'accounts/login.html', {
            'mensaje_exito': mensaje_exito
        })

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    if not username or not password:
        return render(request, 'accounts/login.html', {
            'error_login': "Por favor ingresa usuario y contraseña.",
            'prev_username': username
        })

    estado_usuario = LOGIN_ATTEMPTS.get(username, {'intentos': 0, 'bloqueado': False})

    # Verificar si el usuario ya se encuentra bloqueado
    if estado_usuario.get('bloqueado'):
        return render(request, 'accounts/login.html', {
            'error_login': "Clave bloqueada. Ha superado el máximo de intentos permitidos.",
            'bloqueado': True,
            'prev_username': username
        })

    # authenticate() verifica usuario y contraseña hasheada contra auth_user
    user = authenticate(request, username=username, password=password)

    if user is not None:
        # Credenciales correctas: se resetea el contador de intentos y se inicia sesión
        LOGIN_ATTEMPTS[username] = {'intentos': 0, 'bloqueado': False}
        login(request, user)
        return redirect('/')
    else:
        # Credenciales incorrectas: registrar intento fallido
        if username not in LOGIN_ATTEMPTS:
            LOGIN_ATTEMPTS[username] = {'intentos': 0, 'bloqueado': False}

        LOGIN_ATTEMPTS[username]['intentos'] += 1
        intentos = LOGIN_ATTEMPTS[username]['intentos']

        if intentos >= 3:
            LOGIN_ATTEMPTS[username]['bloqueado'] = True
            mensaje_error = "Clave bloqueada. Ha superado el máximo de intentos permitidos."
            bloqueado = True
        else:
            mensaje_error = f"Usuario o contraseña incorrectos. Intento {intentos} de 3."
            bloqueado = False

        return render(request, 'accounts/login.html', {
            'error_login': mensaje_error,
            'bloqueado': bloqueado,
            'prev_username': username
        })


def logout_view(request):
    """
    Vista de cierre de sesión.
    Cierra la sesión del usuario mediante logout() de Django y redirige a /login/.
    """
    logout(request)
    return redirect('/login/')
