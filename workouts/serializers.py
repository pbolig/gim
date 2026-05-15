from rest_framework import serializers
from .models import Ejercicio, Rutina, EjercicioEnRutina, SesionEntrenamiento, LogEjercicio, PerfilUsuario

class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = '__all__'

class EjercicioEnRutinaSerializer(serializers.ModelSerializer):
    ejercicio = EjercicioSerializer(read_only=True)
    
    class Meta:
        model = EjercicioEnRutina
        fields = ['id', 'ejercicio', 'series', 'repeticiones', 'peso_sugerido', 'descanso_segundos', 'orden']

class RutinaSerializer(serializers.ModelSerializer):
    ejercicios = EjercicioEnRutinaSerializer(source='ejercicioenrutina_set', many=True, read_only=True)
    
    class Meta:
        model = Rutina
        fields = ['id', 'nombre', 'descripcion', 'creada_en', 'ejercicios']

class SesionEntrenamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SesionEntrenamiento
        fields = '__all__'

class LogEjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEjercicio
        fields = '__all__'

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = '__all__'
