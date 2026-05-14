import environ
import os
from pathlib import Path

env = environ.Env(
    DEBUG=(bool, False) # Valor por defecto
)

BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = 'core.urls'

# Leer el archivo .env si existe
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Configuración de base de datos dinámica
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3')
}

# Configuración de Archivos Estáticos (Vital para Nginx)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',         # <--- ESTA ES LA QUE FALTA PARA EL SUPERUSER
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tus aplicaciones
    'workouts',
]

# core/settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Requerido para admin
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Requerido para admin
    'django.contrib.messages.middleware.MessageMiddleware',      # Requerido para admin
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Para eliminar los WARNINGS de las IDs de los modelos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Confiar en el puerto local de desarrollo
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8001',
    'http://127.0.0.1:8001',
    'https://gim.accesovirtual.com.ar', # Ya lo dejamos listo para el VPS
]

# Asegurar que Django entienda que viene detrás de un proxy (Nginx)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')