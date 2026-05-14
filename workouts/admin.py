from django.contrib import admin

from .models import Ejercicio, Rutina, EjercicioEnRutina, SesionEntrenamiento

class EjercicioEnRutinaInline(admin.TabularInline):
    model = EjercicioEnRutina
    extra = 1

@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    inlines = [EjercicioEnRutinaInline]
    list_display = ('nombre', 'creada_en')

@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'musculos_trabajados')
    search_fields = ('nombre', 'musculos_trabajados')

@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('rutina', 'fecha')
