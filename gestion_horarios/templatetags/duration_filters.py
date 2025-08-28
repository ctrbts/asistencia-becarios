# en gestion_horarios/templatetags/duration_filters.py

from django import template

register = template.Library()


@register.filter
def format_duration(timedelta_obj):
    """
    Formatea un objeto timedelta a una cadena de texto HH:mm.
    """
    if timedelta_obj is None:
        return "N/A"

    # Extraemos el total de segundos del timedelta
    total_seconds = int(timedelta_obj.total_seconds())

    # Calculamos horas y minutos
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    # Devolvemos la cadena formateada, asegurando dos dígitos para los minutos
    return f"{hours:02d}:{minutes:02d}"
