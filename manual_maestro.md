# Manual Maestro - Aplicación de Gimnasio PWA

Este documento centraliza el proceso de desarrollo, configuración y despliegue de la aplicación.

## 1. Configuración Inicial del Proyecto
Se ha creado la estructura base del proyecto para alojar el código del backend, frontend y configuración de infraestructura.

- **Carpeta raíz:** `gim/`
- **Estado:** Inicializado.

## 2. Estructura de Contenedores (Docker)
El proyecto utiliza Docker para asegurar la portabilidad y facilidad de despliegue en el VPS.

### Archivos creados:
- `docker-compose.yml`: Gestiona los servicios de Base de Datos (PostgreSQL), Backend (Django) y Servidor Web (Nginx).

## 3. Control de Versiones (GitHub)
Para mantener el código seguro y facilitar el despliegue automático:
1. Se inicializó un repositorio local Git.
2. Se vinculará con un repositorio en GitHub.

## 4. Estrategia de Despliegue (CI/CD)
Se implementará **GitHub Actions** para que cada vez que se realice un `git push` a la rama principal:
1. GitHub se conecte al VPS vía SSH.
2. Ejecute un `git pull`.
3. Reconstruya los contenedores mediante `docker-compose up --build -d`.

## Próximos Pasos Registrados:
- Configurar el `Dockerfile` para la aplicación Django.
- Definir el modelo de datos de Ejercicios y Rutinas.
- Integrar la lógica de Spotify API.