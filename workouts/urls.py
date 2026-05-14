from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EjercicioViewSet, RutinaViewSet, SesionEntrenamientoViewSet, HomeView

router = DefaultRouter()
router.register(r'ejercicios', EjercicioViewSet)
router.register(r'rutinas', RutinaViewSet)
router.register(r'sesiones', SesionEntrenamientoViewSet)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/', include(router.urls)),
]
