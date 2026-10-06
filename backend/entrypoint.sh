#!/bin/sh
set -e

# Arranca como root solo para dejar /data con el dueño correcto, después baja a "app"
if [ "$(id -u)" = "0" ]; then
    mkdir -p /data/media /data/backups
    chown -R app:app /data
    exec setpriv --reuid=app --regid=app --clear-groups "$0" "$@"
fi

# Si hay migraciones pendientes: backup primero, después migrar
if ! python manage.py migrate --check >/dev/null 2>&1; then
    python manage.py backup_db --motivo pre-migracion --conservar 30
    python manage.py migrate --noinput
fi

# Crea el superusuario la primera vez (si ya existe no hace nada)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py createsuperuser --noinput >/dev/null 2>&1 \
        && echo "Superusuario '$DJANGO_SUPERUSER_USERNAME' creado" || true
fi

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-1}" \
    --threads 4 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -
