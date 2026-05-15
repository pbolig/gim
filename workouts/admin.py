from django.contrib import admin
from .models import Ejercicio, Rutina, EjercicioEnRutina, SesionEntrenamiento, LogEjercicio, PerfilUsuario

class EjercicioEnRutinaInline(admin.TabularInline):
    model = EjercicioEnRutina
    extra = 1

@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    inlines = [EjercicioEnRutinaInline]
    list_display = ('nombre', 'creada_en')

@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'categoria', 'musculos_principales')
    search_fields = ('nombre', 'musculos_principales')

@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('rutina', 'usuario', 'fecha_inicio', 'completada')

@admin.register(LogEjercicio)
class LogEjercicioAdmin(admin.ModelAdmin):
    list_display = ('ejercicio', 'user', 'fecha', 'peso_utilizado')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'peso_kg', 'altura_cm')
