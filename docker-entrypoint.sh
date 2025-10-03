#!/bin/sh
set -eu

cd /app

echo "Ensuring Chroma index is available..."
python -m lunbi.scripts.download_s3_file

echo "Applying database migrations..."
alembic upgrade head

echo "Starting application: $*"
exec "$@"
