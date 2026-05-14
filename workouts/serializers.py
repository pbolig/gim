from rest_framework import serializers
from .models import Ejercicio, Rutina, EjercicioEnRutina, SesionEntrenamiento

class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = '__all__'

class EjercicioEnRutinaSerializer(serializers.ModelSerializer):
    ejercicio = EjercicioSerializer(read_only=True)
    
    class Meta:
        model = EjercicioEnRutina
        fields = ['id', 'ejercicio', 'series', 'repeticiones', 'orden']

class RutinaSerializer(serializers.ModelSerializer):
    ejercicios = EjercicioEnRutinaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Rutina
        fields = ['id', 'nombre', 'creada_en', 'ejercicios']

class SesionEntrenamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SesionEntrenamiento
        fields = '__all__'
