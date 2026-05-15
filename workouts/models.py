from django.db import models
from django.contrib.auth.models import User

class Ejercicio(models.Model):
    TIPO_CHOICES = [
        ('FUERZA', 'Fuerza (Reps/Peso)'),
        ('CARDIO', 'Cardio (Tiempo/Distancia)'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tecnica = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="Link a GIF o Video de YouTube")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='FUERZA')
    categoria = models.CharField(max_length=50) # Ej: Pecho, Espalda, HIIT
    musculos_principales = models.CharField(max_length=200, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='ejercicios_creados')
    
    def __str__(self):
        return self.nombre

class Rutina(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    ejercicios = models.ManyToManyField(Ejercicio, through='EjercicioEnRutina')
    creada_en = models.DateTimeField(auto_now_add=True)
    es_publica = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre

class EjercicioEnRutina(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.IntegerField(default=3)
    repeticiones = models.IntegerField(default=12)
    peso_sugerido = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descanso_segundos = models.IntegerField(default=60)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

class SesionEntrenamiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    completada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.rutina.nombre} - {self.fecha_inicio.strftime('%Y-%m-%d %H:%M')}"

class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='spotify_token')
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    debe_cambiar_password = models.BooleanField(default=True)
    
    # Datos Fisicos
    fecha_nacimiento = models.DateField(null=True, blank=True)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura_cm = models.IntegerField(null=True, blank=True)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], blank=True)
    
    def __str__(self):
        return self.user.username

class LogEjercicio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    
    # Lo que realmente hizo el usuario
    series_completadas = models.IntegerField()
    repeticiones_reales = models.IntegerField(null=True, blank=True)
    peso_utilizado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tiempo_esfuerzo_segundos = models.IntegerField(default=0)
    tiempo_descanso_segundos = models.IntegerField(default=0)
    calorias_estimadas = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.ejercicio.nombre} - {self.fecha.date()}"
