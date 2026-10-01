from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Producto

# Lista de marcas disponibles según la pauta (Guías 2 y 3)
MARCAS_DISPONIBLES = ['Acuenta', 'Jumbo', 'Lider', 'Unimarc', 'Santa Isabel']


@login_required(login_url='/login/')
def mostrarIndex(request):
    """
    Vista del menú principal del CRUD.
    Recibe la petición GET autenticada y renderiza la plantilla index.html con accesos directos.
    """
    return render(request, 'productos/index.html')


@login_required(login_url='/login/')
def mostrarFormRegistrar(request):
    """
    Vista para desplegar el formulario de registro de producto.
    Recibe GET y devuelve la plantilla form_registrar.html con las opciones de marcas disponibles.
    """
    return render(request, 'productos/form_registrar.html', {
        'marcas': MARCAS_DISPONIBLES
    })


@login_required(login_url='/login/')
def insertarProducto(request):
    """
    Vista para procesar el guardado de un nuevo producto en SQLite.
    Recibe por POST txtnom, cbomar y txtpre; si son válidos guarda con Producto.objects.create y devuelve msjOk.
    """
    if request.method == 'POST':
        nombre = request.POST.get('txtnom', '').strip()
        marca = request.POST.get('cbomar', '').strip()
        precio_str = request.POST.get('txtpre', '').strip()

        # Validación de campos obligatorios
        if not nombre or not marca or not precio_str:
            return render(request, 'productos/form_registrar.html', {
                'msjErr': 'Todos los campos son obligatorios.',
                'marcas': MARCAS_DISPONIBLES,
                'prev_nom': nombre,
                'prev_mar': marca,
                'prev_pre': precio_str,
            })

        # Validación numérica y de rango para el precio
        try:
            precio = int(precio_str)
            if precio < 1 or precio > 9999999:
                raise ValueError()
        except ValueError:
            return render(request, 'productos/form_registrar.html', {
                'msjErr': 'El precio debe ser un número entero entre 1 y 9.999.999.',
                'marcas': MARCAS_DISPONIBLES,
                'prev_nom': nombre,
                'prev_mar': marca,
                'prev_pre': precio_str,
            })

        # Inserción en la base de datos SQLite mediante el ORM de Django
        Producto.objects.create(nombre=nombre, marca=marca, precio=precio)

        return render(request, 'productos/form_registrar.html', {
            'msjOk': f'Producto "{nombre}" registrado con éxito.',
            'marcas': MARCAS_DISPONIBLES
        })

    # Si se intenta acceder por GET, se redirige al formulario
    return redirect('/form_registrar/')


@login_required(login_url='/login/')
def mostrarListado(request):
    """
    Vista para mostrar todos los productos registrados.
    Consulta Producto.objects.all() y renderiza listado.html con la colección de productos.
    """
    productos = Producto.objects.all()
    return render(request, 'productos/listado.html', {
        'productos': productos
    })


@login_required(login_url='/login/')
def mostrarFormActualizar(request, id):
    """
    Vista para desplegar el formulario de edición con datos precargados.
    Recibe el id por URL, busca el producto en SQLite y renderiza form_actualizar.html.
    """
    try:
        producto = Producto.objects.get(id=id)
        return render(request, 'productos/form_actualizar.html', {
            'producto': producto,
            'marcas': MARCAS_DISPONIBLES
        })
    except Producto.DoesNotExist:
        return redirect('/listado/')


@login_required(login_url='/login/')
def actualizarProducto(request, id):
    """
    Vista para procesar la actualización de un producto existente.
    Recibe los datos editados por POST, actualiza los atributos del objeto y llama a .save().
    """
    try:
        producto = Producto.objects.get(id=id)
    except Producto.DoesNotExist:
        return redirect('/listado/')

    if request.method == 'POST':
        nombre = request.POST.get('txtnom', '').strip()
        marca = request.POST.get('cbomar', '').strip()
        precio_str = request.POST.get('txtpre', '').strip()

        if not nombre or not marca or not precio_str:
            return render(request, 'productos/form_actualizar.html', {
                'producto': producto,
                'marcas': MARCAS_DISPONIBLES,
                'msjErr': 'Todos los campos son obligatorios.'
            })

        try:
            precio = int(precio_str)
            if precio < 1 or precio > 9999999:
                raise ValueError()
        except ValueError:
            return render(request, 'productos/form_actualizar.html', {
                'producto': producto,
                'marcas': MARCAS_DISPONIBLES,
                'msjErr': 'El precio debe ser un número entero entre 1 y 9.999.999.'
            })

        # Actualizar campos y persistir cambios en SQLite
        producto.nombre = nombre
        producto.marca = marca
        producto.precio = precio
        producto.save()

        return redirect('/listado/')

    return redirect('/listado/')


@login_required(login_url='/login/')
def eliminarProducto(request, id):
    """
    Vista para eliminar un producto por su id.
    Recibe el id desde la URL, ejecuta producto.delete() en SQLite y redirige al listado.
    """
    try:
        producto = Producto.objects.get(id=id)
        producto.delete()
    except Producto.DoesNotExist:
        pass

    return redirect('/listado/')
