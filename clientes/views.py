from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClientesForm, RefistroForm
from .forms import Cliente
# pip install reportlab
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
import datetime
from django.db.models import Q

# Create your views here.


@login_required
def create_clientes(request):
    if request.method == 'POST':
        form = ClientesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('cliente_list')
    else:
        form = ClientesForm()
    return render(request, 'clientes/cliente_form.html', {'form': form})


def cliente_list(request):
    query = request.GET.get("q")
    if query:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(apellidos__icontains=query)
        )
    else:
        clientes = Cliente.objects.all()
    return render(request, 'clientes/clientes_list.html', {'clientes': clientes})


@login_required
def update_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClientesForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('cliente_list')
    else:
        form = ClientesForm(instance=cliente)
    return render(request, 'clientes/cliente_form.html', {'form': form, 'cliente': cliente})


@login_required
def delete_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('cliente_list')
    return render(request, 'clientes/cliente_confirm_delete.html', {'cliente': cliente})


def generar_pdf_cliente(request):
    response = HttpResponse(content_type='application/pdf')
    # abrir = inline; descargar = attachment
    response['Content-Disposition'] = 'inline; filename = "clientes.pdf"'
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle("Reporte de clientes")

    width, height = letter

    #
    # Generacion de pie de pagina
    fecha_generacion = datetime.date.today().strftime("%d-%m-%Y")
    pagina_num = 1

    def agregar_pie_pagina(pdf, pagina_num):
        pdf.setFont("Helvetica", 10)
        pdf.drawString(30, 20, f"Fecha de generación: {fecha_generacion}")
        pdf.drawString(width - 100, 20, f"Página num. {pagina_num}")

    # Agregar imagen al pdf (icono)
    # Ruta de la imagen
    ruta_imagen = "C:/Users/josel/OneDrive/Documentos/ISC/Planificacion_de_bodas/Proyectos/crud_clientesjlth/clientes/static/clientes/iconos/clients.png"
    ruta_imagen2 = "C:/Users/josel/OneDrive/Documentos/ISC/Planificacion_de_bodas/Proyectos/crud_clientesjlth/clientes/static/clientes/iconos/anillos.png"

    # Posicion de la imagen
    pdf.drawImage(ruta_imagen, 235, height - 50, 35, 35)
    pdf.drawImage(ruta_imagen2, 550, height - 50, 40, 40)
    # FIN DE IMAGEN

    pdf.setFont("Helvetica-Bold", 16)
    texto = "Lista de Clientes"
    ancho_texto = pdf.stringWidth(texto)
    x = (width - ancho_texto) / 2
    pdf.drawString(100, height - 40, texto)

    # Encabezado de la tabla
    encabezados = ["Nombre", "Apellidos", "Fecha de nac."]
    x_inicial = 100
    y = height - 80

    pdf.setFont("Helvetica-Bold", 12)
    for i, encabezado in enumerate(encabezados):
        pdf.drawString(x_inicial + i * 150, y, encabezado)

    y -= 10
    pdf.line(100, y, width - 100, y)

    y -= 20
    query = request.GET.get("q")
    if query:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(apellidos__icontains=query)
        )
    else:
        clientes = Cliente.objects.all()
    pdf.setFont("Helvetica-Bold", 12)
    for cliente in clientes:
        pdf.drawString(100, y, cliente.nombre)
        pdf.drawString(250, y, cliente.apellidos)
        pdf.drawString(400, y, cliente.fecha_nac.strftime("%d-%m-%Y"))

        y -= 20

        if y <= 50:
            agregar_pie_pagina(pdf, pagina_num)
            pdf.showPage()
            pdf.setFont()
            y = height - 80
            for i, encabezado in enumerate(encabezados):
                pdf.drawString(x_inicial + 1 * 150, y, encabezado)
                y -= 20
            pagina_num += 1
    agregar_pie_pagina(pdf, pagina_num)

    pdf.showPage()
    pdf.save()

    return response


def register(request):
    if request.method == 'POST':
        form = RefistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RefistroForm()
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
