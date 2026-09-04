/**
 * validaciones.js
 * 
 * Funcionalidades interactivas del lado del cliente (UX):
 * 1. Mostrar/ocultar contraseña al pulsar el botón con el ícono de ojo.
 * 2. Indicadores en vivo de cumplimiento de requisitos de contraseña mientras el usuario escribe.
 * 3. Alerta y advertencia antes de enviar el formulario si las contraseñas no coinciden.
 * 
 * NOTA IMPORTANTE (Arquitectura del proyecto):
 * Todo el código de este archivo responde únicamente a mejorar la experiencia
 * de usuario (UX). La validación definitiva, segura y vinculante se realiza
 * SIEMPRE en el servidor Django (accounts/views.py).
 */

document.addEventListener('DOMContentLoaded', () => {

    // ==========================================================================
    // 1. Mostrar / Ocultar Contraseña
    // ==========================================================================
    const toggleButtons = document.querySelectorAll('.btn-toggle-pwd');

    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);

            if (targetInput) {
                if (targetInput.type === 'password') {
                    targetInput.type = 'text';
                    button.textContent = '🔒'; // Cambia ícono para reflejar opción de ocultar
                } else {
                    targetInput.type = 'password';
                    button.textContent = '👁️';
                }
            }
        });
    });

    // ==========================================================================
    // 2. Advertencias en vivo sobre requisitos de contraseña (Registro)
    // ==========================================================================
    const pwdInput = document.getElementById('id_password');
    const confirmPwdInput = document.getElementById('id_confirm_password');
    const reqLength = document.getElementById('req-length');
    const reqUpper = document.getElementById('req-upper');
    const reqDigit = document.getElementById('req-digit');
    const matchHint = document.getElementById('pwd-match-hint');
    const registerForm = document.getElementById('register-form');
    const clientAlert = document.getElementById('js-register-alert');

    if (pwdInput && reqLength && reqUpper && reqDigit) {
        pwdInput.addEventListener('input', () => {
            const val = pwdInput.value;

            // Requisito: Al menos 8 caracteres
            if (val.length >= 8) {
                reqLength.textContent = '✔ Mínimo 8 caracteres';
                reqLength.className = 'req-item valid';
            } else {
                reqLength.textContent = '✖ Mínimo 8 caracteres';
                reqLength.className = 'req-item invalid';
            }

            // Requisito: Al menos una mayúscula
            if (/[A-Z]/.test(val)) {
                reqUpper.textContent = '✔ Al menos 1 mayúscula';
                reqUpper.className = 'req-item valid';
            } else {
                reqUpper.textContent = '✖ Al menos 1 mayúscula';
                reqUpper.className = 'req-item invalid';
            }

            // Requisito: Al menos un número
            if (/[0-9]/.test(val)) {
                reqDigit.textContent = '✔ Al menos 1 número';
                reqDigit.className = 'req-item valid';
            } else {
                reqDigit.textContent = '✖ Al menos 1 número';
                reqDigit.className = 'req-item invalid';
            }

            // Verificar coincidencia en caso de que ya haya texto en confirmación
            validarCoincidenciaEnVivo();
        });
    }

    // Comprobar coincidencia mientras se escribe en la confirmación
    if (confirmPwdInput) {
        confirmPwdInput.addEventListener('input', () => {
            validarCoincidenciaEnVivo();
        });
    }

    function validarCoincidenciaEnVivo() {
        if (!confirmPwdInput || !matchHint) return;

        const val1 = pwdInput ? pwdInput.value : '';
        const val2 = confirmPwdInput.value;

        if (!val2) {
            matchHint.textContent = '';
            matchHint.className = 'hint-text';
            return;
        }

        if (val1 === val2) {
            matchHint.textContent = '✔ Las contraseñas coinciden';
            matchHint.className = 'hint-text match';
        } else {
            matchHint.textContent = '✖ Las contraseñas no coinciden';
            matchHint.className = 'hint-text mismatch';
        }
    }

    // ==========================================================================
    // 3. Verificación de contraseñas antes del submit (Experiencia de usuario)
    // ==========================================================================
    if (registerForm && pwdInput && confirmPwdInput) {
        registerForm.addEventListener('submit', (e) => {
            const val1 = pwdInput.value;
            const val2 = confirmPwdInput.value;

            // Si las contraseñas no coinciden, avisar en el cliente antes de enviar
            if (val1 !== val2) {
                e.preventDefault(); // Detiene el envío innecesario hacia el servidor

                if (clientAlert) {
                    clientAlert.innerHTML = '<strong>Aviso:</strong> Las contraseñas ingresadas no coinciden. Corrígelas antes de continuar.';
                    clientAlert.style.display = 'block';
                    confirmPwdInput.focus();
                } else {
                    alert('Las contraseñas no coinciden.');
                }
            } else {
                if (clientAlert) {
                    clientAlert.style.display = 'none';
                }
            }
        });
    }
});
