#!/bin/sh
set -eu

DOMAIN="${DOMAIN:?DOMAIN environment variable is required}"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
FULLCHAIN="${CERT_DIR}/fullchain.pem"
PRIVKEY="${CERT_DIR}/privkey.pem"

mkdir -p "${CERT_DIR}" /var/www/certbot

if [ ! -s "${FULLCHAIN}" ] || [ ! -s "${PRIVKEY}" ]; then
  echo "Generating temporary self-signed certificate for ${DOMAIN}"
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -subj "/CN=${DOMAIN}" \
    -keyout "${PRIVKEY}" \
    -out "${FULLCHAIN}"
fi

envsubst '${DOMAIN}' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf

(
  while :; do
    sleep 6h
    nginx -s reload || true
  done
) &

exec nginx -g 'daemon off;'
