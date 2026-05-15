import string
import random
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework import viewsets

from .models import Ejercicio, Rutina, SesionEntrenamiento, SpotifyToken, PerfilUsuario
from .serializers import EjercicioSerializer, RutinaSerializer, SesionEntrenamientoSerializer
from .spotify import get_auth_url, get_token, spotify_control

class EjercicioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer

class RutinaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rutina.objects.all()
    serializer_class = RutinaSerializer

class SesionEntrenamientoViewSet(viewsets.ModelViewSet):
    queryset = SesionEntrenamiento.objects.all()
    serializer_class = SesionEntrenamientoSerializer

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        try:
            if request.user.perfil.debe_cambiar_password:
                return redirect('/change-password/')
        except PerfilUsuario.DoesNotExist:
            PerfilUsuario.objects.create(user=request.user, debe_cambiar_password=False)
        return super().get(request, *args, **kwargs)

class WorkoutView(LoginRequiredMixin, TemplateView):
    template_name = 'workout.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        if request.user.perfil.debe_cambiar_password:
            return redirect('/change-password/')
        return super().get(request, *args, **kwargs)

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

class RegisterView(TemplateView):
    template_name = 'register.html'

    def post(self, request):
        email = request.POST.get('email')
        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'Este email ya esta registrado'}, status=400)
        
        temp_password = generate_random_password()
        user = User.objects.create_user(username=email, email=email, password=temp_password)
        PerfilUsuario.objects.create(user=user, debe_cambiar_password=True)
        
        try:
            send_mail(
                'Tu contrasena para GIM App',
                f'Hola! Tu contrasena temporal es: {temp_password}. Cambiala al ingresar.',
                'gimaccesovirtual@gmail.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({'message': 'Mail enviado con exito'})
        except Exception as e:
            return JsonResponse({'error': 'Error al enviar el mail: ' + str(e)}, status=500)

class CustomLoginView(TemplateView):
    template_name = 'login.html'

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'error': 'Credenciales invalidas'}, status=401)

class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'change_password.html'
    login_url = '/login/'

    def post(self, request):
        new_password = request.POST.get('password')
        if len(new_password) < 6:
            return JsonResponse({'error': 'La contrasena debe tener al menos 6 caracteres'}, status=400)
        
        user = request.user
        user.set_password(new_password)
        user.save()
        
        perfil = user.perfil
        perfil.debe_cambiar_password = False
        perfil.save()
        
        update_session_auth_hash(request, user) # Mantiene la sesion activa
        return JsonResponse({'status': 'ok'})

def logout_view(request):
    logout(request)
    return redirect('/login/')

def spotify_login(request):
    return redirect(get_auth_url(request.get_host()))

def spotify_callback(request):
    code = request.GET.get('code')
    if get_token(code, request.get_host(), request.user):
        return redirect('/')
    return JsonResponse({'error': 'Failed to get token'}, status=400)

def spotify_play(request):
    if spotify_control('play', request.user):
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def spotify_pause(request):
    if spotify_control('pause', request.user):
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

class PasswordResetView(TemplateView):
    template_name = 'password_reset.html'

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(username=email)
            temp_password = generate_random_password()
            user.set_password(temp_password)
            user.save()
            
            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            perfil.debe_cambiar_password = True
            perfil.save()
            
            send_mail(
                'Recuperacion de contrasena - GIM App',
                f'Hola! Tu nueva contrasena temporal es: {temp_password}. Cambiala al ingresar.',
                'gimaccesovirtual@gmail.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({'message': 'Mail enviado con exito'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'No existe un usuario con ese email'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error: ' + str(e)}, status=500)

class LogEjercicioViewSet(viewsets.ModelViewSet):
    queryset = LogEjercicio.objects.all()
    serializer_class = LogEjercicioSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
