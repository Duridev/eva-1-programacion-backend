from django.shortcuts import render, redirect
from .store import USERS, LOGIN_ATTEMPTS

def register_view(request):
    if request.method == 'GET':
        return render(request, 'accounts/register.html')

    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')

    errors = []
    
    if not username:
        errors.append("El nombre de usuario es obligatorio.")
    if not email:
        errors.append("El correo electrónico es obligatorio.")
    if not password:
        errors.append("La contraseña es obligatoria.")

    if username and any(u['username'].lower() == username.lower() for u in USERS):
        errors.append("El nombre de usuario ya está en uso.")

    if email and any(u['email'].lower() == email for u in USERS):
        errors.append("El correo ya está registrado.")

    if password:
        if len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres.")
        if not any(c.isupper() for c in password):
            errors.append("La contraseña debe contener al menos una letra mayúscula.")
        if not any(c.isdigit() for c in password):
            errors.append("La contraseña debe contener al menos un número.")

    if password and confirm_password and password != confirm_password:
        errors.append("Las contraseñas no coinciden.")

    if errors:
        return render(request, 'accounts/register.html', {
            'errors': errors,
            'prev_username': username,
            'prev_email': email
        })

    USERS.append({
        'username': username,
        'email': email,
        'password': password
    })

    return redirect('/login/?registrado=1')


def login_view(request):
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

    if estado_usuario.get('bloqueado'):
        return render(request, 'accounts/login.html', {
            'error_login': "Clave bloqueada. Ha superado el máximo de intentos permitidos.",
            'bloqueado': True,
            'prev_username': username
        })

    usuario_encontrado = None
    for u in USERS:
        if u['username'] == username and u['password'] == password:
            usuario_encontrado = u
            break

    if usuario_encontrado:
        LOGIN_ATTEMPTS[username] = {'intentos': 0, 'bloqueado': False}
        request.session['username'] = usuario_encontrado['username']
        return redirect('/bienvenida/')
    else:
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


def welcome_view(request):
    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    return render(request, 'accounts/welcome.html', {
        'username': username
    })


def logout_view(request):
    request.session.flush()
    return redirect('/login/')
