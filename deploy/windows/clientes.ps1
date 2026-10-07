# =============================================================================
#  BACKEND-GLOBAL - gestor de instalaciones por cliente (Windows, sin Docker)
#
#  Un solo codigo (este repo) + un entorno Python compartido.
#  Cada cliente tiene su carpeta en $ClientesDir\<nombre> con:
#     .env       -> configuracion propia (SECRET_KEY, puerto, DATA_DIR...)
#     run.cmd    -> arranca el servidor (migra con backup previo, reinicia si se cae)
#     data\      -> db.sqlite3, media\, backups\   (lo unico a respaldar)
#     logs\      -> server.log
#  Cada cliente corre como Tarea Programada "backend-<nombre>" que inicia con Windows.
#
#  Uso (PowerShell como Administrador):
#     .\clientes.ps1 instalar
#     .\clientes.ps1 crear centro-motos [-Puerto 8005] [-Base C:\ruta\db.sqlite3] [-Cors https://front.com]
#     .\clientes.ps1 ayuda
# =============================================================================
param(
    [Parameter(Position = 0)][string]$Comando = 'ayuda',
    [Parameter(Position = 1)][string]$Nombre,
    [int]$Puerto,
    [string]$Base,
    [string]$Cors,
    [switch]$Si
)

$ErrorActionPreference = 'Stop'

$RepoDir     = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$BackendDir  = Join-Path $RepoDir 'backend'
$ClientesDir = if ($env:CLIENTES_DIR) { $env:CLIENTES_DIR } else { 'C:\clientes-backend' }
$VenvDir     = Join-Path $ClientesDir '_venv'
$Python      = Join-Path $VenvDir 'Scripts\python.exe'
$PuertoInicial = 8001
$Utf8SinBom  = New-Object System.Text.UTF8Encoding $false

function Ok($m)    { Write-Host "OK  $m" -ForegroundColor Green }
function Info($m)  { Write-Host "->  $m" -ForegroundColor Cyan }
function Aviso($m) { Write-Host "!   $m" -ForegroundColor Yellow }
function Falla($m) { Write-Host "X   $m" -ForegroundColor Red; exit 1 }

function Requiere-Admin {
    $p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Falla 'Ejecuta PowerShell como Administrador'
    }
}

function Requiere-Instalado {
    if (-not (Test-Path $Python)) { Falla "Falta el entorno Python. Ejecuta: .\clientes.ps1 instalar" }
}

function Requiere-Cliente($n) {
    if (-not $n) { Falla 'Falta el nombre del cliente' }
    # Mismo formato que en 'crear': evita rutas como '..' (importante para 'borrar')
    if ($n -cnotmatch '^[a-z0-9][a-z0-9-]{1,40}$') { Falla "Nombre de cliente invalido: $n" }
    if (-not (Test-Path (Join-Path $ClientesDir "$n\.env"))) { Falla "No existe el cliente '$n' en $ClientesDir" }
}

function Aleatorio([int]$largo) {
    $chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'.ToCharArray()
    $rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
    $bytes = New-Object byte[] $largo
    $rng.GetBytes($bytes)
    -join ($bytes | ForEach-Object { $chars[$_ % $chars.Length] })
}

function Leer-Env($archivo, $variable) {
    $linea = Get-Content $archivo | Where-Object { $_ -match "^$variable=" } | Select-Object -First 1
    if ($linea) { $linea.Substring($variable.Length + 1) } else { '' }
}

function Clientes {
    if (-not (Test-Path $ClientesDir)) { return @() }
    Get-ChildItem $ClientesDir -Directory |
        Where-Object { -not $_.Name.StartsWith('_') -and (Test-Path (Join-Path $_.FullName '.env')) } |
        ForEach-Object { $_.Name }
}

function Puerto-Ocupado([int]$p) {
    foreach ($c in Clientes) {
        if ((Leer-Env (Join-Path $ClientesDir "$c\.env") 'PUERTO') -eq "$p") { return $true }
    }
    $escucha = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    return [bool]$escucha
}

function Siguiente-Puerto {
    $p = $PuertoInicial
    while (Puerto-Ocupado $p) { $p++ }
    return $p
}

function Detener-Puerto([int]$p) {
    Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

function Esperar-Respuesta([int]$p) {
    for ($i = 0; $i -lt 60; $i++) {
        try {
            Invoke-WebRequest "http://127.0.0.1:$p/health/" -UseBasicParsing -TimeoutSec 3 | Out-Null
            return $true
        } catch { Start-Sleep -Seconds 2 }
    }
    return $false
}

function Escribir-RunCmd($n) {
    $dir = Join-Path $ClientesDir $n
    $p = Leer-Env (Join-Path $dir '.env') 'PUERTO'
    # Bucle: si el servidor se cae, vuelve a levantarlo a los 5 segundos
    $cmd = @"
@echo off
rem Generado por clientes.ps1 - no editar a mano
set ENV_FILE=%~dp0.env
cd /d "$BackendDir"
:inicio
"$Python" manage.py migrate --check >nul 2>&1
if errorlevel 1 (
    "$Python" manage.py backup_db --motivo pre-migracion --conservar 30 >> "%~dp0logs\server.log" 2>&1
    "$Python" manage.py migrate --noinput >> "%~dp0logs\server.log" 2>&1
)
"$Python" manage.py createsuperuser --noinput >nul 2>&1
echo [%date% %time%] Iniciando en puerto $p >> "%~dp0logs\server.log"
"$Python" -m waitress --listen=0.0.0.0:$p --threads=8 --channel-timeout=300 config.wsgi:application >> "%~dp0logs\server.log" 2>&1
echo [%date% %time%] El servidor se detuvo, reiniciando... >> "%~dp0logs\server.log"
timeout /t 5 /nobreak >nul
goto inicio
"@
    [IO.File]::WriteAllText((Join-Path $dir 'run.cmd'), $cmd, [Text.Encoding]::ASCII)
}

function Registrar-Tarea($n) {
    $dir = Join-Path $ClientesDir $n
    $tarea = "backend-$n"
    $accion = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c `"$dir\run.cmd`"" -WorkingDirectory $dir
    $disparo = New-ScheduledTaskTrigger -AtStartup
    $usuario = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    $config = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable `
        -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew
    Register-ScheduledTask -TaskName $tarea -Action $accion -Trigger $disparo -Principal $usuario `
        -Settings $config -Force | Out-Null
}

function Detener-Cliente($n) {
    $tarea = "backend-$n"
    $p = [int](Leer-Env (Join-Path $ClientesDir "$n\.env") 'PUERTO')
    Stop-ScheduledTask -TaskName $tarea -ErrorAction SilentlyContinue
    Detener-Puerto $p
}

function Iniciar-Cliente($n) {
    Escribir-RunCmd $n
    Registrar-Tarea $n
    Start-ScheduledTask -TaskName "backend-$n"
}

# -----------------------------------------------------------------------------
function Cmd-Instalar {
    Requiere-Admin
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) {
        Falla 'Python no esta instalado. Instalar Python 3.12 desde https://www.python.org/downloads/ (marcar "Add to PATH")'
    }
    Info "Python: $(& python --version)"

    New-Item -ItemType Directory -Force $ClientesDir | Out-Null
    if (-not (Test-Path $Python)) {
        Info "Creando entorno en $VenvDir ..."
        & python -m venv $VenvDir
    }
    Cmd-Construir
    Ok "Listo. Crea el primer cliente con:  .\clientes.ps1 crear <nombre>"
}

function Cmd-Construir {
    Requiere-Instalado
    Info 'Instalando dependencias...'
    & $Python -m pip install --upgrade pip -q
    & $Python -m pip install -r (Join-Path $BackendDir 'requirements.txt') -q
    if ($LASTEXITCODE -ne 0) { Falla 'Fallo pip install' }
    Push-Location $BackendDir
    try { & $Python manage.py collectstatic --noinput | Out-Null } finally { Pop-Location }
    Ok 'Dependencias y archivos estaticos listos'
}

function Cmd-Crear {
    Requiere-Admin; Requiere-Instalado
    if ($Nombre -notmatch '^[a-z0-9][a-z0-9-]{1,40}$') {
        Falla 'Nombre invalido. Usar minusculas, numeros y guiones (ej: centro-motos)'
    }
    $dir = Join-Path $ClientesDir $Nombre
    if (Test-Path $dir) { Falla "Ya existe $dir" }
    if ($Base -and -not (Test-Path $Base)) { Falla "No existe el archivo de base $Base" }

    if (-not $Puerto) { $Puerto = Siguiente-Puerto }
    elseif (Puerto-Ocupado $Puerto) { Falla "El puerto $Puerto ya esta en uso" }

    New-Item -ItemType Directory -Force "$dir\data\media", "$dir\data\backups", "$dir\logs" | Out-Null
    Ok "Carpeta creada: $dir"

    $adminPass = Aleatorio 16
    $contenido = @"
# Cliente: $Nombre  (creado $(Get-Date -Format 'yyyy-MM-dd HH:mm'))
PUERTO=$Puerto
DOMINIO=
DATA_DIR=$dir\data

SECRET_KEY=$(Aleatorio 60)
DEBUG=False
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=
BEHIND_HTTPS_PROXY=False
CORS_ALLOWED_ORIGINS=$Cors
API_SYNC_KEY=$(Aleatorio 40)

# Superusuario inicial del admin (solo se usa la primera vez)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@localhost
DJANGO_SUPERUSER_PASSWORD=$adminPass
"@
    [IO.File]::WriteAllText("$dir\.env", $contenido, $Utf8SinBom)
    Ok "Configuracion generada (SECRET_KEY propia, puerto $Puerto)"

    if ($Base) {
        Copy-Item $Base "$dir\data\db.sqlite3"
        Ok "Base importada desde $Base"
    }

    New-NetFirewallRule -DisplayName "backend-$Nombre" -Direction Inbound -Protocol TCP `
        -LocalPort $Puerto -Action Allow | Out-Null
    Ok "Firewall: puerto $Puerto abierto"

    Info 'Iniciando (migraciones automaticas)...'
    Iniciar-Cliente $Nombre
    if (Esperar-Respuesta $Puerto) { Ok 'Backend respondiendo' }
    else { Aviso "No respondio todavia. Revisa:  .\clientes.ps1 logs $Nombre" }

    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } |
           Select-Object -First 1).IPAddress
    Write-Host ''
    Write-Host '================= BACKEND DESPLEGADO ================='
    Write-Host " Cliente:  $Nombre"
    Write-Host " URL:      http://${ip}:$Puerto/api/"
    Write-Host " Admin:    /admin/   usuario: admin   clave: $adminPass"
    Write-Host " ClaveAPI: $(Leer-Env "$dir\.env" 'API_SYNC_KEY')   (header Authorization: Bearer <clave>)"
    Write-Host " Monitor:  /health/  (para Uptime Kuma)"
    Write-Host " Tarea:    backend-$Nombre (inicia con Windows)"
    Write-Host " Datos:    $dir\data"
    Write-Host '======================================================'
    Aviso 'Si el VPS tiene firewall del proveedor (panel web), abri el puerto ahi tambien'
}

function Cmd-Listar {
    '{0,-25} {1,-7} {2,-12} {3}' -f 'CLIENTE', 'PUERTO', 'TAREA', 'ESCUCHANDO'
    foreach ($c in Clientes) {
        $p = [int](Leer-Env (Join-Path $ClientesDir "$c\.env") 'PUERTO')
        $t = Get-ScheduledTask -TaskName "backend-$c" -ErrorAction SilentlyContinue
        $estado = if ($t) { $t.State } else { 'sin tarea' }
        $escucha = if (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue) { 'si' } else { 'NO' }
        '{0,-25} {1,-7} {2,-12} {3}' -f $c, $p, $estado, $escucha
    }
}

function Cmd-Actualizar {
    Requiere-Admin; Requiere-Instalado
    if (Test-Path (Join-Path $RepoDir '.git')) {
        Info 'Bajando cambios del repositorio...'
        git -C $RepoDir pull --ff-only
        if ($LASTEXITCODE -ne 0) { Falla 'Fallo git pull' }
    }
    # Hay que detener todo antes de pip install (Windows bloquea archivos en uso)
    foreach ($c in Clientes) { Detener-Cliente $c }
    Cmd-Construir
    foreach ($c in Clientes) {
        Info "Iniciando $c (backup + migraciones automaticas)..."
        Iniciar-Cliente $c
    }
    Ok 'Todos los clientes actualizados'
}

function Cmd-Reiniciar {
    Requiere-Admin; Requiere-Cliente $Nombre
    Detener-Cliente $Nombre
    Iniciar-Cliente $Nombre
    Ok "Reiniciado $Nombre"
}

function Cmd-Clave {
    Requiere-Instalado; Requiere-Cliente $Nombre
    Push-Location $BackendDir
    try {
        $env:ENV_FILE = Join-Path $ClientesDir "$Nombre\.env"
        & $Python manage.py changepassword admin
    } finally { Pop-Location; Remove-Item Env:\ENV_FILE -ErrorAction SilentlyContinue }
}

function Cmd-Logs {
    Requiere-Cliente $Nombre
    Get-Content (Join-Path $ClientesDir "$Nombre\logs\server.log") -Tail 100 -Wait
}

function Cmd-Backup {
    Requiere-Instalado
    $objetivos = if ($Nombre) { Requiere-Cliente $Nombre; @($Nombre) } else { Clientes }
    Push-Location $BackendDir
    try {
        foreach ($c in $objetivos) {
            Info "Backup de $c"
            $env:ENV_FILE = Join-Path $ClientesDir "$c\.env"
            & $Python manage.py backup_db
            if ($LASTEXITCODE -ne 0) { Aviso "Fallo el backup de $c" }
        }
    } finally { Pop-Location; Remove-Item Env:\ENV_FILE -ErrorAction SilentlyContinue }
}

function Cmd-Eliminar {
    Requiere-Admin; Requiere-Cliente $Nombre
    $conf = Read-Host "Escribi '$Nombre' para confirmar (los datos se mueven a _eliminados)"
    if ($conf -ne $Nombre) { Falla 'Cancelado' }
    Detener-Cliente $Nombre
    Unregister-ScheduledTask -TaskName "backend-$Nombre" -Confirm:$false -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "backend-$Nombre" -ErrorAction SilentlyContinue
    $destino = Join-Path $ClientesDir '_eliminados'
    New-Item -ItemType Directory -Force $destino | Out-Null
    Move-Item (Join-Path $ClientesDir $Nombre) (Join-Path $destino "$Nombre-$(Get-Date -Format 'yyyyMMdd-HHmmss')")
    Ok "Cliente $Nombre detenido. Datos en $destino"
}

function Cmd-Borrar {
    Requiere-Admin; Requiere-Cliente $Nombre
    if (-not $Si) {
        Aviso "Se va a BORRAR PARA SIEMPRE '$Nombre': base de datos, backups y configuracion."
        Aviso "No se puede deshacer. (Para una baja con copia de los datos usa: eliminar $Nombre)"
        $conf = Read-Host "Escribi '$Nombre' para confirmar"
        if ($conf -ne $Nombre) { Falla 'Cancelado, no se borro nada' }
    }
    Detener-Cliente $Nombre
    Unregister-ScheduledTask -TaskName "backend-$Nombre" -Confirm:$false -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "backend-$Nombre" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2   # esperar que Windows libere los archivos
    Remove-Item (Join-Path $ClientesDir $Nombre) -Recurse -Force
    Ok "Cliente $Nombre borrado por completo"
}

function Cmd-Ayuda {
    @"
Uso (PowerShell como Administrador):  .\clientes.ps1 <comando>

  instalar                          Crea el entorno Python e instala dependencias
  crear <nombre> [opciones]         Crea y levanta un cliente nuevo
        -Puerto N                   Puerto fijo (por defecto: el siguiente libre desde $PuertoInicial)
        -Base C:\ruta\db.sqlite3      Arrancar con una base existente
        -Cors https://front.com     Origen permitido del frontend
  listar                            Clientes, puertos y estado
  actualizar                        git pull + dependencias + reinicia todos (con backup previo)
  reiniciar <nombre>                Reinicia un cliente (aplica cambios del .env)
  clave <nombre>                    Cambiar contrasena del admin
  logs <nombre>                     Ver log en vivo
  backup [nombre]                   Backup de la base (todos si no se indica)
  eliminar <nombre>                 Baja: detiene el cliente y archiva sus datos en _eliminados
  borrar <nombre> [-Si]             Borra TODO para siempre (pruebas/errores). -Si: sin confirmar

Carpeta de clientes: $ClientesDir   (cambiar con `$env:CLIENTES_DIR)
"@
}

switch ($Comando) {
    'instalar'   { Cmd-Instalar }
    'construir'  { Cmd-Construir }
    'crear'      { Cmd-Crear }
    'listar'     { Cmd-Listar }
    'actualizar' { Cmd-Actualizar }
    'reiniciar'  { Cmd-Reiniciar }
    'clave'      { Cmd-Clave }
    'logs'       { Cmd-Logs }
    'backup'     { Cmd-Backup }
    'eliminar'   { Cmd-Eliminar }
    'borrar'     { Cmd-Borrar }
    default      { Cmd-Ayuda }
}
