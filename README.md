# Formulario Nexus

Esta app sirve para recoger respuestas de convivencia entre dos personas y guardarlas en Google Sheets.

La dinámica es simple:
- Una persona entra al formulario, lo completa y recibe un link.
- Le pasa ese link a su ex-compañero.
- La segunda persona responde y queda todo emparejado por `match_id`.

## Arranque rápido (local)

Necesitas Python 3.10+.

1. Instala dependencias:

```bash
pip install -r requirements.txt
```

2. Prepara secretos:

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

3. Edita `.streamlit/secrets.toml` con:
- Tu Google Sheet (`spreadsheet` y `worksheet`).
- Las credenciales de la service account.

4. Lanza la app:

```bash
streamlit run app.py
```

## Publicarlo en servidor (Cloudflare Flexible)

Este repo ya trae `docker-compose` con Streamlit + Nginx.

1. Crea el archivo de entorno:

```bash
cp .env.example .env
```

2. En `.env`, pon tu dominio:
- `DOMAIN=formulario.nbynexus.com`

3. Asegúrate de tener `.streamlit/secrets.toml` bien configurado.

4. Levanta todo:

```bash
docker compose up -d --build
```

5. En Cloudflare:
- Activa proxy (nube naranja) en el DNS del subdominio.
- SSL/TLS mode en `Flexible`.

Si quieres revisar que Nginx está vivo:

```bash
docker compose logs -f nginx
```
