# Despliegue de BACKEND-GLOBAL por cliente

Un solo código, **una instalación independiente por cliente**: cada una tiene su base de
datos, su `SECRET_KEY`, su puerto y su carpeta. Se pueden tener muchos clientes en un VPS,
o un cliente solo en su propio VPS. Los comandos son los mismos en los dos casos.

```
<carpeta de clientes>/
├── ferreteria-x/
│   ├── .env          ← configuración propia (puerto, claves, dominio)
│   └── data/         ← db.sqlite3, media/, backups/   ← LO ÚNICO A RESPALDAR
├── centro-motos/
│   └── ...
```

Las migraciones corren solas al arrancar o al actualizar, y antes de migrar se hace un
backup automático en `data/backups/`.

| VPS | Cómo corre | Script |
|---|---|---|
| **Linux (recomendado)** Ubuntu/Debian | Docker: un contenedor por cliente | `deploy/linux/clientes.sh` |
| **Windows Server** | Python nativo: una tarea programada por cliente | `deploy/windows/clientes.ps1` |

> Windows Server 2019 no puede correr contenedores Linux de forma razonable, por eso hay un modo nativo.
> Si podés elegir, usá Linux: es más barato, más liviano y aísla mejor a cada cliente.

---

## Linux (Ubuntu 22.04 / 24.04 o Debian 12)

### Una sola vez por VPS

```bash
sudo apt update && sudo apt install -y git curl
sudo git clone https://github.com/<usuario>/BACKEND-GLOBAL.git /opt/backend-global
cd /opt/backend-global
sudo ./deploy/linux/clientes.sh instalar     # instala Docker si falta y construye la imagen
```

### Por cada cliente

```bash
sudo ./deploy/linux/clientes.sh crear ferreteria-x
# → puerto asignado automáticamente (8001, 8002, ...)
# → muestra la URL http://IP:PUERTO/api/ y la clave del admin

sudo ./deploy/linux/clientes.sh crear centro-motos --base /ruta/db.sqlite3   # con datos existentes
```

### Día a día

```bash
sudo ./deploy/linux/clientes.sh listar             # clientes, puertos, estado
sudo ./deploy/linux/clientes.sh actualizar         # git pull + rebuild + reinicia todos
sudo ./deploy/linux/clientes.sh logs ferreteria-x
sudo ./deploy/linux/clientes.sh reiniciar ferreteria-x   # después de editar su .env
sudo ./deploy/linux/clientes.sh eliminar ferreteria-x    # archiva los datos, no los borra
```

Backup diario automático (3 AM, conserva 14 por cliente):

```bash
echo "0 3 * * * root /opt/backend-global/deploy/linux/clientes.sh backup" | sudo tee /etc/cron.d/backend-backup
```

> Ojo: Docker abre los puertos publicados **aunque ufw los bloquee**. Si un cliente no tiene
> que ser accesible desde afuera, usá el modo dominio (el puerto queda solo en localhost).

### Más adelante: dominios con HTTPS

Cuando tengas el dominio, creá un registro DNS **A** de `api.cliente.com.ar` apuntando a la IP del VPS, y después:

```bash
sudo ./deploy/linux/clientes.sh traefik tu@email.com          # una sola vez por VPS (usa 80/443)
sudo ./deploy/linux/clientes.sh crear cliente-nuevo --dominio api.cliente.com.ar
```

Traefik saca el certificado de Let's Encrypt y enruta por dominio. No hay que configurar Nginx.

Para pasar a dominio un cliente que ya existe (sus datos no se tocan):

```bash
sudo ./deploy/linux/clientes.sh dominio ferreteria-x api.ferreteriax.com.ar
sudo ./deploy/linux/clientes.sh dominio ferreteria-x --quitar     # volver a IP:puerto
```

Tip: con un DNS comodín `*.api.brixsoft.com → IP del VPS` (un solo registro A), cada cliente
puede tener `nombre.api.brixsoft.com` sin tocar el DNS nunca más.

---

## Windows Server

### Una sola vez por VPS (PowerShell **como Administrador**)

1. Instalar **Python 3.12** desde https://www.python.org/downloads/ (tildar *Add python.exe to PATH*, *Install for all users*).
2. Instalar **Git** desde https://git-scm.com/download/win
3. Clonar e instalar:

```powershell
git clone https://github.com/<usuario>/BACKEND-GLOBAL.git C:\backend-global
cd C:\backend-global
Set-ExecutionPolicy -Scope Process Bypass
.\deploy\windows\clientes.ps1 instalar
```

### Por cada cliente

```powershell
.\deploy\windows\clientes.ps1 crear ferreteria-x
.\deploy\windows\clientes.ps1 crear centro-motos -Base C:\ruta\db.sqlite3
```

Cada cliente queda como tarea programada `backend-<nombre>`: arranca con Windows y se
reinicia sola si el proceso se cae. El script también abre el puerto en el Firewall de Windows.

### Día a día

```powershell
.\deploy\windows\clientes.ps1 listar
.\deploy\windows\clientes.ps1 actualizar
.\deploy\windows\clientes.ps1 logs ferreteria-x
.\deploy\windows\clientes.ps1 reiniciar ferreteria-x
.\deploy\windows\clientes.ps1 backup
```

Backup diario: crear una tarea programada que ejecute
`powershell -ExecutionPolicy Bypass -File C:\backend-global\deploy\windows\clientes.ps1 backup`.

> Si `git pull` dice *dubious ownership*:
> `git config --global --add safe.directory C:/backend-global`

---

## Acceso a la API (clave)

La API **no responde sin credenciales** (`401`). Hay dos formas de entrar:

- **Navegador:** loguearse en `/admin/`; después `/api/` se navega normalmente.
- **Dashboard / sincronización:** mandar la clave del cliente (`API_SYNC_KEY` de su `.env`,
  la muestra `crear` al final) en el header `Authorization: Bearer <clave>`.

`/health/` es público y no muestra datos: es la URL para cargar en Uptime Kuma.

## Firewall del proveedor

Muchos VPS (Contabo, Hetzner, AWS, DigitalOcean...) tienen además un firewall en el
panel web. Ahí también hay que abrir el puerto de cada cliente (o 80/443 en el modo dominio).

## Migrar un cliente que ya está en producción

1. Copiar su `db.sqlite3` al VPS nuevo.
2. `crear <nombre> --base /ruta/db.sqlite3` (Linux) o `-Base` (Windows).
3. Apuntar el frontend o el script de sincronización a la URL nueva.
