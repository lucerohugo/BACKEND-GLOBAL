* =========================================================
* PEDIDOSSUBIDA.PRG
* Importa pedidos (ventas + detalle) desde un archivo tmp
* generado por el sistema web hacia las tablas vta / dvt
* Mismo formato que SubInfo.tmp: lineas con campos entre
* comillas separados por coma, 2do campo = tipo de registro
* =========================================================

PARAMETERS DATO1

SET DATE TO FRENCH
SET CENTURY ON
SET TALK OFF
SET SAFETY OFF
SET DELETED ON

* =========================================================
* ABRIR TABLAS
* =========================================================
* ===== aca deberia de poner el nombre real de las dbf
IF USED('vta')
    USE IN vta
ENDIF

IF USED('dvt')
    USE IN dvt
ENDIF

* ===== aca deberia de poner el nombre real de las dbf
USE vta EXCL IN 0
USE dvt EXCL IN 0

* =========================================================
* ABRIR ARCHIVO TMP
* =========================================================
ARCHI = FOPEN(DATO1,0)

IF ARCHI < 0
    WAIT WINDOW "No se pudo abrir archivo"
    RETURN
ENDIF

* =========================================================
* BUSCAR PRIMER "
* =========================================================
REG = FREAD(ARCHI,1)

DO WHILE REG <> CHR(34) AND !FEOF(ARCHI)
    REG = FREAD(ARCHI,1)
ENDDO

* =========================================================
* LECTURA PRINCIPAL
* =========================================================
DO WHILE !FEOF(ARCHI)

    IF REG <> CHR(34)
        REG = FREAD(ARCHI,1)
        LOOP
    ENDIF

    DIMENSION aCampos[1]

    nCampo = 0

    * =====================================================
    * LEER CAMPOS ENTRE COMILLAS
    * =====================================================
    DO WHILE .T.

        cValor = ""

        REG = FREAD(ARCHI,1)

        DO WHILE REG <> CHR(34) AND !FEOF(ARCHI)

            cValor = cValor + REG

            REG = FREAD(ARCHI,1)

        ENDDO

        nCampo = nCampo + 1

        DIMENSION aCampos[nCampo]

        aCampos[nCampo] = ALLTRIM(cValor)

        REG = FREAD(ARCHI,1)

        IF REG <> ","
            EXIT
        ENDIF

        REG = FREAD(ARCHI,1)

    ENDDO

    IF nCampo = 0
        LOOP
    ENDIF

    * =====================================================
    * VALIDAR TIPO
    * =====================================================
    cTipo = LOWER(aCampos[2])

    * =====================================================
    * CABECERA DE VENTA (PEDIDO)
    * =====================================================
    IF cTipo = "vta"

        SELECT vta

        APPEND BLANK

        * Codigo venta
        IF nCampo >= 3
            REPLACE vta_codi WITH VAL(aCampos[3])
        ENDIF

        * Fecha
        IF nCampo >= 4 AND !EMPTY(aCampos[4])

            NEWFech = SUBSTR(aCampos[4],9,2) + '/' + SUBSTR(aCampos[4],6,2) + '/' + SUBSTR(aCampos[4],1,4)
            REPLACE vta_fech WITH CTOD(NEWFech)

        ENDIF

        * Total real
        IF nCampo >= 5
            REPLACE vta_itoR WITH aCampos[5]
        ENDIF

        * Importe gravado
        IF nCampo >= 6
            REPLACE vta_igra WITH VAL(aCampos[6])
        ENDIF

        * Importe exento
        IF nCampo >= 7
            REPLACE vta_iexe WITH VAL(aCampos[7])
        ENDIF

        * Importe IVA
        IF nCampo >= 8
            REPLACE vta_iiva WITH VAL(aCampos[8])
        ENDIF

        * Impuesto interno
        IF nCampo >= 9
            REPLACE vta_iiin WITH VAL(aCampos[9])
        ENDIF

        * Ingresos brutos
        IF nCampo >= 10
            REPLACE vta_ibts WITH VAL(aCampos[10])
        ENDIF

        * Cliente
        IF nCampo >= 11
            REPLACE cli_codi WITH VAL(aCampos[11])
        ENDIF

        * Condicion de venta
        IF nCampo >= 12
            REPLACE vta_cvta WITH VAL(aCampos[12])
        ENDIF

        * Sucursal
        IF nCampo >= 13
            REPLACE suc_codi WITH VAL(aCampos[13])
        ENDIF

        * Comodin venta
        IF nCampo >= 14
            REPLACE vta_ccom WITH VAL(aCampos[14])
        ENDIF

        * General
        IF nCampo >= 15
            REPLACE gen_codi WITH VAL(aCampos[15])
        ENDIF

    ENDIF

    * =====================================================
    * DETALLE DE VENTA (com hace PEDIDO del anterior prg debandi)
    * =====================================================
    IF cTipo = "dvt"

        SELECT dvt

        APPEND BLANK

        * Codigo detalle
        IF nCampo >= 3
            REPLACE dvt_codi WITH VAL(aCampos[3])
        ENDIF

        * Venta
        IF nCampo >= 4
            REPLACE vta_codi WITH VAL(aCampos[4])
        ENDIF

        * Articulo
        IF nCampo >= 5
            REPLACE art_codi WITH VAL(aCampos[5])
        ENDIF

        * Importe original sin bonificacion
        IF nCampo >= 6
            REPLACE dvt_iOri WITH VAL(aCampos[6])
        ENDIF

        * Precio unitario
        IF nCampo >= 7
            REPLACE dvt_iuni WITH VAL(aCampos[7])
        ENDIF

        * Total
        IF nCampo >= 8
            REPLACE dvt_itot WITH VAL(aCampos[8])
        ENDIF

        * Costo
        IF nCampo >= 9
            REPLACE dvt_cost WITH VAL(aCampos[9])
        ENDIF

        * Importe IVA
        IF nCampo >= 10
            REPLACE dvt_iiva WITH VAL(aCampos[10])
        ENDIF

        * Importe gravado
        IF nCampo >= 11
            REPLACE dvt_igra WITH VAL(aCampos[11])
        ENDIF

        * Importe exento
        IF nCampo >= 12
            REPLACE dvt_iexe WITH VAL(aCampos[12])
        ENDIF

        * Impuesto interno unitario
        IF nCampo >= 13
            REPLACE dvt_iint WITH VAL(aCampos[13])
        ENDIF

        * Cantidad de piezas
        IF nCampo >= 14
            REPLACE dvt_caPi WITH VAL(aCampos[14])
        ENDIF

        * Cantidad
        IF nCampo >= 15
            REPLACE dvt_cant WITH VAL(aCampos[15])
        ENDIF

    ENDIF

    * =====================================================
    * SALTAR CR/LF
    * =====================================================
    DO WHILE REG = CHR(13) OR REG = CHR(10)

        REG = FREAD(ARCHI,1)

    ENDDO

ENDDO

* =========================
* CIERRE
* =========================
FCLOSE(ARCHI)
CLOSE ALL
