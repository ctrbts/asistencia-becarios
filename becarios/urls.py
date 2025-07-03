# Ejemplo en 'tú_proyecto/urls.py'
from django.contrib import admin
from django.urls import path, include
from gestion_horarios.views import fichar, vista_reportes, becarios_activos_vista

# --- Personalización de los títulos del Admin ---
""" admin.site.site_header = "Administración del Sistema de Asistencia"
admin.site.site_title = "Portal de Administración - [Nombre de tu Institución]"
admin.site.index_title = "Bienvenido al Portal de Gestión de Becarios" """

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", fichar, name="fichar"),
    path("reportes/", vista_reportes, name="reportes"),
    path("activos/", becarios_activos_vista, name="activos"),
]
