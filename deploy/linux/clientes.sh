#!/usr/bin/env bash
# =============================================================================
#  BACKEND-GLOBAL - gestor de instalaciones por cliente (Linux + Docker)
#
#  Una sola imagen Docker del backend, un contenedor por cliente.
#  Cada cliente tiene su carpeta en $CLIENTES_DIR/<nombre> con:
#     .env                -> configuración propia (SECRET_KEY, puerto, dominio...)
#     docker-compose.yml  -> generado automáticamente
#     data/               -> db.sqlite3, media/, backups/   (lo único a respaldar)
#
#  Uso:  sudo ./clientes.sh <comando> [opciones]      (./clientes.sh ayuda)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CLIENTES_DIR="${CLIENTES_DIR:-/opt/clientes-backend}"
IMAGEN="${IMAGEN:-backend-global:latest}"
PUERTO_INICIAL="${PUERTO_INICIAL:-8001}"
RED_TRAEFIK="traefik"

verde()  { printf '\033[32m✔ %s\033[0m\n' "$*"; }
info()   { printf '\033[36m→ %s\033[0m\n' "$*"; }
aviso()  { printf '\033[33m! %s\033[0m\n' "$*"; }
error()  { printf '\033[31m✘ %s\033[0m\n' "$*" >&2; exit 1; }

aleatorio() { LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom 2>/dev/null | head -c "$1" || true; }

leer_env() { # leer_env <archivo> <VARIABLE>
    grep -E "^$2=" "$1" 2>/dev/null | head -n1 | cut -d= -f2- || true
}

requiere_docker() {
    command -v docker >/dev/null || error "Docker no está instalado. Ejecutá: sudo $0 instalar"
    docker info >/dev/null 2>&1 || error "No se puede usar Docker. Ejecutá el script con sudo."
}

requiere_cliente() {
    [ -n "${1:-}" ] || error "Falta el nombre del cliente"
    [ -f "$CLIENTES_DIR/$1/.env" ] || error "No existe el cliente '$1' en $CLIENTES_DIR"
}

ip_local() { hostname -I 2>/dev/null | awk '{print $1}'; }

puerto_ocupado() {
    local p="$1"
    grep -qsE "^PUERTO=$p$" "$CLIENTES_DIR"/*/.env && return 0
    if command -v ss >/dev/null; then
        ss -ltnH 2>/dev/null | awk '{print $4}' | grep -qE "[:.]$p$" && return 0
    fi
    return 1
}

siguiente_puerto() {
    local p="$PUERTO_INICIAL"
    while puerto_ocupado "$p"; do p=$((p + 1)); done
    echo "$p"
}

esperar_respuesta() { # esperar_respuesta <puerto>
    command -v curl >/dev/null || { aviso "curl no instalado, no se verifica el arranque"; return 0; }
    for _ in $(seq 1 60); do
        curl -fsS -o /dev/null "http://127.0.0.1:$1/health/" 2>/dev/null && return 0
        sleep 2
    done
    return 1
}

# -----------------------------------------------------------------------------
generar_compose() { # generar_compose <nombre>
    local nombre="$1" dir="$CLIENTES_DIR/$1"
    local puerto dominio
    puerto="$(leer_env "$dir/.env" PUERTO)"
    dominio="$(leer_env "$dir/.env" DOMINIO)"

    {
        echo "# Generado por clientes.sh - no editar a mano (usar el .env)"
        echo "name: backend-$nombre"
        echo "services:"
        echo "  web:"
        echo "    image: $IMAGEN"
        echo "    container_name: backend-$nombre"
        echo "    restart: unless-stopped"
        echo "    env_file: .env"
        echo "    environment:"
        echo "      DATA_DIR: /data"
        echo "    volumes:"
        echo "      - ./data:/data"
        echo "    logging:"
        echo "      driver: json-file"
        echo "      options: { max-size: \"10m\", max-file: \"3\" }"
        if [ -z "$dominio" ]; then
            # Modo puerto: accesible en http://IP:PUERTO
            echo "    ports:"
            echo "      - \"$puerto:8000\""
        else
            # Modo dominio: Traefik enruta por nombre; el puerto queda solo local
            echo "    ports:"
            echo "      - \"127.0.0.1:$puerto:8000\""
            echo "    labels:"
            echo "      - traefik.enable=true"
            echo "      - traefik.docker.network=$RED_TRAEFIK"
            echo "      - traefik.http.routers.backend-$nombre.rule=Host(\`$dominio\`)"
            echo "      - traefik.http.routers.backend-$nombre.entrypoints=websecure"
            echo "      - traefik.http.routers.backend-$nombre.tls.certresolver=le"
            echo "      - traefik.http.services.backend-$nombre.loadbalancer.server.port=8000"
            echo "    networks: [default, $RED_TRAEFIK]"
            echo "networks:"
            echo "  $RED_TRAEFIK:"
            echo "    external: true"
        fi
    } > "$dir/docker-compose.yml"
}

# -----------------------------------------------------------------------------
cmd_instalar() {
    if ! command -v docker >/dev/null; then
        [ "$(id -u)" = "0" ] || error "Para instalar Docker ejecutá con sudo"
        info "Instalando Docker (script oficial get.docker.com)..."
        curl -fsSL https://get.docker.com | sh
        systemctl enable --now docker
    fi
    requiere_docker
    docker compose version >/dev/null 2>&1 || error "Falta el plugin 'docker compose'"
    verde "Docker OK: $(docker --version)"

    mkdir -p "$CLIENTES_DIR"
    verde "Carpeta de clientes: $CLIENTES_DIR"

    cmd_construir
    echo
    verde "Listo. Creá el primer cliente con:  sudo $0 crear <nombre>"
}

cmd_construir() {
    requiere_docker
    info "Construyendo imagen $IMAGEN desde $REPO_DIR/backend ..."
    docker build -t "$IMAGEN" "$REPO_DIR/backend"
    verde "Imagen construida"
}

cmd_crear() {
    local nombre="${1:-}"; shift || true
    local puerto="" dominio="" db="" cors=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --puerto)  puerto="$2"; shift 2 ;;
            --dominio) dominio="$2"; shift 2 ;;
            --base)    db="$2"; shift 2 ;;
            --cors)    cors="$2"; shift 2 ;;
            *) error "Opción desconocida: $1" ;;
        esac
    done

    [[ "$nombre" =~ ^[a-z0-9][a-z0-9-]{1,40}$ ]] \
        || error "Nombre inválido. Usar minúsculas, números y guiones (ej: centro-motos)"
    requiere_docker
    docker image inspect "$IMAGEN" >/dev/null 2>&1 || cmd_construir

    local dir="$CLIENTES_DIR/$nombre"
    [ -e "$dir" ] && error "Ya existe $dir"
    [ -z "$db" ] || [ -f "$db" ] || error "No existe el archivo de base $db"

    if [ -z "$puerto" ]; then
        puerto="$(siguiente_puerto)"
    elif puerto_ocupado "$puerto"; then
        error "El puerto $puerto ya está en uso"
    fi

    if [ -n "$dominio" ] && ! docker network inspect "$RED_TRAEFIK" >/dev/null 2>&1; then
        error "Para usar --dominio primero instalá Traefik:  sudo $0 traefik <email>"
    fi

    mkdir -p "$dir/data"
    verde "Carpeta creada: $dir"

    local hosts="*" csrf="" proxy="False"
    if [ -n "$dominio" ]; then
        hosts="$dominio"; csrf="https://$dominio"; proxy="True"
    fi
    local admin_pass; admin_pass="$(aleatorio 16)"

    cat > "$dir/.env" <<EOF
# Cliente: $nombre  (creado $(date '+%Y-%m-%d %H:%M'))
PUERTO=$puerto
DOMINIO=$dominio

SECRET_KEY=$(aleatorio 60)
DEBUG=False
ALLOWED_HOSTS=$hosts
CSRF_TRUSTED_ORIGINS=$csrf
BEHIND_HTTPS_PROXY=$proxy
CORS_ALLOWED_ORIGINS=$cors
API_SYNC_KEY=$(aleatorio 40)

GUNICORN_WORKERS=1

# Superusuario inicial del admin (solo se usa la primera vez)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@localhost
DJANGO_SUPERUSER_PASSWORD=$admin_pass
EOF
    chmod 600 "$dir/.env"
    verde "Configuración generada (SECRET_KEY propia, puerto $puerto)"

    if [ -n "$db" ]; then
        cp "$db" "$dir/data/db.sqlite3"
        verde "Base importada desde $db"
    fi

    generar_compose "$nombre"
    info "Iniciando contenedor (migraciones automáticas)..."
    (cd "$dir" && docker compose up -d)

    if esperar_respuesta "$puerto"; then
        verde "Backend respondiendo"
    else
        aviso "No respondió todavía. Revisá:  sudo $0 logs $nombre"
    fi

    echo
    echo "================= BACKEND DESPLEGADO ================="
    echo " Cliente:     $nombre"
    if [ -n "$dominio" ]; then
        echo " URL:         https://$dominio/api/"
    else
        echo " URL:         http://$(ip_local):$puerto/api/"
    fi
    echo " Admin:       /admin/   usuario: admin   clave: $admin_pass"
    echo " Clave API:   $(leer_env "$dir/.env" API_SYNC_KEY)"
    echo "              (header  Authorization: Bearer <clave>  para el dashboard y la sincronización)"
    echo " Monitor:     /health/  (para Uptime Kuma)"
    echo " Contenedor:  backend-$nombre"
    echo " Datos:       $dir/data"
    echo "======================================================"
    [ -z "$dominio" ] && aviso "Si usás firewall, abrí el puerto $puerto (ej: sudo ufw allow $puerto/tcp)"
    return 0
}

cmd_listar() {
    requiere_docker
    printf '%-25s %-7s %-35s %s\n' CLIENTE PUERTO DOMINIO ESTADO
    local env nombre estado
    for env in "$CLIENTES_DIR"/*/.env; do
        [ -f "$env" ] || continue
        nombre="$(basename "$(dirname "$env")")"
        estado="$(docker inspect -f '{{.State.Status}}{{if .State.Health}} ({{.State.Health.Status}}){{end}}' \
                  "backend-$nombre" 2>/dev/null || echo 'sin contenedor')"
        printf '%-25s %-7s %-35s %s\n' "$nombre" "$(leer_env "$env" PUERTO)" \
               "$(leer_env "$env" DOMINIO)" "$estado"
    done
}

cmd_actualizar() {
    requiere_docker
    if [ -d "$REPO_DIR/.git" ]; then
        info "Bajando cambios del repositorio..."
        git -C "$REPO_DIR" pull --ff-only
    fi
    cmd_construir
    local env nombre
    for env in "$CLIENTES_DIR"/*/.env; do
        [ -f "$env" ] || continue
        nombre="$(basename "$(dirname "$env")")"
        info "Actualizando $nombre (backup + migraciones automáticas)..."
        generar_compose "$nombre"
        (cd "$CLIENTES_DIR/$nombre" && docker compose up -d)
    done
    docker image prune -f >/dev/null
    verde "Todos los clientes actualizados"
}

cmd_reiniciar() {
    requiere_cliente "${1:-}"; requiere_docker
    generar_compose "$1"
    (cd "$CLIENTES_DIR/$1" && docker compose up -d --force-recreate)
    verde "Reiniciado $1"
}

escribir_env() { # escribir_env <archivo> <VARIABLE> <valor>
    if grep -qE "^$2=" "$1"; then
        sed -i "s|^$2=.*|$2=$3|" "$1"
    else
        echo "$2=$3" >> "$1"
    fi
}

cmd_dominio() {
    local nombre="${1:-}" dominio="${2:-}"
    requiere_cliente "$nombre"; requiere_docker
    [ -n "$dominio" ] || error "Uso: $0 dominio <nombre> <api.cliente.com>   (o --quitar)"
    local env="$CLIENTES_DIR/$nombre/.env"

    if [ "$dominio" = "--quitar" ]; then
        escribir_env "$env" DOMINIO ""
        escribir_env "$env" ALLOWED_HOSTS "*"
        escribir_env "$env" CSRF_TRUSTED_ORIGINS ""
        escribir_env "$env" BEHIND_HTTPS_PROXY False
        cmd_reiniciar "$nombre"
        verde "Dominio quitado. URL: http://$(ip_local):$(leer_env "$env" PUERTO)/api/"
        return 0
    fi

    [[ "$dominio" =~ ^[a-z0-9.-]+\.[a-z]{2,}$ ]] || error "Dominio inválido: $dominio"
    docker network inspect "$RED_TRAEFIK" >/dev/null 2>&1 \
        || error "Primero instalá Traefik:  sudo $0 traefik <email>"
    if grep -qsE "^DOMINIO=$dominio$" "$CLIENTES_DIR"/*/.env; then
        error "El dominio $dominio ya está asignado a otro cliente"
    fi

    escribir_env "$env" DOMINIO "$dominio"
    escribir_env "$env" ALLOWED_HOSTS "$dominio"
    escribir_env "$env" CSRF_TRUSTED_ORIGINS "https://$dominio"
    escribir_env "$env" BEHIND_HTTPS_PROXY True
    cmd_reiniciar "$nombre"
    verde "Dominio asignado. URL: https://$dominio/api/"
    aviso "El DNS (registro A de $dominio) tiene que apuntar a la IP de este VPS."
    aviso "El certificado HTTPS tarda ~1 minuto la primera vez. Desde ahora el puerto queda solo interno."
}

cmd_clave() {
    requiere_cliente "${1:-}"; requiere_docker
    local usuario="${2:-admin}"
    info "Cambiando la contraseña de '$usuario' en $1 (no se muestra mientras la escribís)"
    docker exec -it "backend-$1" python manage.py changepassword "$usuario"
}

cmd_logs() {
    requiere_cliente "${1:-}"; requiere_docker
    docker logs --tail 200 -f "backend-$1"
}

cmd_backup() {
    requiere_docker
    local objetivos=() env
    if [ -n "${1:-}" ]; then
        requiere_cliente "$1"; objetivos=("$1")
    else
        for env in "$CLIENTES_DIR"/*/.env; do
            [ -f "$env" ] && objetivos+=("$(basename "$(dirname "$env")")")
        done
    fi
    for nombre in "${objetivos[@]}"; do
        info "Backup de $nombre"
        docker exec "backend-$nombre" python manage.py backup_db || aviso "Falló el backup de $nombre"
    done
}

cmd_eliminar() {
    requiere_cliente "${1:-}"; requiere_docker
    local nombre="$1" confirma
    read -r -p "Escribí '$nombre' para confirmar (los datos se mueven a _eliminados): " confirma
    [ "$confirma" = "$nombre" ] || error "Cancelado"
    (cd "$CLIENTES_DIR/$nombre" && docker compose down)
    mkdir -p "$CLIENTES_DIR/_eliminados"
    mv "$CLIENTES_DIR/$nombre" "$CLIENTES_DIR/_eliminados/$nombre-$(date +%Y%m%d-%H%M%S)"
    verde "Cliente $nombre detenido. Datos en $CLIENTES_DIR/_eliminados/"
}

cmd_traefik() {
    local email="${1:-}"
    [ -n "$email" ] || error "Uso: $0 traefik <email-para-lets-encrypt>"
    requiere_docker
    docker network inspect "$RED_TRAEFIK" >/dev/null 2>&1 || docker network create "$RED_TRAEFIK" >/dev/null
    local dir="$CLIENTES_DIR/_traefik"
    mkdir -p "$dir/letsencrypt"
    cat > "$dir/docker-compose.yml" <<EOF
# Proxy único del VPS: recibe 80/443 y enruta por dominio a cada cliente
name: traefik
services:
  traefik:
    image: traefik:v3.6
    container_name: traefik
    restart: unless-stopped
    command:
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.web.http.redirections.entrypoint.to=websecure
      - --entrypoints.web.http.redirections.entrypoint.scheme=https
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.le.acme.email=$email
      - --certificatesresolvers.le.acme.storage=/letsencrypt/acme.json
      - --certificatesresolvers.le.acme.httpchallenge.entrypoint=web
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    networks: [$RED_TRAEFIK]
networks:
  $RED_TRAEFIK:
    external: true
EOF
    (cd "$dir" && docker compose up -d)
    verde "Traefik corriendo. Ahora podés crear clientes con --dominio"
    aviso "El DNS del dominio (registro A) tiene que apuntar a la IP de este VPS"
}

cmd_ayuda() {
    cat <<EOF
Uso: sudo $0 <comando>

  instalar                         Instala Docker (si falta) y construye la imagen
  crear <nombre> [opciones]        Crea y levanta un cliente nuevo
        --puerto N                 Puerto fijo (por defecto: el siguiente libre desde $PUERTO_INICIAL)
        --dominio api.cliente.com  Publicar por dominio con HTTPS (requiere 'traefik')
        --base archivo.sqlite3     Arrancar con una base existente
        --cors https://front.com   Origen permitido del frontend
  listar                           Clientes, puertos y estado
  actualizar                       git pull + rebuild + reinicia todos (con backup previo)
  reiniciar <nombre>               Reinicia un cliente (aplica cambios del .env)
  dominio <nombre> <dominio>       Pasa un cliente existente a dominio + HTTPS (--quitar para volver a puerto)
  clave <nombre> [usuario]         Cambiar contraseña del admin (o de otro usuario)
  logs <nombre>                    Ver logs en vivo
  backup [nombre]                  Backup de la base (todos si no se indica)
  eliminar <nombre>                Detiene el cliente y archiva sus datos
  traefik <email>                  Instala el proxy para usar dominios + HTTPS

Carpeta de clientes: $CLIENTES_DIR   (cambiar con CLIENTES_DIR=/otra/ruta)
EOF
}

comando="${1:-ayuda}"; shift || true
case "$comando" in
    instalar)   cmd_instalar "$@" ;;
    construir)  cmd_construir "$@" ;;
    crear)      cmd_crear "$@" ;;
    listar|ls)  cmd_listar "$@" ;;
    actualizar) cmd_actualizar "$@" ;;
    reiniciar)  cmd_reiniciar "$@" ;;
    clave)      cmd_clave "$@" ;;
    dominio)    cmd_dominio "$@" ;;
    logs)       cmd_logs "$@" ;;
    backup)     cmd_backup "$@" ;;
    eliminar)   cmd_eliminar "$@" ;;
    traefik)    cmd_traefik "$@" ;;
    *)          cmd_ayuda ;;
esac
