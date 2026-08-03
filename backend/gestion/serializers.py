from rest_framework import serializers

from .models import (
    General,
    Zona, CanalVenta, Provincia, Localidad, CondicionIva, LegajoPersonal,
    GrupoCliente, ComodinCliente, Clientes,
    Rubro, SubRubro, SubMarca, Marca, Proveedor, ComodinArticulo, Articulos,
    Sucursal, ComodinVenta, Ventas, DetalleVenta,
    Cobranzas,
)


#---------------------------------------------------------GENERAL↓------------------------------------------------------------------

class GeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = General
        fields = [
            'gen_codi', 'gen_nomb', 'gen_logo', 'gen_cuit',
            'gen_dire', 'gen_tele',
        ]


#----------------------------------------------------------CLIENTES↓--------------------------------------------------------------------

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = ['zon_codi', 'zon_nomb']


class CanalVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanalVenta
        fields = ['can_codi', 'can_nomb']


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = ['pci_codi', 'pci_nomb']


class LocalidadSerializer(serializers.ModelSerializer):
    pci_nomb = serializers.CharField(source='pci_codi.pci_nomb', read_only=True)

    class Meta:
        model = Localidad
        fields = ['loc_codi', 'loc_nomb', 'loc_cpos', 'pci_codi', 'pci_nomb']


class CondicionIvaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CondicionIva
        fields = ['civ_codi', 'civ_nomb']


class LegajoPersonalSerializer(serializers.ModelSerializer):
    loc_nomb = serializers.CharField(source='loc_codi.loc_nomb', read_only=True)

    class Meta:
        model = LegajoPersonal
        fields = [
            'per_codi', 'per_nomb', 'per_Ndoc', 'Per_CUIL', 'Per_Celu',
            'Per_mail', 'per_alta', 'per_baja', 'Per_domi', 'loc_codi', 'loc_nomb',
        ]


class GrupoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoCliente
        fields = ['grc_codi', 'grc_nomb']


class ComodinClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComodinCliente
        fields = ['cli_ccom', 'cli_ncom']


class ClientesSerializer(serializers.ModelSerializer):
    cli_ncom = serializers.CharField(source='cli_ccom.cli_ncom', read_only=True)
    can_nomb = serializers.CharField(source='can_codi.can_nomb', read_only=True)
    zon_nomb = serializers.CharField(source='zon_codi.zon_nomb', read_only=True)
    grc_nomb = serializers.CharField(source='grc_codi.grc_nomb', read_only=True)
    loc_nomb = serializers.CharField(source='loc_codi.loc_nomb', read_only=True)
    civ_nomb = serializers.CharField(source='civ_codi.civ_nomb', read_only=True)
    per_nomb = serializers.CharField(source='per_codi.per_nomb', read_only=True)

    class Meta:
        model = Clientes
        fields = [
            'cli_codi', 'cli_nomb', 'cli_dire', 'cli_celu', 'cli_emai',
            'cli_ndoc', 'cli_cuit', 'cli_alta', 'cli_baja',
            'cli_ccom', 'can_codi', 'zon_codi', 'grc_codi', 'loc_codi', 'civ_codi', 'per_codi',
            'cli_ncom', 'can_nomb', 'zon_nomb', 'grc_nomb', 'loc_nomb', 'civ_nomb', 'per_nomb',
        ]


#----------------------------------------------------------------ARTICULOS↓------------------------------------------------------------

class RubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields = ['rub_codi', 'rub_nomb']


class SubRubroSerializer(serializers.ModelSerializer):
    rub_nomb = serializers.CharField(source='rub_codi.rub_nomb', read_only=True)

    class Meta:
        model = SubRubro
        fields = ['sru_codi', 'sru_nomb', 'rub_codi', 'rub_nomb']


class SubMarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubMarca
        fields = ['smar_codi', 'smar_nomb']


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['mar_codi', 'mar_nomb']


class ProveedorSerializer(serializers.ModelSerializer):
    loc_nomb = serializers.CharField(source='loc_codi.loc_nomb', read_only=True)
    civ_nomb = serializers.CharField(source='civ_codi.civ_nomb', read_only=True)

    class Meta:
        model = Proveedor
        fields = [
            'pro_codi', 'Pro_nomb', 'pro_Cuit', 'pro_dire', 'pro_celu', 'pro_ibru',
            'loc_codi', 'civ_codi',
            'loc_nomb', 'civ_nomb',
        ]


class ComodinArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComodinArticulo
        fields = ['art_ccom', 'art_ncom']


class ArticulosSerializer(serializers.ModelSerializer):
    art_ncom = serializers.CharField(source='art_ccom.art_ncom', read_only=True)
    pro_nomb = serializers.CharField(source='pro_codi.Pro_nomb', read_only=True)
    sru_nomb = serializers.CharField(source='sru_codi.sru_nomb', read_only=True)
    mar_nomb = serializers.CharField(source='mar_codi.mar_nomb', read_only=True)
    smar_nomb = serializers.CharField(source='smar_codi.smar_nomb', read_only=True)

    class Meta:
        model = Articulos
        fields = [
            'art_codi', 'art_nomb', 'art_medi', 'art_umed', 'art_uequ', 'art_ucos',
            'art_tprec', 'art_prec', 'art_pnet', 'art_pfin', 'art_tiva', 'art_iint',
            'art_habi', 'art_pesa',
            'art_ccom', 'pro_codi', 'sru_codi', 'mar_codi', 'smar_codi',
            'art_ncom', 'pro_nomb', 'sru_nomb', 'mar_nomb', 'smar_nomb',
        ]


#---------------------------------------------------------------VENTAS↓-----------------------------------------------------------------



class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ['suc_codi', 'suc_nomb']


class ComodinVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComodinVenta
        fields = ['vta_ccom', 'vta_ncom']


class DetalleVentaSerializer(serializers.ModelSerializer):
    art_nomb = serializers.CharField(source='art_codi.art_nomb', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = [
            'dvt_codi', 'vta_codi', 'art_codi',
            'dvt_iOri', 'dvt_iuni', 'dvt_itot', 'dvt_cost', 'dvt_iiva',
            'dvt_igra', 'dvt_iexe', 'dvt_iint', 'dvt_caPi', 'dvt_cant',
            'art_nomb',
        ]


class VentasSerializer(serializers.ModelSerializer):
    cli_nomb = serializers.CharField(source='cli_codi.cli_nomb', read_only=True)
    suc_nomb = serializers.CharField(source='suc_codi.suc_nomb', read_only=True)
    vta_ncom = serializers.CharField(source='vta_ccom.vta_ncom', read_only=True)
    detalles = DetalleVentaSerializer(many=True, read_only=True)

    class Meta:
        model = Ventas
        fields = [
            'vta_codi', 'vta_fech', 'vta_cvta', 'vta_itoR', 'vta_igra',
            'vta_iexe', 'vta_iiva', 'vta_iiin', 'vta_ibts',
            'cli_codi', 'suc_codi', 'vta_ccom', 'gen_codi',
            'cli_nomb', 'suc_nomb', 'vta_ncom',
            'detalles',
        ]


#--------------------------------------------------------COBRANZAS↓---------------------------------------------------------------------

class CobranzasSerializer(serializers.ModelSerializer):
    cli_nomb = serializers.CharField(source='cli_codi.cli_nomb', read_only=True)
    suc_nomb = serializers.CharField(source='suc_codi.suc_nomb', read_only=True)

    class Meta:
        model = Cobranzas
        fields = [
            'cob_codi', 'cob_fech', 'cob_itot', 'cli_codi', 'suc_codi',
            'cli_nomb', 'suc_nomb',
        ]
