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
        fields = '__all__'


#----------------------------------------------------------CLIENTES↓--------------------------------------------------------------------

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = '__all__'


class CanalVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanalVenta
        fields = '__all__'


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = '__all__'


class LocalidadSerializer(serializers.ModelSerializer):
    pci_nomb = serializers.CharField(source='pci_codi.pci_nomb', read_only=True)

    class Meta:
        model = Localidad
        fields = '__all__'


class CondicionIvaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CondicionIva
        fields = '__all__'


class LegajoPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegajoPersonal
        fields = '__all__'


class GrupoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoCliente
        fields = '__all__'


class ComodinClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComodinCliente
        fields = '__all__'


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
        fields = '__all__'


#----------------------------------------------------------------ARTICULOS↓------------------------------------------------------------

class RubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields = '__all__'


class SubRubroSerializer(serializers.ModelSerializer):
    rub_nomb = serializers.CharField(source='rub_codi.rub_nomb', read_only=True)

    class Meta:
        model = SubRubro
        fields = '__all__'


class SubMarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubMarca
        fields = '__all__'


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'


class ProveedorSerializer(serializers.ModelSerializer):
    loc_nomb = serializers.CharField(source='loc_codi.loc_nomb', read_only=True)
    civ_nomb = serializers.CharField(source='civ_codi.civ_nomb', read_only=True)

    class Meta:
        model = Proveedor
        fields = '__all__'


class ComodinArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComodinArticulo
        fields = '__all__'


class ArticulosSerializer(serializers.ModelSerializer):
    art_ncom = serializers.CharField(source='art_ccom.art_ncom', read_only=True)
    pro_nomb = serializers.CharField(source='pro_codi.Pro_nomb', read_only=True)
    sru_nomb = serializers.CharField(source='sru_codi.sru_nomb', read_only=True)
    mar_nomb = serializers.CharField(source='mar_codi.mar_nomb', read_only=True)
    smar_nomb = serializers.CharField(source='smar_codi.smar_nomb', read_only=True)

    class Meta:
        model = Articulos
        fields = '__all__'


#---------------------------------------------------------------VENTAS↓-----------------------------------------------------------------



class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'


class ComodinVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComodinVenta
        fields = '__all__'


class DetalleVentaSerializer(serializers.ModelSerializer):
    art_nomb = serializers.CharField(source='art_codi.art_nomb', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = '__all__'


class VentasSerializer(serializers.ModelSerializer):
    cli_nomb = serializers.CharField(source='cli_codi.cli_nomb', read_only=True)
    suc_nomb = serializers.CharField(source='suc_codi.suc_nomb', read_only=True)
    vta_ncom = serializers.CharField(source='vta_ccom.vta_ncom', read_only=True)
    detalles = DetalleVentaSerializer(many=True, read_only=True)

    class Meta:
        model = Ventas
        fields = '__all__'


#--------------------------------------------------------COBRANZAS↓---------------------------------------------------------------------

class CobranzasSerializer(serializers.ModelSerializer):
    cli_nomb = serializers.CharField(source='cli_codi.cli_nomb', read_only=True)
    suc_nomb = serializers.CharField(source='suc_codi.suc_nomb', read_only=True)

    class Meta:
        model = Cobranzas
        fields = '__all__'
