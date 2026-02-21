#!/bin/sh
set -eu

DOMAIN="${DOMAIN:?DOMAIN environment variable is required}"
LE_CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
LE_FULLCHAIN="${LE_CERT_DIR}/fullchain.pem"
LE_PRIVKEY="${LE_CERT_DIR}/privkey.pem"
TMP_CERT_DIR="/etc/nginx/selfsigned"
TMP_FULLCHAIN="${TMP_CERT_DIR}/${DOMAIN}.crt"
TMP_PRIVKEY="${TMP_CERT_DIR}/${DOMAIN}.key"
CONF_FILE="/etc/nginx/conf.d/default.conf"

mkdir -p "${LE_CERT_DIR}" "${TMP_CERT_DIR}" /var/www/certbot

pick_cert_paths() {
  if [ -s "${LE_FULLCHAIN}" ] && [ -s "${LE_PRIVKEY}" ]; then
    SSL_CERT_PATH="${LE_FULLCHAIN}"
    SSL_KEY_PATH="${LE_PRIVKEY}"
    return
  fi

  if [ ! -s "${TMP_FULLCHAIN}" ] || [ ! -s "${TMP_PRIVKEY}" ]; then
    echo "Generating temporary self-signed certificate for ${DOMAIN}"
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
      -subj "/CN=${DOMAIN}" \
      -keyout "${TMP_PRIVKEY}" \
      -out "${TMP_FULLCHAIN}"
  fi
  SSL_CERT_PATH="${TMP_FULLCHAIN}"
  SSL_KEY_PATH="${TMP_PRIVKEY}"
}

render_nginx_conf() {
  pick_cert_paths
  export DOMAIN SSL_CERT_PATH SSL_KEY_PATH
  envsubst '${DOMAIN} ${SSL_CERT_PATH} ${SSL_KEY_PATH}' \
    < /etc/nginx/templates/default.conf.template \
    > "${CONF_FILE}"
}

render_nginx_conf

(
  while :; do
    sleep 1m
    render_nginx_conf
    nginx -s reload || true
  done
) &

exec nginx -g 'daemon off;'
