from django.views.generic import TemplateView
from rest_framework import viewsets
from .models import Ejercicio, Rutina, SesionEntrenamiento
from .serializers import EjercicioSerializer, RutinaSerializer, SesionEntrenamientoSerializer

class EjercicioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer

class RutinaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rutina.objects.all()
    serializer_class = RutinaSerializer

class SesionEntrenamientoViewSet(viewsets.ModelViewSet):
    queryset = SesionEntrenamiento.objects.all()
    serializer_class = SesionEntrenamientoSerializer

class HomeView(TemplateView):
    template_name = 'index.html'
