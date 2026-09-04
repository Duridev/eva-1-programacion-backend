/**
 * ==============================================================================
 * ARCHIVO: static/js/validaciones.js
 * ------------------------------------------------------------------------------
 * ¿PARA QUÉ SIRVE ESTE ARCHIVO?
 * Es el script de frontend del navegador. Su propósito es mejorar la Experiencia
 * de Usuario (UX) mediante interactividad visual en tiempo real.
 * 
 * ¿QUÉ FUNCIONES REALIZA DENTRO DEL PROGRAMA?
 * 1. Mostrar/ocultar contraseñas: Alterna el atributo type="password" a type="text"
 *    cuando el usuario presiona el botón con el ícono del ojo.
 * 2. Asistencia en vivo de requisitos: Mientras el usuario tipea en el campo de clave,
 *    evalúa longitud (>=8), mayúscula ([A-Z]) y dígito ([0-9]) y actualiza los textos
 *    a verde o rojo en tiempo real.
 * 3. Prevención y advertencia temprana: Si las dos contraseñas no coinciden,
 *    cancela el envío (e.preventDefault()) y muestra un mensaje de alerta en la página
 *    para evitar un viaje innecesario al servidor.
 * 
 * ⚠️ PREGUNTA CLAVE DEL PROFESOR:
 * "¿Si desactivo JavaScript en el navegador, me puedo registrar con una contraseña mala?"
 * RESPUESTA: NO. La validación que realmente protege el sistema y decide si un usuario
 * se guarda o no ocurre SIEMPRE en Django (accounts/views.py). Este archivo JS es
 * solamente una ayuda visual amigable para el usuario.
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {

    // ==========================================================================
    // 1. FUNCIONALIDAD: MOSTRAR / OCULTAR CONTRASEÑA
    // ==========================================================================
    // Selecciona todos los botones con la clase .btn-toggle-pwd
    const toggleButtons = document.querySelectorAll('.btn-toggle-pwd');

    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Lee el ID del input al que apunta el botón (atributo data-target)
            const targetId = button.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);

            if (targetInput) {
                // Si la clave está oculta (password), la mostramos (text)
                if (targetInput.type === 'password') {
                    targetInput.type = 'text';
                    button.textContent = '🔒'; // Cambia el ícono a candado
                } else {
                    // Si ya está visible, la volvemos a ocultar
                    targetInput.type = 'password';
                    button.textContent = '👁️'; // Vuelve al ícono de ojo
                }
            }
        });
    });

    // ==========================================================================
    // 2. FUNCIONALIDAD: CHECKLIST EN VIVO DE REQUISITOS DE CONTRASEÑA
    // ==========================================================================
    const pwdInput = document.getElementById('id_password');
    const confirmPwdInput = document.getElementById('id_confirm_password');
    const reqLength = document.getElementById('req-length');
    const reqUpper = document.getElementById('req-upper');
    const reqDigit = document.getElementById('req-digit');
    const matchHint = document.getElementById('pwd-match-hint');
    const registerForm = document.getElementById('register-form');
    const clientAlert = document.getElementById('js-register-alert');

    // Solo se ejecuta si estamos en la pantalla de registro (donde existen estos elementos)
    if (pwdInput && reqLength && reqUpper && reqDigit) {
        // Evento 'input': Se dispara cada vez que el usuario escribe o borra una letra
        pwdInput.addEventListener('input', () => {
            const val = pwdInput.value;

            // Requisito 1: Mínimo 8 caracteres
            if (val.length >= 8) {
                reqLength.textContent = '✔ Mínimo 8 caracteres';
                reqLength.className = 'req-item valid'; // Pone el texto en verde
            } else {
                reqLength.textContent = '✖ Mínimo 8 caracteres';
                reqLength.className = 'req-item invalid'; // Pone el texto en gris/rojo
            }

            // Requisito 2: Al menos una letra mayúscula (Expresión Regular: /[A-Z]/)
            if (/[A-Z]/.test(val)) {
                reqUpper.textContent = '✔ Al menos 1 mayúscula';
                reqUpper.className = 'req-item valid';
            } else {
                reqUpper.textContent = '✖ Al menos 1 mayúscula';
                reqUpper.className = 'req-item invalid';
            }

            // Requisito 3: Al menos un número (Expresión Regular: /[0-9]/)
            if (/[0-9]/.test(val)) {
                reqDigit.textContent = '✔ Al menos 1 número';
                reqDigit.className = 'req-item valid';
            } else {
                reqDigit.textContent = '✖ Al menos 1 número';
                reqDigit.className = 'req-item invalid';
            }

            // Validar también si coincide con el campo de confirmación
            validarCoincidenciaEnVivo();
        });
    }

    // Escucha eventos de tipeo en el campo de confirmación de contraseña
    if (confirmPwdInput) {
        confirmPwdInput.addEventListener('input', () => {
            validarCoincidenciaEnVivo();
        });
    }

    /**
     * Función auxiliar para verificar si ambas claves escritas son idénticas
     */
    function validarCoincidenciaEnVivo() {
        if (!confirmPwdInput || !matchHint) return;

        const val1 = pwdInput ? pwdInput.value : '';
        const val2 = confirmPwdInput.value;

        // Si el usuario aún no ha escrito en confirmación, no mostramos nada
        if (!val2) {
            matchHint.textContent = '';
            matchHint.className = 'hint-text';
            return;
        }

        // Comparamos los valores de ambos campos
        if (val1 === val2) {
            matchHint.textContent = '✔ Las contraseñas coinciden';
            matchHint.className = 'hint-text match'; // Estilo verde
        } else {
            matchHint.textContent = '✖ Las contraseñas no coinciden';
            matchHint.className = 'hint-text mismatch'; // Estilo rojo
        }
    }

    // ==========================================================================
    // 3. FUNCIONALIDAD: VALIDACIÓN ANTES DE ENVIAR (SUBMIT)
    // ==========================================================================
    if (registerForm && pwdInput && confirmPwdInput) {
        registerForm.addEventListener('submit', (e) => {
            const val1 = pwdInput.value;
            const val2 = confirmPwdInput.value;

            // Si las contraseñas son diferentes:
            if (val1 !== val2) {
                // e.preventDefault() cancela el envío del formulario al servidor
                e.preventDefault();

                // Mostramos un aviso visual en la parte superior del formulario
                if (clientAlert) {
                    clientAlert.innerHTML = '<strong>Aviso:</strong> Las contraseñas ingresadas no coinciden. Corrígelas antes de continuar.';
                    clientAlert.style.display = 'block';
                    confirmPwdInput.focus();
                } else {
                    alert('Las contraseñas no coinciden.');
                }
            } else {
                // Si coinciden, ocultamos la alerta y dejamos que Django procese
                if (clientAlert) {
                    clientAlert.style.display = 'none';
                }
            }
        });
    }
});
