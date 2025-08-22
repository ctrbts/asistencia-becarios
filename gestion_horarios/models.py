# en 'gestion_horarios/models.py'

from django.db import models
from django.utils import timezone


class Becario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    # El legajo será el identificador principal para fichar
    legajo = models.CharField(
        max_length=20, unique=True, help_text="Número de legajo único del becario."
    )
    dni = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (Legajo: {self.legajo})"


class Registro(models.Model):
    becario = models.ForeignKey(Becario, on_delete=models.CASCADE)
    fecha_hora_entrada = models.DateTimeField(default=timezone.now)
    fecha_hora_salida = models.DateTimeField(null=True, blank=True)
    # Nuevos campos para el control de incidencias
    incidencia = models.BooleanField(
        default=False,
        help_text="Marcar si el registro tuvo un cierre automático o irregular.",
    )
    observaciones = models.TextField(
        blank=True, null=True, help_text="Detalles sobre la incidencia."
    )

    @property
    def duracion(self):
        if self.fecha_hora_salida:
            return self.fecha_hora_salida - self.fecha_hora_entrada
        return None

    def __str__(self):
        return f"{self.becario} - Entrada: {self.fecha_hora_entrada.strftime('%Y-%m-%d %H:%M')}"
