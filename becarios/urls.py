# Ejemplo en 'tú_proyecto/urls.py'
from django.contrib import admin
from django.urls import path
from gestion_horarios.views import fichar, vista_reportes, becarios_activos_vista, generar_reporte_pdf

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", fichar, name="fichar"),
    path("reportes/", vista_reportes, name="reportes"),
    path("activos/", becarios_activos_vista, name="activos"),
    path("reportes/pdf/", generar_reporte_pdf, name="reporte_pdf")
]
