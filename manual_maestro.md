# Manual Maestro - Aplicación de Gimnasio PWA

Este documento centraliza el proceso de desarrollo, configuración y despliegue de la aplicación.

## Tips para trabajar en desarrollo
Para comenzar a trabajar en el entorno local y subir cambios, sigue estos pasos:
1. Activar la consola integrada de tu editor y asegúrate de estar utilizando **bash** (Git Bash o similar).
2. Activar el entorno virtual local ejecutando:
   ```powershell
   .\venv\Scripts\activate
   ```
   *(Si usas Git Bash: `source venv/Scripts/activate`)*
3. Luego, levantar o actualizar el docker local ejecutando:
   > **Nota:** Asegúrate de tener **Docker Desktop abierto y corriendo** en tu computadora antes de ejecutar este comando.
   ```bash
   docker-compose up -d --build
   ```
4. Luego, en la URL del navegador escribir: `http://localhost:8000` (o el puerto configurado) para que abra la aplicación.
5. Para subir los cambios a GitHub y que se desplieguen automáticamente en el servidor, ejecuta:
   ```bash
   git add .
   git commit -m "Descripción de los cambios"
   git push origin main
   ```

## 1. Configuración Inicial e Infraestructura
Se ha establecido la base del proyecto en la carpeta local `gim/` y se ha replicado la estructura profesional en el VPS de Contabo.

| Ítem | Valor |
|---|---|
| Carpeta raíz local | `gim/` |
| Repositorio | `https://github.com/pbolig/gim` |
| VPS Host | Contabo — `213.136.70.104` |
| Usuario SSH | `root` |
| Dominio | `accesovirtual.com.ar` (registrado en NIC.ar, DNS delegados a Contabo) |
| Subdominio | `gim.accesovirtual.com.ar` |
| Stack | Django + Gunicorn + Nginx + PostgreSQL + Docker |

## 2. Estructura de directorios y Contenedores (Docker)
El proyecto utiliza Docker para asegurar la portabilidad, evitando conflictos con otros servicios existentes en el servidor.

### Directorios en VPS (`/opt/accesovirtual/gim/`):
```
/opt/accesovirtual/gim/
├── app/        ← código fuente (repo clonado aquí)
├── backups/    ← backups de la base de datos PostgreSQL
└── logs/       ← registros de actividad del sistema
```
Creado con: `mkdir -p /opt/accesovirtual/gim/{app,backups,logs}`

### Configuración Docker (Producción):
- `docker-compose.prod.yml`: Gestiona los servicios de DB (PostgreSQL:15), Web (Django) y Nginx.
- **Puertos:** Se utilizan `8080` (HTTPS) y `8081` (HTTP) para no entrar en conflicto con el proyecto `sgh` (que ya ocupa 80/443).

## 3. Seguridad y Certificados (SSL)

### Paso 1 — Claves SSH para deploy automático
Generar el par de claves en la máquina local (Windows/PowerShell):
```powershell
ssh-keygen -t ed25519 -C "deploy-gim" -f $env:USERPROFILE\.ssh\gim_deploy
```
Instalar la clave pública en el VPS:
```powershell
type $env:USERPROFILE\.ssh\gim_deploy.pub | ssh root@213.136.70.104 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

### Paso 2 — GitHub Secrets
En `https://github.com/pbolig/gim/settings/secrets/actions` se configuraron:
- `SSH_PRIVATE_KEY`: Contenido completo de la clave privada (`gim_deploy`)
- `VPS_HOST`: `213.136.70.104`
- `VPS_USER`: `root`

### Paso 3 — Registro DNS
En el panel de Contabo se agregó el registro A para `gim` apuntando a `213.136.70.104` (TTL 3600).

### Paso 4 — Certificado SSL (Let's Encrypt)
Se usó el método `--webroot` para no interferir con `sgh`:
```bash
certbot certonly --webroot -w /opt/accesovirtual/sgh/app -d gim.accesovirtual.com.ar
```

## 4. Archivos de configuración en el VPS

### `nginx.prod.conf`
Configura el redireccionamiento HTTP a HTTPS, el proxy reverso a Gunicorn (`web:8000`), y el alias para servir `/static/`.

### `.env` (No subir al repositorio)
*Este archivo debe crearse manualmente por única vez en el VPS (`/opt/accesovirtual/gim/app/.env`) ya que no se sube a GitHub por seguridad.*
```env
POSTGRES_DB=gim
POSTGRES_USER=gim
POSTGRES_PASSWORD=tu_contraseña_segura
SECRET_KEY=tu_django_secret_key_aleatoria
DEBUG=False
ALLOWED_HOSTS=gim.accesovirtual.com.ar
```

## 5. Estrategia de Despliegue (CI/CD)
Se ha implementado un flujo de **GitHub Actions** automatizado en `.github/workflows/deploy.yml`.

### Flujo de deploy (cada push a main)
1. `git push origin main` desde la máquina local.
2. GitHub Actions detecta el push y ejecuta el workflow.
3. Se conecta al VPS por SSH usando `SSH_PRIVATE_KEY`.
4. En el VPS ejecuta:
   - `git fetch origin main` y `git reset --hard origin/main` — fuerza la bajada de los últimos cambios resolviendo conflictos.
   - `docker compose -f docker-compose.prod.yml up --build -d` — reconstruye y levanta los contenedores.
   - `docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate` — aplica migraciones pendientes.
   - `docker compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput` — recopila archivos estáticos.

**URL de Acceso en Producción:** `https://gim.accesovirtual.com.ar:8080`

## 6. Pendientes y Próximos Pasos 
- [x] Crear e Inicializar el proyecto Django en local dentro de `/gim`.
- [x] Configurar `settings.py` para leer variables de entorno del archivo `.env`.
- [x] Crear el `.env` en el VPS con los valores reales y de producción.
- [x] Verificar que el archivo `.env` esté correctamente agregado en `.gitignore`.
- [x] Hacer el primer deploy completo y verificar la url `https://gim.accesovirtual.com.ar:8080/admin/`.
- [ ] Crear el modelo de datos de Ejercicios y Rutinas (prioridad).
- [ ] Desarrollar API y el Frontend PWA (React/Vue/Vanilla).
- [ ] Integrar lógica de Spotify API y Web Speech API.
- [ ] Configurar script de backup automático de la base de datos en `/opt/accesovirtual/gim/backups/`.