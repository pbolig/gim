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

from .models import Ejercicio, Rutina, SesionEntrenamiento, SpotifyToken, PerfilUsuario, LogEjercicio, EjercicioEnRutina
from .serializers import EjercicioSerializer, RutinaSerializer, SesionEntrenamientoSerializer, LogEjercicioSerializer, EjercicioEnRutinaSerializer
from .spotify import get_auth_url, get_token, spotify_control

class EjercicioViewSet(viewsets.ModelViewSet):
    serializer_class = EjercicioSerializer

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        if user.is_authenticated:
            return Ejercicio.objects.filter(Q(creado_por__isnull=True) | Q(creado_por=user))
        return Ejercicio.objects.filter(creado_por__isnull=True)

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

class RutinaViewSet(viewsets.ModelViewSet):
    serializer_class = RutinaSerializer

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        if user.is_authenticated:
            return Rutina.objects.filter(Q(es_publica=True) | Q(creado_por=user))
        return Rutina.objects.filter(es_publica=True)

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

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

class ManageRoutinesView(LoginRequiredMixin, TemplateView):
    template_name = 'manage_routines.html'
    login_url = '/login/'

class ManageExercisesView(LoginRequiredMixin, TemplateView):
    template_name = 'manage_exercises.html'
    login_url = '/login/'

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
    from .spotify import SpotifyToken, refresh_spotify_token, get_spotify_devices
    import requests
    from django.utils import timezone
    
    try:
        user_token = SpotifyToken.objects.get(user=request.user)
        if user_token.expires_at <= timezone.now():
            refresh_spotify_token(user_token)
        
        devices = get_spotify_devices(request.user)
        target_device_id = None
        if devices:
            active_device = next((d for d in devices if d['is_active']), None)
            if active_device:
                target_device_id = active_device['id']
            else:
                # Prioridad Pro: 1. Computer, 2. Smartphone, 3. El resto
                priority_device = next((d for d in devices if d['type'].lower() == 'computer'), None) or \
                                  next((d for d in devices if d['type'].lower() == 'smartphone'), None)
                
                target_device_id = priority_device['id'] if priority_device else devices[0]['id']

        url = "https://api.spotify.com/v1/me/player/play"
        if target_device_id: url += f"?device_id={target_device_id}"

        requests.put(url, headers={"Authorization": f"Bearer {user_token.access_token}"})
        return JsonResponse({'status': 'ok'})
    except:
        return JsonResponse({'status': 'error'}, status=400)

def spotify_pause(request):
    from .spotify import SpotifyToken, refresh_spotify_token, get_spotify_devices
    import requests
    from django.utils import timezone
    
    try:
        user_token = SpotifyToken.objects.get(user=request.user)
        if user_token.expires_at <= timezone.now():
            refresh_spotify_token(user_token)
            
        requests.put("https://api.spotify.com/v1/me/player/pause", 
                    headers={"Authorization": f"Bearer {user_token.access_token}"})
        return JsonResponse({'status': 'ok'})
    except:
        return JsonResponse({'status': 'error'}, status=400)

def spotify_status(request):
    from .spotify import get_spotify_status
    from .models import SpotifyToken
    
    is_connected = SpotifyToken.objects.filter(user=request.user).exists()
    status = get_spotify_status(request.user)
    
    if status:
        item = status.get('item', {})
        return JsonResponse({
            'is_connected': True,
            'is_playing': status.get('is_playing'),
            'track_name': item.get('name'),
            'artist_name': item.get('artists', [{}])[0].get('name'),
            'device_name': status.get('device', {}).get('name')
        })
    
    return JsonResponse({
        'is_connected': is_connected,
        'is_playing': False
    })

def spotify_playlists(request):
    from .spotify import get_user_playlists
    playlists = get_user_playlists(request.user)
    return JsonResponse({'playlists': playlists})

def spotify_play_playlist(request, playlist_uri):
    from .spotify import SpotifyToken, refresh_spotify_token, get_spotify_devices
    import requests
    from django.utils import timezone
    
    try:
        user_token = SpotifyToken.objects.get(user=request.user)
        if user_token.expires_at <= timezone.now():
            refresh_spotify_token(user_token)
            
        # Paso PRO: Buscar dispositivos si no hay uno activo
        devices = get_spotify_devices(request.user)
        target_device_id = None
        
        if devices:
            active_device = next((d for d in devices if d['is_active']), None)
            if active_device:
                target_device_id = active_device['id']
            else:
                # Prioridad Pro: 1. Computer, 2. Smartphone, 3. El resto
                priority_device = next((d for d in devices if d['type'].lower() == 'computer'), None) or \
                                  next((d for d in devices if d['type'].lower() == 'smartphone'), None)
                
                target_device_id = priority_device['id'] if priority_device else devices[0]['id']

        url = "https://api.spotify.com/v1/me/player/play"
        if target_device_id:
            url += f"?device_id={target_device_id}"

        response = requests.put(
            url,
            json={"context_uri": playlist_uri},
            headers={"Authorization": f"Bearer {user_token.access_token}"}
        )
        return JsonResponse({'status': 'ok' if response.status_code in [204, 202] else 'error'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

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

class EjercicioEnRutinaViewSet(viewsets.ModelViewSet):
    serializer_class = EjercicioEnRutinaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return EjercicioEnRutina.objects.filter(rutina__creado_por=user)
        return EjercicioEnRutina.objects.none()
