FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/data

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Por si el repo se clonó en Windows con finales de línea CRLF
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh \
    && SECRET_KEY=build DATA_DIR=/tmp python manage.py collectstatic --noinput \
    && useradd --uid 10001 --no-create-home app \
    && mkdir -p /data && chown app:app /data

VOLUME /data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/', timeout=4)" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
