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
#  Uso:  ./clientes.sh <comando> [opciones]      (./clientes.sh ayuda)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# La carpeta de clientes se guarda en $CONFIG para que funcione igual con sudo, sin sudo o desde cron.
# Prioridad: variable CLIENTES_DIR > archivo de configuración > /opt/clientes-backend
CONFIG="/etc/backend-global.conf"
if [ -z "${CLIENTES_DIR:-}" ] && [ -f "$CONFIG" ]; then
    # shellcheck disable=SC1090
    . "$CONFIG"
fi
CLIENTES_DIR="${CLIENTES_DIR:-/opt/clientes-backend}"
if [ ! -f "$CONFIG" ] && [ "$(id -u)" = "0" ]; then
    echo "CLIENTES_DIR=$CLIENTES_DIR" > "$CONFIG"
fi
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
    command -v docker >/dev/null || error "Docker no está instalado. Ejecutá: $0 instalar"
    docker info >/dev/null 2>&1 || error "No se puede usar Docker. Ejecutá el script como root (o con sudo)."
}

requiere_cliente() {
    [ -n "${1:-}" ] || error "Falta el nombre del cliente"
    # Mismo formato que en 'crear': evita rutas como '..' (importante para 'borrar')
    [[ "$1" =~ ^[a-z0-9][a-z0-9-]{1,40}$ ]] || error "Nombre de cliente inválido: $1"
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
    local puerto dominio proxy
    puerto="$(leer_env "$dir/.env" PUERTO)"
    dominio="$(leer_env "$dir/.env" DOMINIO)"
    proxy="$(leer_env "$dir/.env" PROXY)"

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
        elif [ "$proxy" = "nginx" ]; then
            # Modo dominio con el nginx del VPS: el puerto queda solo local
            echo "    ports:"
            echo "      - \"127.0.0.1:$puerto:8000\""
        else
            # Modo dominio con Traefik: enruta por nombre; el puerto queda solo local
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
        [ "$(id -u)" = "0" ] || error "Para instalar Docker ejecutá como root (o con sudo)"
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
    verde "Listo. Creá el primer cliente con:  $0 crear <nombre>"
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

    if [ -n "$dominio" ]; then
        validar_dominio "$dominio" ""
        [ -n "$(detectar_proxy)" ] || error_sin_proxy
    fi

    mkdir -p "$dir/data"
    verde "Carpeta creada: $dir"

    local admin_pass; admin_pass="$(aleatorio 16)"

    cat > "$dir/.env" <<EOF
# Cliente: $nombre  (creado $(date '+%Y-%m-%d %H:%M'))
PUERTO=$puerto
DOMINIO=
PROXY=

SECRET_KEY=$(aleatorio 60)
DEBUG=False
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=
BEHIND_HTTPS_PROXY=False
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
        aviso "No respondió todavía. Revisá:  $0 logs $nombre"
    fi

    if [ -n "$dominio" ]; then
        cmd_dominio "$nombre" "$dominio" || true
        dominio="$(leer_env "$dir/.env" DOMINIO)"
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
    if [ -z "$dominio" ]; then
        aviso "Para entrar desde afuera abrí el puerto $puerto en el firewall del proveedor,"
        aviso "o asignale un dominio:  $0 dominio $nombre $nombre.tudominio.com"
    fi
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

detectar_proxy() { # nginx | traefik | (vacío)
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx traefik; then
        echo traefik
    elif command -v nginx >/dev/null && systemctl is-active --quiet nginx; then
        echo nginx
    fi
    return 0
}

error_sin_proxy() {
    error "Este VPS no tiene nginx ni Traefik para los dominios. Instalá nginx:  apt install -y nginx   (o: $0 traefik <email>)"
}

validar_dominio() { # validar_dominio <dominio> <cliente-actual>
    [[ "$1" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$ ]] \
        || error "Dominio inválido: $1 (ej: la-republica.brixsoft.com)"
    local env
    for env in "$CLIENTES_DIR"/*/.env; do
        [ -f "$env" ] || continue
        [ "$(basename "$(dirname "$env")")" = "$2" ] && continue
        if grep -qFx "DOMINIO=$1" "$env"; then
            error "El dominio $1 ya está asignado a $(basename "$(dirname "$env")")"
        fi
    done
    return 0
}

nginx_conf() { # ruta del archivo de nginx del cliente
    if [ -d /etc/nginx/sites-available ]; then
        echo "/etc/nginx/sites-available/backend-$1.conf"
    else
        echo "/etc/nginx/conf.d/backend-$1.conf"
    fi
}

quitar_nginx() { # quitar_nginx <nombre>
    rm -f "$(nginx_conf "$1")" "/etc/nginx/sites-enabled/backend-$1.conf"
    if nginx -t >/dev/null 2>&1; then systemctl reload nginx; fi
    return 0
}

configurar_nginx() { # configurar_nginx <nombre> <dominio> <puerto>  -> 0 si quedó con HTTPS
    local nombre="$1" dominio="$2" puerto="$3" conf
    conf="$(nginx_conf "$nombre")"
    cat > "$conf" <<EOF
# Generado por clientes.sh para el cliente $nombre - no editar a mano
server {
    listen 80;
    listen [::]:80;
    server_name $dominio;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:$puerto;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
EOF
    if [ -d /etc/nginx/sites-enabled ]; then
        ln -sf "$conf" "/etc/nginx/sites-enabled/backend-$nombre.conf"
    fi
    if ! nginx -t >/dev/null 2>&1; then
        quitar_nginx "$nombre"
        error "nginx rechazó la configuración (revisá con: nginx -t). No se cambió nada en nginx."
    fi
    systemctl reload nginx
    verde "nginx configurado: $dominio → puerto local $puerto"

    # El certificado solo se puede sacar si el DNS ya apunta a este VPS
    local ip_dns
    ip_dns="$(getent ahostsv4 "$dominio" 2>/dev/null | awk 'NR==1{print $1}')"
    if [ -z "$ip_dns" ]; then
        aviso "El dominio $dominio todavía no existe en el DNS."
        aviso "Creá un registro A: $dominio → $(ip_local) y después repetí:  $0 dominio $nombre $dominio"
        return 1
    fi
    if ! hostname -I | tr ' ' '\n' | grep -qx "$ip_dns"; then
        aviso "El DNS de $dominio apunta a $ip_dns y este VPS es $(ip_local). Se intenta igual..."
    fi

    if ! command -v certbot >/dev/null; then
        info "Instalando certbot..."
        apt-get install -y certbot python3-certbot-nginx >/dev/null
    fi
    local email_args=(--register-unsafely-without-email)
    if [ -n "${CERTBOT_EMAIL:-}" ]; then email_args=(-m "$CERTBOT_EMAIL"); fi
    info "Pidiendo certificado HTTPS (Let's Encrypt)..."
    if certbot --nginx -d "$dominio" --non-interactive --agree-tos --redirect \
            --keep-until-expiring "${email_args[@]}"; then
        verde "HTTPS activo"
        return 0
    fi
    aviso "No se pudo sacar el certificado. Revisá el DNS y repetí:  $0 dominio $nombre $dominio"
    return 1
}

cmd_dominio() {
    local nombre="${1:-}" dominio="${2:-}"
    requiere_cliente "$nombre"; requiere_docker
    [ -n "$dominio" ] || error "Uso: $0 dominio <nombre> <nombre.brixsoft.com>   (o --quitar)"
    local env="$CLIENTES_DIR/$nombre/.env"
    local dominio_viejo proxy_viejo puerto
    dominio_viejo="$(leer_env "$env" DOMINIO)"
    proxy_viejo="$(leer_env "$env" PROXY)"
    puerto="$(leer_env "$env" PUERTO)"

    if [ "$dominio" = "--quitar" ]; then
        if [ "$proxy_viejo" = "nginx" ]; then quitar_nginx "$nombre"; fi
        escribir_env "$env" DOMINIO ""
        escribir_env "$env" PROXY ""
        escribir_env "$env" ALLOWED_HOSTS "*"
        escribir_env "$env" CSRF_TRUSTED_ORIGINS ""
        escribir_env "$env" BEHIND_HTTPS_PROXY False
        cmd_reiniciar "$nombre"
        verde "Dominio quitado. URL: http://$(ip_local):$puerto/api/"
        return 0
    fi

    validar_dominio "$dominio" "$nombre"
    local proxy; proxy="$(detectar_proxy)"
    [ -n "$proxy" ] || error_sin_proxy

    if [ "$proxy_viejo" = "nginx" ] && [ "$dominio_viejo" != "$dominio" ]; then
        quitar_nginx "$nombre"
    fi

    escribir_env "$env" DOMINIO "$dominio"
    escribir_env "$env" PROXY "$proxy"
    # 127.0.0.1/localhost: para el chequeo de salud interno (el puerto deja de ser público)
    escribir_env "$env" ALLOWED_HOSTS "$dominio,127.0.0.1,localhost"
    escribir_env "$env" CSRF_TRUSTED_ORIGINS "https://$dominio"
    escribir_env "$env" BEHIND_HTTPS_PROXY True
    cmd_reiniciar "$nombre"

    if [ "$proxy" = "nginx" ]; then
        configurar_nginx "$nombre" "$dominio" "$puerto" || return 1
        verde "Listo: https://$dominio/api/"
    else
        verde "Dominio asignado (Traefik). URL: https://$dominio/api/"
        aviso "El DNS (registro A de $dominio) tiene que apuntar a la IP de este VPS."
    fi
    aviso "El puerto $puerto quedó cerrado hacia afuera: se entra solo por el dominio."
    return 0
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
    if [ "$(leer_env "$CLIENTES_DIR/$nombre/.env" PROXY)" = "nginx" ]; then
        quitar_nginx "$nombre"
        verde "Configuración de nginx eliminada"
    fi
    mkdir -p "$CLIENTES_DIR/_eliminados"
    mv "$CLIENTES_DIR/$nombre" "$CLIENTES_DIR/_eliminados/$nombre-$(date +%Y%m%d-%H%M%S)"
    verde "Cliente $nombre detenido. Datos en $CLIENTES_DIR/_eliminados/"
}

cmd_borrar() {
    local nombre="${1:-}" confirmar="${2:-}"
    requiere_cliente "$nombre"; requiere_docker
    local dir="$CLIENTES_DIR/$nombre"
    local dominio proxy
    dominio="$(leer_env "$dir/.env" DOMINIO)"
    proxy="$(leer_env "$dir/.env" PROXY)"

    if [ "$confirmar" != "--si" ]; then
        aviso "Se va a BORRAR PARA SIEMPRE '$nombre': base de datos, backups, configuración${dominio:+ y el dominio $dominio}."
        aviso "No se puede deshacer. (Para una baja con copia de los datos usá: $0 eliminar $nombre)"
        local confirma
        read -r -p "Escribí '$nombre' para confirmar: " confirma
        [ "$confirma" = "$nombre" ] || error "Cancelado, no se borró nada"
    fi

    if [ -f "$dir/docker-compose.yml" ]; then
        (cd "$dir" && docker compose down --remove-orphans) || true
    fi
    docker rm -f "backend-$nombre" >/dev/null 2>&1 || true
    verde "Contenedor y red eliminados"

    if [ "$proxy" = "nginx" ]; then
        quitar_nginx "$nombre"
        if [ -n "$dominio" ] && command -v certbot >/dev/null; then
            certbot delete --cert-name "$dominio" --non-interactive >/dev/null 2>&1 || true
        fi
        verde "nginx y certificado de $dominio eliminados"
    fi

    rm -rf "$dir"
    verde "Datos borrados: $dir"
    verde "Cliente $nombre borrado por completo (la imagen compartida por todos los clientes no se toca)"
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
Uso: $0 <comando>   (como root)

  instalar                         Instala Docker (si falta) y construye la imagen
  crear <nombre> [opciones]        Crea y levanta un cliente nuevo
        --puerto N                 Puerto fijo (por defecto: el siguiente libre desde $PUERTO_INICIAL)
        --dominio x.brixsoft.com   Publicar por dominio con HTTPS (usa el nginx o Traefik del VPS)
        --base archivo.sqlite3     Arrancar con una base existente
        --cors https://front.com   Origen permitido del frontend
  listar                           Clientes, puertos y estado
  actualizar                       git pull + rebuild + reinicia todos (con backup previo)
  reiniciar <nombre>               Reinicia un cliente (aplica cambios del .env)
  dominio <nombre> <dominio>       Pasa un cliente existente a dominio + HTTPS (--quitar para volver a puerto)
  clave <nombre> [usuario]         Cambiar contraseña del admin (o de otro usuario)
  logs <nombre>                    Ver logs en vivo
  backup [nombre]                  Backup de la base (todos si no se indica)
  eliminar <nombre>                Baja: detiene el cliente y archiva sus datos en _eliminados
  borrar <nombre> [--si]           Borra TODO para siempre (pruebas/errores). --si: sin confirmar
  traefik <email>                  Instala Traefik (solo en un VPS SIN nginx)

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
    borrar)     cmd_borrar "$@" ;;
    traefik)    cmd_traefik "$@" ;;
    *)          cmd_ayuda ;;
esac
