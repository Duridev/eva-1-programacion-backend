"""
Pruebas automatizadas de la aplicación accounts (accounts/tests.py).

Verificación del checklist de la Sección 13 de especificacion_edd_login_django.md.
Se utiliza SimpleTestCase para no requerir base de datos.
"""

from django.test import SimpleTestCase, Client
from accounts.store import USERS, LOGIN_ATTEMPTS


class AccountsEddTests(SimpleTestCase):
    def setUp(self):
        """Reinicia el estado en memoria antes de cada prueba."""
        USERS.clear()
        USERS.append({
            "username": "admin",
            "email": "admin@ejemplo.com",
            "password": "Admin1234"
        })
        LOGIN_ATTEMPTS.clear()
        self.client = Client()

    def test_01_raiz_redirige_a_login(self):
        """Verifica que la raíz '/' redirige a '/login/'."""
        response = self.client.get('/')
        self.assertRedirects(response, '/login/', fetch_redirect_response=False)

    def test_02_registro_usuario_existente_error(self):
        """Registro con usuario existente -> error 'El nombre de usuario ya está en uso.'"""
        response = self.client.post('/registro/', {
            'username': 'admin',
            'email': 'nuevo@correo.com',
            'password': 'Password1',
            'confirm_password': 'Password1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El nombre de usuario ya está en uso.")

    def test_03_registro_correo_existente_error(self):
        """Registro con correo existente -> error 'El correo ya está registrado.'"""
        response = self.client.post('/registro/', {
            'username': 'otrouser',
            'email': 'admin@ejemplo.com',
            'password': 'Password1',
            'confirm_password': 'Password1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El correo ya está registrado.")

    def test_04_registro_password_invalida(self):
        """Registro con contraseña corta, sin mayúscula o sin número."""
        # Corta (< 8 caracteres)
        res_corta = self.client.post('/registro/', {
            'username': 'user1',
            'email': 'user1@correo.com',
            'password': 'Ab1',
            'confirm_password': 'Ab1'
        })
        self.assertContains(res_corta, "La contraseña debe tener al menos 8 caracteres.")

        # Sin mayúscula
        res_minus = self.client.post('/registro/', {
            'username': 'user2',
            'email': 'user2@correo.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertContains(res_minus, "La contraseña debe contener al menos una letra mayúscula.")

        # Sin número
        res_sin_num = self.client.post('/registro/', {
            'username': 'user3',
            'email': 'user3@correo.com',
            'password': 'PasswordSinNumero',
            'confirm_password': 'PasswordSinNumero'
        })
        self.assertContains(res_sin_num, "La contraseña debe contener al menos un número.")

    def test_05_registro_passwords_no_coinciden(self):
        """Registro con contraseñas que no coinciden -> error 'Las contraseñas no coinciden.'"""
        response = self.client.post('/registro/', {
            'username': 'usuario_nuevo',
            'email': 'nuevo@test.com',
            'password': 'Password123',
            'confirm_password': 'OtraPassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Las contraseñas no coinciden.")

    def test_06_registro_exitoso_y_redireccion(self):
        """Registro exitoso -> se agrega a USERS y redirige a /login/?registrado=1."""
        response = self.client.post('/registro/', {
            'username': 'carlos',
            'email': 'carlos@test.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        self.assertRedirects(response, '/login/?registrado=1', fetch_redirect_response=False)
        self.assertTrue(any(u['username'] == 'carlos' for u in USERS))

    def test_07_login_exitoso_y_bienvenida(self):
        """Login exitoso -> guarda sesión y redirige a bienvenida."""
        response = self.client.post('/login/', {
            'username': 'admin',
            'password': 'Admin1234'
        }, follow=True)
        self.assertRedirects(response, '/bienvenida/')
        self.assertContains(response, "Bienvenido, admin")

    def test_08_login_fallido_intentos_1_y_2(self):
        """Login fallido en intentos 1 y 2 muestra contador incremental."""
        # Intento 1
        res1 = self.client.post('/login/', {'username': 'admin', 'password': 'WrongPassword1'})
        self.assertContains(res1, "Usuario o contraseña incorrectos. Intento 1 de 3.")
        self.assertEqual(LOGIN_ATTEMPTS['admin']['intentos'], 1)
        self.assertFalse(LOGIN_ATTEMPTS['admin']['bloqueado'])

        # Intento 2
        res2 = self.client.post('/login/', {'username': 'admin', 'password': 'WrongPassword2'})
        self.assertContains(res2, "Usuario o contraseña incorrectos. Intento 2 de 3.")
        self.assertEqual(LOGIN_ATTEMPTS['admin']['intentos'], 2)
        self.assertFalse(LOGIN_ATTEMPTS['admin']['bloqueado'])

    def test_09_login_fallido_intento_3_bloqueo(self):
        """Login fallido 3 -> bloquea la cuenta y no permite más intentos."""
        self.client.post('/login/', {'username': 'admin', 'password': 'WrongPassword1'})
        self.client.post('/login/', {'username': 'admin', 'password': 'WrongPassword2'})
        res3 = self.client.post('/login/', {'username': 'admin', 'password': 'WrongPassword3'})

        self.assertContains(res3, "Clave bloqueada. Ha superado el máximo de intentos permitidos.")
        self.assertEqual(LOGIN_ATTEMPTS['admin']['intentos'], 3)
        self.assertTrue(LOGIN_ATTEMPTS['admin']['bloqueado'])

        # Intento 4 con contraseña CORRECTA: debe permanecer bloqueado
        res4 = self.client.post('/login/', {'username': 'admin', 'password': 'Admin1234'})
        self.assertContains(res4, "Clave bloqueada. Ha superado el máximo de intentos permitidos.")
        self.assertNotIn('username', self.client.session)

    def test_10_acceso_bienvenida_sin_sesion(self):
        """Acceso a /bienvenida/ sin sesión activa redirige a /login/."""
        response = self.client.get('/bienvenida/')
        self.assertRedirects(response, '/login/', fetch_redirect_response=False)
