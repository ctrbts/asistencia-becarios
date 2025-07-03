# en 'gestion_horarios/admin.py'
from django.contrib import admin
from .models import Becario, Registro


@admin.register(Becario)
class BecarioAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "legajo", "dni")  # Añadido legajo
    search_fields = ("apellido", "nombre", "legajo", "dni")


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = (
        "becario",
        "fecha_hora_entrada",
        "fecha_hora_salida",
        "incidencia",
    )  # Añadido incidencia
    list_filter = ("incidencia", "becario", "fecha_hora_entrada")
    readonly_fields = ("fecha_hora_entrada", "fecha_hora_salida")
    # Para poder filtrar por fecha de forma más cómoda
    date_hierarchy = "fecha_hora_entrada"
