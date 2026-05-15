from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (EjercicioViewSet, RutinaViewSet, SesionEntrenamientoViewSet, 
    HomeView, WorkoutView, spotify_login, spotify_callback, spotify_play, spotify_pause,
    RegisterView, CustomLoginView, logout_view, ChangePasswordView, PasswordResetView, LogEjercicioViewSet)

router = DefaultRouter()
router.register(r'ejercicios', EjercicioViewSet)
router.register(r'rutinas', RutinaViewSet)
router.register(r'sesiones', SesionEntrenamientoViewSet)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('workout/', WorkoutView.as_view(), name='workout'),
    path('spotify/login/', spotify_login, name='spotify_login'),
    path('spotify/callback/', spotify_callback, name='spotify_callback'),
    path('api/spotify/play/', spotify_play, name='spotify_play'),
    path('api/spotify/pause/', spotify_pause, name='spotify_pause'),
    path('api/', include(router.urls)),
]

router.register(r'logs', LogEjercicioViewSet)
