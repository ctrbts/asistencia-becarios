# en 'gestion_horarios/views.py'

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import time
from .models import Becario, Registro

from django.db.models import F, Sum, DurationField
from django.db.models.functions import Cast
from datetime import timedelta
from django.contrib.auth.decorators import login_required


def fichar(request):
    if request.method == "POST":
        legajo = request.POST.get("legajo")
        if not legajo:
            messages.error(request, "Por favor, ingrese un número de legajo.")
            return redirect("fichar")

        try:
            becario = Becario.objects.get(legajo=legajo)
        except Becario.DoesNotExist:
            messages.error(
                request, f"No se encontró un becario con el legajo {legajo}."
            )
            return redirect("fichar")

        registro_abierto = Registro.objects.filter(
            becario=becario, fecha_hora_salida__isnull=True
        ).first()
        hoy = timezone.now().date()

        if registro_abierto:
            # Escenario 1: Hay un registro abierto
            fecha_entrada_registro = registro_abierto.fecha_hora_entrada.date()

            if fecha_entrada_registro < hoy:
                # INCIDENCIA: Olvidó marcar la salida un día anterior
                # 1. Cerramos el registro antiguo a las 23:59 del día de entrada
                fin_del_dia = timezone.make_aware(
                    timezone.datetime.combine(fecha_entrada_registro, time.max)
                )
                registro_abierto.fecha_hora_salida = fin_del_dia
                registro_abierto.incidencia = True
                registro_abierto.observaciones = (
                    "Cierre automático por olvido de marcación de salida."
                )
                registro_abierto.save()

                messages.warning(
                    request,
                    f"Se detectó que no marcaste tu salida el día {fecha_entrada_registro.strftime('%d/%m/%Y')}. Se regularizó automáticamente.",
                )

                # 2. Creamos el nuevo registro de entrada para hoy
                Registro.objects.create(becario=becario)
                messages.success(
                    request,
                    f"¡Hola, {becario.nombre}! Tu nueva entrada de hoy ha sido registrada.",
                )

            else:
                # MARCACIÓN DE SALIDA NORMAL: El registro abierto es de hoy
                registro_abierto.fecha_hora_salida = timezone.now()
                registro_abierto.save()
                messages.success(
                    request,
                    f"¡Adiós, {becario.nombre}! Salida registrada a las {registro_abierto.fecha_hora_salida.strftime('%H:%M:%S')}.",
                )

        else:
            # Escenario 2: No hay registros abiertos, es una entrada normal
            Registro.objects.create(becario=becario)
            messages.success(
                request, f"¡Hola, {becario.nombre}!  Entrada registrada con éxito."
            )

        return redirect("fichar")

    # La vista para GET no cambia
    return render(request, "gestion_horarios/fichar.html")


@login_required  # Protege la vista para que solo usuarios logueados puedan acceder
def vista_reportes(request):
    # Reporte 1: Becarios activos ahora mismo
    becarios_activos = Registro.objects.filter(fecha_hora_salida__isnull=True).order_by(
        "-fecha_hora_entrada"
    )

    # Reporte 2: Horas totales por becario en un rango
    becarios_con_horas = None
    fecha_inicio_str = request.GET.get("fecha_inicio")
    fecha_fin_str = request.GET.get("fecha_fin")

    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = timezone.datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
        # Buscamos hasta el final del día de la fecha de fin
        fecha_fin = timezone.datetime.combine(
            timezone.datetime.strptime(fecha_fin_str, "%Y-%m-%d"), time.max
        )

        # Usamos el ORM de Django para hacer el cálculo en la base de datos
        becarios_con_horas = (
            Becario.objects.filter(
                registro__fecha_hora_entrada__gte=fecha_inicio,
                registro__fecha_hora_salida__lte=fecha_fin,
                registro__fecha_hora_salida__isnull=False,
            )
            .annotate(
                # Calculamos la diferencia de tiempo para cada registro
                duracion_registro=F("registro__fecha_hora_salida")
                - F("registro__fecha_hora_entrada")
            )
            .values("legajo", "nombre", "apellido")
            .annotate(
                # Sumamos todas las duraciones por becario
                horas_totales=Sum("duracion_registro")
            )
            .order_by("-horas_totales")
        )

    context = {
        "becarios_activos": becarios_activos,
        "becarios_con_horas": becarios_con_horas,
        "fecha_inicio": fecha_inicio_str,
        "fecha_fin": fecha_fin_str,
    }
    return render(request, "gestion_horarios/reportes.html", context)


@login_required
def becarios_activos_vista(request):
    """
    Esta vista muestra una lista de todos los becarios que tienen un registro
    de entrada pero no de salida (están activos).
    """
    # La consulta busca registros sin fecha_hora_salida.
    # Usamos select_related('becario') para optimizar y evitar consultas
    # adicionales a la base de datos dentro del bucle de la plantilla.
    registros_activos = (
        Registro.objects.filter(fecha_hora_salida__isnull=True)
        .select_related("becario")
        .order_by("-fecha_hora_entrada")
    )

    context = {"registros_activos": registros_activos}
    return render(request, "gestion_horarios/activos.html", context)
