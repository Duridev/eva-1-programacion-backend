"""
==============================================================================
ARCHIVO: accounts/tests.py
------------------------------------------------------------------------------
¿PARA QUÉ SIRVE ESTE ARCHIVO?
Contiene las pruebas unitarias automatizadas del sistema. Permite verificar que
todas las reglas de negocio descritas en la Sección 13 del documento EDD
funcionan exactamente como se espera sin necesidad de probarlas manualmente a mano.

¿QUÉ FUNCIONES REALIZA DENTRO DEL PROGRAMA?
1. Hereda de 'SimpleTestCase': Permite probar vistas y peticiones HTTP SIN necesitar
   crear ni configurar una base de datos de pruebas.
2. Utiliza 'self.client': Un cliente virtual que simula ser un navegador web que
   envía peticiones GET y POST al servidor.
3. Método setUp(): Reinicia la lista USERS y LOGIN_ATTEMPTS antes de cada prueba
   para garantizar que cada test se ejecute de forma aislada e independiente.
==============================================================================
"""

from django.test import SimpleTestCase, Client
from accounts.store import USERS, LOGIN_ATTEMPTS


class AccountsEddTests(SimpleTestCase):
    def setUp(self):
        """
        Método que se ejecuta automáticamente ANTES de cada prueba.
        Restaura el estado original en memoria (solo el usuario semilla 'admin').
        """
        USERS.clear()
        USERS.append({
            "username": "admin",
            "email": "admin@ejemplo.com",
            "password": "Admin1234"
        })
        LOGIN_ATTEMPTS.clear()
        self.client = Client()

    def test_01_raiz_redirige_a_login(self):
        """Caso 1: Al entrar a la raíz '/' debe redirigir a '/login/'."""
        response = self.client.get('/')
        self.assertRedirects(response, '/login/', fetch_redirect_response=False)

    def test_02_registro_usuario_existente_error(self):
        """Caso 2: Intentar registrar un usuario existente ('admin') genera error."""
        response = self.client.post('/registro/', {
            'username': 'admin',
            'email': 'nuevo@correo.com',
            'password': 'Password1',
            'confirm_password': 'Password1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El nombre de usuario ya está en uso.")

    def test_03_registro_correo_existente_error(self):
        """Caso 3: Intentar registrar un correo existente genera error."""
        response = self.client.post('/registro/', {
            'username': 'otrouser',
            'email': 'admin@ejemplo.com',
            'password': 'Password1',
            'confirm_password': 'Password1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El correo ya está registrado.")

    def test_04_registro_password_invalida(self):
        """Caso 4: Validar las 3 reglas de contraseña en servidor (longitud, mayúscula, número)."""
        # Prueba 4a: Menor a 8 caracteres
        res_corta = self.client.post('/registro/', {
            'username': 'user1',
            'email': 'user1@correo.com',
            'password': 'Ab1',
            'confirm_password': 'Ab1'
        })
        self.assertContains(res_corta, "La contraseña debe tener al menos 8 caracteres.")

        # Prueba 4b: Sin mayúscula
        res_minus = self.client.post('/registro/', {
            'username': 'user2',
            'email': 'user2@correo.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertContains(res_minus, "La contraseña debe contener al menos una letra mayúscula.")

        # Prueba 4c: Sin número
        res_sin_num = self.client.post('/registro/', {
            'username': 'user3',
            'email': 'user3@correo.com',
            'password': 'PasswordSinNumero',
            'confirm_password': 'PasswordSinNumero'
        })
        self.assertContains(res_sin_num, "La contraseña debe contener al menos un número.")

    def test_05_registro_passwords_no_coinciden(self):
        """Caso 5: Contraseñas no coinciden genera error 'Las contraseñas no coinciden.'"""
        response = self.client.post('/registro/', {
            'username': 'usuario_nuevo',
            'email': 'nuevo@test.com',
            'password': 'Password123',
            'confirm_password': 'OtraPassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Las contraseñas no coinciden.")

    def test_06_registro_exitoso_y_redireccion(self):
        """Caso 6: Registro con datos correctos se guarda en USERS y redirige a login."""
        response = self.client.post('/registro/', {
            'username': 'carlos',
            'email': 'carlos@test.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        self.assertRedirects(response, '/login/?registrado=1', fetch_redirect_response=False)
        self.assertTrue(any(u['username'] == 'carlos' for u in USERS))

    def test_07_login_exitoso_y_bienvenida(self):
        """Caso 7: Credenciales correctas crean la sesión y llevan a la bienvenida."""
        response = self.client.post('/login/', {
            'username': 'admin',
            'password': 'Admin1234'
        }, follow=True)
        self.assertRedirects(response, '/bienvenida/')
        self.assertContains(response, "Bienvenido, admin")

    def test_08_login_fallido_intentos_1_y_2(self):
        """Caso 8: Contraseñas incorrectas incrementan el contador ('Intento X de 3')."""
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
        """Caso 9: Al tercer fallo se bloquea y no permite entrar ni con clave correcta."""
        self.client.post('/login/', {'username': 'admin', 'password': 'WrongPassword1'})
        self.client.post('/login/', {'username': 'admin', 'password': 'WrongPassword2'})
        res3 = self.client.post('/login/', {'username': 'admin', 'password': 'WrongPassword3'})

        # Verificar mensaje y estado bloqueado
        self.assertContains(res3, "Clave bloqueada. Ha superado el máximo de intentos permitidos.")
        self.assertEqual(LOGIN_ATTEMPTS['admin']['intentos'], 3)
        self.assertTrue(LOGIN_ATTEMPTS['admin']['bloqueado'])

        # Intento 4: Probar con la clave CORRECTA ('Admin1234') -> Debe seguir bloqueado
        res4 = self.client.post('/login/', {'username': 'admin', 'password': 'Admin1234'})
        self.assertContains(res4, "Clave bloqueada. Ha superado el máximo de intentos permitidos.")
        self.assertNotIn('username', self.client.session)

    def test_10_acceso_bienvenida_sin_sesion(self):
        """Caso 10: Intentar ingresar a /bienvenida/ directamente sin login redirige a /login/."""
        response = self.client.get('/bienvenida/')
        self.assertRedirects(response, '/login/', fetch_redirect_response=False)
