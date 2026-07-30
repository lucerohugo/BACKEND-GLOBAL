import sys
import os
import json
import requests
import csv
from datetime import datetime
from decimal import Decimal
# usar esta version

# ============================================================
# CONFIG
# ============================================================

BASE_URL = "http://localhost:8000/api"

URL = f"{BASE_URL}/importar_datos/"

RUTA_TMP = "SubInfo.tmp"

SALIDA = "banderasubASR.tmp"

CHECKPOINT = "sync_status.json"

TIMEOUT = 300

TAM_LOTE = 500

HEADERS = {
    "Content-Type": "application/json; charset=utf-8"
}

# ============================================================
# GENERAR SALIDA
# ============================================================

def generar_salida(estado):

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(str(estado))


# ============================================================
# MAPEO TMP -> JSON
# ============================================================
# Los codigos de tipo de linea (clave de MAPEO) son PLACEHOLDERS
# armados a partir de los prefijos de gestion/models.py. Confirmar
# contra los codigos reales que emite el sistema que genera el .tmp
# y ajustar si no coinciden.
# El orden de los campos respeta el orden declarado en cada modelo.

MAPEO = {

    "gen": [
        ("gen_codi", int),
        ("gen_nomb", str),
        ("gen_cuit", str),
        ("gen_dire", str),
        ("gen_tele", str),
    ],

    "zona": [
        ("zon_codi", int),
        ("zon_nomb", str),
    ],

    "canv": [
        ("can_codi", int),
        ("can_nomb", str),
    ],

    "pci": [
        ("pci_codi", int),
        ("pci_nomb", str),
    ],

    "civa": [
        ("civ_codi", int),
        ("civ_nomb", str),
    ],

    "per": [
        ("per_codi", int),
        ("per_nomb", str),
        ("per_Ndoc", str),
        ("Per_CUIL", str),
        ("Per_Celu", str),
        ("Per_mail", str),
        ("Per_domi", str),
        ("Per_loca", str),
    ],

    "grc": [
        ("grc_codi", int),
        ("grc_nomb", str),
    ],

    
    "ccli": [
        ("cli_ccom", int),
        ("cli_ncom", str),
    ],

    "loca": [
        ("loc_codi", int),
        ("loc_nomb", str),
        ("loc_cpos", int),
        ("pci_codi", int),
    ],

    "rub": [
        ("rub_codi", int),
        ("rub_nomb", str),
    ],

    "sru": [
        ("sru_codi", int),
        ("sru_nomb", str),
        ("rub_codi", int),
    ],

    "smar": [
        ("smar_codi", int),
        ("smar_nomb", str),
    ],

    "marc": [
        ("mar_codi", int),
        ("mar_nomb", str),
    ],

    "prov": [
        ("pro_codi", int),
        ("Pro_nomb", str),
        ("pro_Cuit", str),
        ("pro_dire", str),
        ("pro_celu", str),
        ("pro_ibru", str),
        ("loc_codi", int),
        ("civ_codi", int),
    ],


     
    "ccoma": [
        ("art_ccom", int),
        ("art_ncom", str),
    ],

    "clie": [
        ("cli_codi", int),
        ("cli_nomb", str),
        ("cli_dire", str),
        ("cli_celu", str),
        ("cli_emai", str),
        ("cli_ndoc", str),
        ("cli_cuit", str),
        ("cli_alta", str),
        ("cli_baja", str),
        ("cli_ccom", int), #comodin cliente
        ("can_codi", int),
        ("zon_codi", int),
        ("grc_codi", int),
        ("loc_codi", int),
        ("civ_codi", int),
        ("per_codi", int),
    ],

    "arbi": [
        ("art_codi", int),
        ("art_nomb", str),
        ("art_medi", int),
        ("art_umed", int),
        ("art_uequ", int),
        ("art_ucos", int),
        ("art_tprec", str),
        ("art_prec", int),
        ("art_pnet", int),
        ("art_pfin", int),
        ("art_tiva", str),
        ("art_iint", int),
        ("art_habi", bool),
        ("art_pesa", bool),
        ("art_ccom", int), 
        ("pro_codi", int),
        ("sru_codi", int),
        ("mar_codi", int),
        ("smar_codi", int),
    ],

    "suc": [
        ("suc_codi", int),
        ("suc_nomb", str),
    ],

    # "cvta": [
    #     ("vta_cvta", str),
    # ],

    #comodin de ventas 
    "ccov": [
        ("vta_ccom", int),
        ("vta_ncom", str),
    ],

    "vta": [
        ("vta_codi", int),
        ("vta_fech", str),
        ("vta_cvta", str),
        ("vta_itoR", int),
        ("vta_igra", int),
        ("vta_iexe", int),
        ("vta_iiva", Decimal),
        ("vta_iiin", str),
        ("vta_ibts", str),
        ("cli_codi", int),
        ("suc_codi", int),
        ("vta_ccom", int), #comodin venta
        ("gen_codi", int),
    ],

    "dvt": [
        # ("dvt_codi", int), #es autonumerico en el back
        ("vta_codi", int),
        ("art_codi", int),
        ("dvt_iOri", str),
        ("dvt_iuni", str),
        ("dvt_itot", str),
        ("dvt_cost", str),
        ("dvt_iiva", str),
        ("dvt_igra", str),
        ("dvt_iexe", str),
        ("dvt_iint", str),
        ("dvt_caPi", str),
        ("dvt_cant", int),
    ],

    "cob": [
        ("cob_codi", int),
        ("cob_fech", str),
        ("cob_itot", str),
        ("cli_codi", int),
        ("suc_codi", int),
    ],
}

# ============================================================
# DESTINOS JSON
# ============================================================
# Deben coincidir exactamente con las claves de MODELOS en
# gestion/views.py (importar_datos), y se listan en orden de
# dependencia (igual que MODELOS) para que el envio por lotes
# respete las FK.

DESTINOS = {

    "gen": "general",
    "zona": "zonas",
    "canv": "canales_venta",
    "pci": "provincias",
    "civa": "condiciones_iva",
    "per": "legajos_personal",
    "grc": "grupos_cliente",
    "ccli": "comodines_cliente",
    "loca": "localidades",
    "rub": "rubros",
    "smar": "submarcas",
    "marc": "marcas",
    "suc": "sucursales",
    "ccov": "comodines_venta",
    "ccoma": "comodines_articulo",
    "clie": "clientes",
    "sru": "subrubros",
    "prov": "proveedores",
    "arbi": "articulos",
    "vta": "ventas",
    "dvt": "detalles_venta",
    "cob": "cobranzas",
}

# ============================================================
# CONVERTIR TIPOS
# ============================================================

def convertir(valor, tipo):

    if valor is None:
        return None

    valor = str(valor).strip()

    if valor == "":
        return ""

    try:

        if tipo == int:

            valor = valor.replace(",", ".")

            return int(float(valor))

        if tipo == bool:

            return valor.lower() in (
                "true",
                "1",
                "t",
                "s",
                "si",
                "y"
            )

        # Normalizar números decimales
        valor = valor.replace(",", ".")

        try:
            numero = Decimal(valor)
            return str(numero.normalize())
        except:
            pass

        return valor

    except:

        return ""

    try:

        if tipo == int:

            valor = valor.replace(",", ".")

            return int(float(valor))

        if tipo == bool:

            return valor.lower() in (
                "true",
                "1",
                "t",
                "s",
                "si",
                "y"
            )

        return valor

    except:

        return ""


# ============================================================
# REPARAR COMILLAS EN ARTICULOS
# ============================================================

def reparar_linea_articulo(linea):

    if ',"arbi",' not in linea:
        return linea

    # buscar el inicio del nombre
    pos = linea.find(',"arbi",')

    if pos == -1:
        return linea

    # buscar la tercera comilla
    partes = linea.split('"')

    if len(partes) < 8:
        return linea

    resultado = ""
    dentro_nombre = False
    contador = 0

    i = 0
    while i < len(linea):

        c = linea[i]

        if c == '"':

            contador += 1

            # inicio nombre
            if contador == 5:
                dentro_nombre = True
                resultado += c
                i += 1
                continue

            # fin nombre
            if dentro_nombre:

                siguiente = linea[i + 1:i + 3]

                # si viene coma despues -> fin campo real
                if siguiente == ',"':
                    dentro_nombre = False
                    resultado += c
                    i += 1
                    continue

                # si NO -> es pulgadas internas
                resultado += '""'
                i += 1
                continue

        resultado += c
        i += 1

    return resultado


# ============================================================
# PARSER CSV
# ============================================================

def parse_line(line):

    try:

        reader = csv.reader(
            [line],
            delimiter=',',
            quotechar='"',
            skipinitialspace=False
        )

        return next(reader)

    except Exception as e:

        print("===================================")
        print("ERROR PARSEANDO")
        print(line)
        print(e)

        return []


# ============================================================
# LIMPIAR TEXTO
# ============================================================

def limpiar_texto(valor):

    if not isinstance(valor, str):
        return valor

    valor = valor.replace("\x00", "")
    valor = valor.replace("�", "")
    valor = valor.replace("\r", "")
    valor = valor.replace("\n", "")

    return valor.strip()


#tomo todo tipo de fechas 
def normalizar_fecha(valor):

    if valor is None:
        return None

    valor = str(valor).strip()

    if valor == "":
        return None

    formatos = [
        "%Y-%m-%d",   # 2026-07-27
        "%m/%d/%y",   # 07/24/26
        "%m/%d/%Y",   # 07/24/2026
        "%d/%m/%Y",   # 24/07/2026
        "%d/%m/%y",   # 24/07/26
        "%d-%m-%Y",
        "%d-%m-%y",
        "%Y/%m/%d",
    ]

    for formato in formatos:
        try:
            fecha = datetime.strptime(valor, formato)
            return fecha.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return valor


# ============================================================
# LEER TMP
# ============================================================

def leer_tmp(ruta):

    data_final = {destino: [] for destino in DESTINOS.values()}

    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:

        for numero_linea, line in enumerate(f, start=1):

            line = line.strip()

            if not line:
                continue

            # reparar pulgadas internas
            line = reparar_linea_articulo(line)

            row = parse_line(line)

            if len(row) < 3:
                continue

            tipo = row[1].lower()

            if tipo not in MAPEO:
                continue

            estructura = MAPEO[tipo]

            registro = {}

            base = 2

            for i, (campo, tipo_dato) in enumerate(estructura):

                pos = i + base

                if pos >= len(row):

                    registro[campo] = ""
                    continue

                valor = convertir(
                    row[pos],
                    tipo_dato
                )

                valor = limpiar_texto(valor)

                if campo.endswith("_fech") or campo.endswith("_alta") or campo.endswith("_baja"):
                    valor = normalizar_fecha(valor)

                registro[campo] = valor

            destino = DESTINOS[tipo]

            data_final[destino].append(registro)

    return data_final


# ============================================================
# CHECKPOINTS
# ============================================================

def cargar_checkpoint():

    if not os.path.exists(CHECKPOINT):
        return {}

    try:

        with open(CHECKPOINT, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return {}


def guardar_checkpoint(data):

    with open(CHECKPOINT, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# ENVIAR API
# ============================================================

def enviar_api(tabla, registros):

    try:

        payload = {
            tabla: registros
        }

        r = requests.post(
            URL,
            headers=HEADERS,
            json=payload,
            timeout=TIMEOUT
        )

        print("===================================")
        print("TABLA:", tabla)
        print("STATUS:", r.status_code)

        try:

            respuesta = r.json()

            print(json.dumps(
                respuesta,
                indent=4,
                ensure_ascii=False
            ))

        except:

            print(r.text)

        return r.status_code in (200, 201)

    except Exception as e:

        print("ERROR REQUEST:", e)

        return False


# ============================================================
# ENVIAR LOTES
# ============================================================

def enviar_por_lotes(tabla, registros, checkpoint):

    total = len(registros)

    if total == 0:
        return True

    inicio = checkpoint.get(tabla, 0)

    print("===================================")
    print(f"ENVIANDO {tabla.upper()}")
    print(f"TOTAL REGISTROS: {total}")
    print(f"REANUDANDO DESDE: {inicio}")

    for i in range(inicio, total, TAM_LOTE):

        lote = registros[i:i + TAM_LOTE]

        print("-----------------------------------")
        print(f"LOTE {i} A {i + len(lote)}")

        ok = enviar_api(tabla, lote)

        if not ok:
            return False

        checkpoint[tabla] = i + len(lote)

        guardar_checkpoint(checkpoint)

        print(f"CHECKPOINT {tabla}: {checkpoint[tabla]}")

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    data = leer_tmp(RUTA_TMP)

    checkpoint = cargar_checkpoint()

    for tabla, registros in data.items():

        if not registros:
            continue

        total = len(registros)

        actual = checkpoint.get(tabla, 0)

        if actual >= total:

            print(f"{tabla} YA SINCRONIZADA")
            continue

        ok = enviar_por_lotes(
            tabla,
            registros,
            checkpoint
        )

        if not ok:

            print(f"ERROR EN {tabla}")

            generar_salida(0)

            sys.exit(0)

    print("===================================")
    print("SINCRONIZACION COMPLETA")
    print("===================================")

    if os.path.exists(CHECKPOINT):
        os.remove(CHECKPOINT)

    generar_salida(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
