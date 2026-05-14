# Setup de Deploy Automático — Proyecto GIM

Documentación del proceso de configuración de CI/CD para el proyecto `gim` sobre el VPS de Contabo, siguiendo la misma estructura del proyecto `sgh` existente.

---

## Infraestructura

| Ítem | Valor |
|---|---|
| VPS | Contabo — `213.136.70.104` |
| Usuario SSH | `root` |
| Dominio | `accesovirtual.com.ar` (registrado en NIC.ar, DNS delegados a Contabo) |
| Subdominio | `gim.accesovirtual.com.ar` |
| Repositorio | `https://github.com/pbolig/gim` |
| Stack | Django + Gunicorn + Nginx + PostgreSQL + Docker |

---

## Estructura de directorios en el VPS

```
/opt/accesovirtual/
├── sgh/
│   ├── app/        ← código fuente
│   ├── backups/    ← backups de la base de datos
│   └── logs/
└── gim/
    ├── app/        ← código fuente (repo clonado aquí)
    ├── backups/    ← backups de la base de datos
    └── logs/
```

Creado con:
```bash
mkdir -p /opt/accesovirtual/gim/{app,backups,logs}
```

---

## Paso 1 — Claves SSH para deploy automático

### En la máquina local (Windows/PowerShell)

Generar el par de claves:
```powershell
ssh-keygen -t ed25519 -C "deploy-gim" -f $env:USERPROFILE\.ssh\gim_deploy
```

Archivos generados:
- `C:\Users\Pedro.Bolig\.ssh\gim_deploy` → clave privada (va a GitHub Secrets)
- `C:\Users\Pedro.Bolig\.ssh\gim_deploy.pub` → clave pública (va al VPS)

### Instalar la clave pública en el VPS

Desde PowerShell (reemplazo de `ssh-copy-id` para Windows):
```powershell
type $env:USERPROFILE\.ssh\gim_deploy.pub | ssh root@213.136.70.104 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Verificar conexión sin contraseña:
```powershell
ssh -i $env:USERPROFILE\.ssh\gim_deploy root@213.136.70.104
```

---

## Paso 2 — GitHub Secrets

En `https://github.com/pbolig/gim/settings/secrets/actions` se configuraron los siguientes secretos:

| Nombre | Valor |
|---|---|
| `SSH_PRIVATE_KEY` | Contenido completo del archivo `gim_deploy` (clave privada) |
| `VPS_HOST` | `213.136.70.104` |
| `VPS_USER` | `root` |

Para copiar la clave privada al portapapeles:
```powershell
Get-Content $env:USERPROFILE\.ssh\gim_deploy | clip
```

---

## Paso 3 — Registro DNS

En el panel de Contabo (`https://my.contabo.com` → DNS Zones → `accesovirtual.com.ar`) se agregó:

| Campo | Valor |
|---|---|
| Tipo | A |
| Nombre | `gim` |
| Datos | `213.136.70.104` |
| TTL | `3600` |

Verificar propagación desde el VPS:
```bash
dig gim.accesovirtual.com.ar +short
# Debe devolver: 213.136.70.104
```

---

## Paso 4 — Certificado SSL (Let's Encrypt)

El puerto 80 estaba ocupado por el nginx de `sgh`, por lo que se usó el método `--webroot`:

```bash
certbot certonly --webroot -w /opt/accesovirtual/sgh/app -d gim.accesovirtual.com.ar
```

Certificados generados en:
- `/etc/letsencrypt/live/gim.accesovirtual.com.ar/fullchain.pem`
- `/etc/letsencrypt/live/gim.accesovirtual.com.ar/privkey.pem`

Vencimiento: `2026-08-11` (renovación automática configurada por certbot).

---

## Paso 5 — Archivos de configuración en el VPS

### `/opt/accesovirtual/gim/app/nginx.prod.conf`

```nginx
server {
    listen 80;
    server_name gim.accesovirtual.com.ar;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name gim.accesovirtual.com.ar;

    ssl_certificate /etc/letsencrypt/live/gim.accesovirtual.com.ar/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gim.accesovirtual.com.ar/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    underscores_in_headers on;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /static/;
    }
}
```

### `/opt/accesovirtual/gim/app/docker-compose.prod.yml`

```yaml
services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file: .env
    restart: always

  web:
    build: .
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/code
      - static_volume:/static
    depends_on:
      - db
    env_file: .env
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "8080:443"
      - "8081:80"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - static_volume:/static
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  static_volume:
```

> Los puertos `8080/8081` evitan conflicto con `sgh` que ya ocupa `80/443`.

### `/opt/accesovirtual/gim/app/.env`

```env
POSTGRES_DB=gim
POSTGRES_USER=gim
POSTGRES_PASSWORD=password_segura
SECRET_KEY=tu_django_secret_key
DEBUG=False
ALLOWED_HOSTS=gim.accesovirtual.com.ar
```

> ⚠️ Este archivo **no debe subirse al repositorio**. Verificar que `.gitignore` lo incluya.

---

## Paso 6 — Workflow de GitHub Actions

Archivo: `.github/workflows/deploy.yml` en el repositorio.

```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Configurar SSH
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Agregar VPS a known_hosts
        run: ssh-keyscan -H ${{ secrets.VPS_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy
        run: |
          ssh ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} << 'EOF'
            cd /opt/accesovirtual/gim/app
            git pull origin main
            docker-compose -f docker-compose.prod.yml up --build -d
            docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate
            docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
          EOF
```

---

## Flujo de deploy (cada push a main)

1. `git push origin main` desde la máquina local
2. GitHub Actions detecta el push y ejecuta el workflow
3. Se conecta al VPS por SSH usando `SSH_PRIVATE_KEY`
4. En el VPS ejecuta:
   - `git pull origin main` — baja los cambios
   - `docker-compose up --build -d` — reconstruye y levanta los contenedores
   - `python manage.py migrate` — aplica migraciones pendientes
   - `python manage.py collectstatic` — recopila archivos estáticos

---

## Pendiente

- [ ] Crear el proyecto Django en la máquina local dentro de `/gim`
- [ ] Configurar `settings.py` para leer variables del `.env`
- [ ] Crear el `.env` en el VPS con los valores reales
- [ ] Verificar que `.env` esté en `.gitignore`
- [ ] Hacer el primer deploy completo y verificar `https://gim.accesovirtual.com.ar`
- [ ] Configurar script de backup de la base de datos en `/opt/accesovirtual/gim/backups/`
