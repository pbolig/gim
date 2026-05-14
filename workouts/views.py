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

class WorkoutView(TemplateView):
    template_name = 'workout.html'

from .spotify import get_auth_url, get_token, spotify_control
from django.shortcuts import redirect
from django.http import JsonResponse

def spotify_login(request):
    return redirect(get_auth_url(request.get_host()))

def spotify_callback(request):
    code = request.GET.get('code')
    if get_token(code, request.get_host()):
        return redirect('/')
    return JsonResponse({'error': 'Failed to get token'}, status=400)

def spotify_play(request):
    if spotify_control('play'):
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def spotify_pause(request):
    if spotify_control('pause'):
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
