#!/bin/sh
set -eu

cd /app

if [ "$(id -u)" = "0" ]; then
  install -d -m 0775 -o lunbi -g lunbi /app/chroma
  echo "Ensuring Chroma index is available..."
  python -m lunbi.scripts.download_s3_file || true
  chown -R lunbi:lunbi /app/chroma
  echo "Applying database migrations..."
  su -s /bin/sh lunbi -c "alembic upgrade head"
  echo "Starting application as lunbi: $*"
  exec su -s /bin/sh lunbi -c "$*"
fi

echo "Ensuring Chroma index is available..."
python -m lunbi.scripts.download_s3_file || true

echo "Applying database migrations..."
alembic upgrade head

echo "Starting application: $*"
exec "$@"
