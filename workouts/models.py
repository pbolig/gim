from django.db import models

class Ejercicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion_tecnica = models.TextField(help_text="Consejo para la técnica correcta")
    imagen_gif = models.URLField(blank=True, help_text="URL del GIF o imagen ilustrativa")
    musculos_trabajados = models.CharField(max_length=200, help_text="Ej: Pecho, Tríceps")
    
    def __str__(self):
        return self.nombre

class Rutina(models.Model):
    nombre = models.CharField(max_length=100)
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class EjercicioEnRutina(models.Model):
    rutina = models.ForeignKey(Rutina, related_name='ejercicios', on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.PositiveIntegerField(default=3)
    repeticiones = models.PositiveIntegerField(default=12)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']