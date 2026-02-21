# Nexus Form (Streamlit + Google Sheets)

App web para recolectar datos emparejados (Persona A / Persona B) y guardar el dataset en Google Sheets.

## Requisitos

- Python 3.10+
- Un Google Sheet compartido con una service account

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

1. Copia el ejemplo de secretos:

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

2. Edita `.streamlit/secrets.toml` con:
- `app_base_url` (opcional, para generar enlace completo).
- `spreadsheet` y `worksheet`.
- Credenciales de la service account.

## Ejecutar

```bash
streamlit run app.py
```

## Deploy self-hosted (Docker Compose + Nginx + Certbot)

### 1) Requisitos del servidor

- Docker + Docker Compose Plugin instalados.
- DNS `A` de `formulario.nbynexus.com` apuntando a la IP del servidor.
- Puertos `80` y `443` abiertos en firewall/security group.

### 2) Variables de entorno del despliegue

```bash
cp .env.example .env
```

Edita `.env`:
- `DOMAIN=formulario.nbynexus.com`
- `LETSENCRYPT_EMAIL=tu-email@dominio.com`

### 3) Secretos de Streamlit

Debes tener `.streamlit/secrets.toml` con tu conexión de Google Sheets.

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

### 4) Levantar stack completo

```bash
docker compose up -d --build
```

Servicios:
- `app`: Streamlit en `:8501` (interno).
- `nginx`: reverse proxy público `:80/:443`.
- `certbot`: emisión/renovación de TLS Let's Encrypt por `webroot`.

### 5) Verificación

```bash
docker compose logs -f certbot
docker compose logs -f nginx
```

Al inicio Nginx crea un certificado temporal autofirmado para poder arrancar. En cuanto Certbot emite el certificado real, Nginx lo toma en los reloads periódicos.

## Flujos

- URL raíz (`/`): Persona A crea `match_id`, guarda respuestas A y recibe enlace para compartir.
- URL con `?match_id=...`: Persona B completa el mismo formulario y actualiza la fila de ese `match_id`.
- Si no existe ese `match_id`, se guarda una nueva fila con datos de B (fallback).
