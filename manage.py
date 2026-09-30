#!/usr/bin/env python

import os
import sys


def main():
    """Ejecuta tareas administrativas y comandos del proyecto."""
    # Le indica a Django dónde está el archivo settings.py que debe leer
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        # Importa la función de Django que interpreta los comandos de consola
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está activado tu entorno virtual?"
        ) from exc
    # sys.argv contiene lo que escribimos en la terminal (ej: ['manage.py', 'runserver'])
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
