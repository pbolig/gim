# Manual Maestro - GIM App (Producción & Local) 🏋️‍♂️🚀

Este manual contiene toda la arquitectura, credenciales y procedimientos para mantener la aplicación funcionando en el VPS y en entorno local.

---

## 🏗️ Arquitectura del Servidor (VPS)

La aplicación corre sobre una arquitectura de **Proxy Inverso Doble**:
1.  **Nginx Maestro (Host):** Recibe el tráfico en los puertos 80/443, maneja el SSL (Certbot) y redirige al puerto `8080`.
2.  **Docker Compose:**
    *   **Nginx (Contenedor):** Escucha en el `8080` (mapeado al 80 interno), sirve archivos estáticos y pasa el tráfico a Django.
    *   **Web (Gunicorn):** Ejecuta la lógica de Django en el puerto `8000`.
    *   **DB (PostgreSQL):** Base de datos persistente.

---

## 🔑 Credenciales y Configuración Social

> [!IMPORTANT]
> Por seguridad, las claves reales NO deben subirse a GitHub. Consultar el archivo `.env` privado en el VPS o en Local.

### 🌐 Google Cloud (Login)
- **Client ID:** (Consultar en archivo .env)
- **Client Secret:** (Consultar en archivo .env)
- **Redirect URI (Prod):** `https://gim.accesovirtual.com.ar/accounts/google/login/callback/`
- **Redirect URI (Local):** `http://localhost/accounts/google/login/callback/`

### 🎵 Spotify (Música)
- **Client ID:** (Consultar en archivo .env)
- **Client Secret:** (Consultar en archivo .env)
- **Redirect URI (Prod):** `https://gim.accesovirtual.com.ar/spotify/callback/`
- **Redirect URI (Local):** `http://localhost/spotify/callback/`

---

## 🚀 Procedimientos de Despliegue

### 1. Subir cambios desde Local
En tu computadora:
```powershell
git add .
git commit -m "Descripción del cambio"
git push
```

### 2. Actualizar el VPS
En el servidor:
```bash
cd /opt/accesovirtual/gim/app
git pull
docker compose up -d --build
```

### 3. Migraciones y Base de Datos
Si cambiaste modelos en Django:
```bash
docker compose exec web python manage.py migrate
```

### 4. Crear un Superusuario (Admin)
```bash
docker compose exec web python manage.py createsuperuser
```

---

## 🛠️ Archivo .env (Producción)
Ubicación: `/opt/accesovirtual/gim/app/.env`
Debe contener obligatoriamente:
```env
DEBUG=False
SECRET_KEY=tu_clave_secreta_django
ALLOWED_HOSTS=gim.accesovirtual.com.ar,localhost,127.0.0.1
DATABASE_URL=postgres://gim:tu_pass_db@db:5432/gim
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

---

## 💡 Notas de Mantenimiento
- **Logs:** Para ver errores en vivo: `docker compose logs -f web`.
- **SSL:** Renovación automática por Certbot en el host.
- **X-Forwarded-Proto:** El Nginx de Docker está configurado para forzar `https` y que los logins sociales no fallen.

---
*Última actualización: 15 de Mayo de 2026*