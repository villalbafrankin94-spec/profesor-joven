from django.db import models

# Create your models here.
class Entrenamiento(models.Model):
    jugador_id = models.CharField(max_length=100)
    fecha = models.DateField()
    tipo = models.CharField(max_length=100)
    duracion_minutos = models.IntegerField()
    intensidad = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Entrenamiento {self.jugador_id} - {self.fecha}"