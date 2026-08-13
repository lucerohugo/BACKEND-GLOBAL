from django.contrib import admin

from .models import (
    General,
    Zona, CanalVenta, Provincia, Localidad, CondicionIva, LegajoPersonal,
    GrupoCliente, ComodinCliente, Clientes,
    Rubro, SubRubro, SubMarca, Marca, Proveedor, ComodinArticulo, Articulos,
    Sucursal, ComodinVenta, Ventas, DetalleVenta,
    Cobranzas,
)


#-----------------------------------------------------------------GENERAL↓------------------------------------------------------------------------------------

@admin.register(General)
class GeneralAdmin(admin.ModelAdmin):
    list_display = ['gen_codi', 'gen_nomb', 'gen_cuit', 'gen_dire', 'gen_tele']
    search_fields = ['gen_codi','gen_nomb', 'gen_cuit']
    ordering = ['gen_nomb']


#-----------------------------------------------------------------CLIENTES↓--------------------------------------------------------------------------------

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ['zon_codi', 'zon_nomb']
    search_fields = ['zon_codi','zon_nomb']
    ordering = ['zon_nomb']


@admin.register(CanalVenta)
class CanalVentaAdmin(admin.ModelAdmin):
    list_display = ['can_codi', 'can_nomb']
    search_fields = ['can_codi','can_nomb']
    ordering = ['can_nomb']


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ['pci_codi', 'pci_nomb']
    search_fields = ['pci_codi','pci_nomb']
    ordering = ['pci_nomb']


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ['loc_codi', 'loc_nomb', 'loc_cpos', 'pci_codi']
    list_filter = ['pci_codi']
    search_fields = ['loc_codi', 'loc_nomb', 'pci_codi__exact', 'pci_codi__pci_nomb']
    ordering = ['loc_nomb']


@admin.register(CondicionIva)
class CondicionIvaAdmin(admin.ModelAdmin):
    list_display = ['civ_codi', 'civ_nomb']
    search_fields = ['civ_codi','civ_nomb']
    ordering = ['civ_nomb']


@admin.register(LegajoPersonal)
class LegajoPersonalAdmin(admin.ModelAdmin):
    list_display = ['per_codi', 'per_nomb', 'Per_CUIL', 'Per_Celu', 'Per_mail', 'loc_codi', 'per_alta_display', 'per_baja']
    list_filter = ['loc_codi']
    search_fields = ['per_codi','per_nomb', 'Per_CUIL', 'per_Ndoc']
    ordering = ['per_nomb']

    @admin.display(description='Per alta', ordering='per_alta')
    def per_alta_display(self, obj):
        return obj.per_alta.strftime('%d/%m/%Y') if obj.per_alta else '-'


@admin.register(GrupoCliente)
class GrupoClienteAdmin(admin.ModelAdmin):
    list_display = ['grc_codi', 'grc_nomb']
    search_fields = ['grc_codi', 'grc_nomb']
    ordering = ['grc_nomb']


@admin.register(ComodinCliente)
class ComodinClienteAdmin(admin.ModelAdmin):
    list_display = ['cli_ccom', 'cli_ncom']
    search_fields = ['cli_ccom','cli_ncom']
    ordering = ['cli_ncom']


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = [
        'cli_codi', 'cli_nomb', 'cli_cuit', 'loc_codi', 'can_codi',
        'zon_codi', 'grc_codi', 'civ_codi', 'per_codi', 'cli_alta_display', 'cli_baja',
    ]
    list_filter = ['loc_codi__pci_codi', 'can_codi', 'zon_codi', 'grc_codi', 'civ_codi']
    search_fields = ['cli_codi', 'cli_nomb', 'cli_cuit', 'cli_ndoc', 'cli_ccom__exact']
    fieldsets = (
        ('Datos del cliente', {
            'fields': ('cli_codi', 'cli_nomb', 'cli_ndoc', 'cli_cuit', 'cli_ccom')
        }),
        ('Contacto', {
            'fields': ('cli_emai', 'cli_celu', 'cli_dire', 'loc_codi')
        }),
        ('Clasificación comercial', {
            'fields': ('can_codi', 'zon_codi', 'grc_codi', 'civ_codi', 'per_codi')
        }),
        ('Alta / Baja', {
            'fields': ('cli_alta', 'cli_baja'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Cli alta', ordering='cli_alta')
    def cli_alta_display(self, obj):
        return obj.cli_alta.strftime('%d/%m/%Y') if obj.cli_alta else '-'


#------------------------------------------------------------------------ARTICULOS↓----------------------------------------------------------------------

@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    list_display = ['rub_codi', 'rub_nomb']
    search_fields = ['rub_codi','rub_nomb']
    ordering = ['rub_nomb']


@admin.register(SubRubro)
class SubRubroAdmin(admin.ModelAdmin):
    list_display = ['sru_codi', 'sru_nomb', 'rub_codi']
    list_filter = ['rub_codi']
    search_fields = ['sru_codi','sru_nomb']
    ordering = ['rub_codi', 'sru_nomb']


@admin.register(SubMarca)
class SubMarcaAdmin(admin.ModelAdmin):
    list_display = ['smar_codi', 'smar_nomb']
    search_fields = ['smar_codi','smar_nomb']
    ordering = ['smar_nomb']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['mar_codi', 'mar_nomb']
    search_fields = ['mar_codi','mar_nomb']
    ordering = ['mar_nomb']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['pro_codi', 'Pro_nomb', 'pro_Cuit', 'pro_ibru', 'loc_codi', 'civ_codi']
    list_filter = ['loc_codi', 'civ_codi']
    search_fields = ['pro_codi','Pro_nomb', 'pro_Cuit']
    ordering = ['Pro_nomb']


@admin.register(ComodinArticulo)
class ComodinArticuloAdmin(admin.ModelAdmin):
    list_display = ['art_ccom', 'art_ncom']
    search_fields = ['art_ccom','art_ncom']
    ordering = ['art_ncom']


@admin.register(Articulos)
class ArticulosAdmin(admin.ModelAdmin):
    list_display = [
        'art_codi', 'art_nomb', 'art_ucos', 'art_prec', 'art_pfin',
        'art_tiva', 'art_habi', 'art_pesa',
    ]
    list_filter = ['pro_codi', 'sru_codi', 'mar_codi', 'smar_codi', 'art_habi', 'art_pesa']
    search_fields = ['art_codi', 'art_nomb', 'art_ccom__exact']
    ordering = ['art_nomb']


#-------------------------------------------------------------------------VENTAS↓---------------------------------------------------------------------------------


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ['suc_codi', 'suc_nomb']
    search_fields = ['suc_codi','suc_nomb']
    ordering = ['suc_nomb']


@admin.register(ComodinVenta)
class ComodinVentaAdmin(admin.ModelAdmin):
    list_display = ['vta_ccom', 'vta_ncom']
    search_fields = ['vta_ccom','vta_ncom']
    ordering = ['vta_ncom']


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    fk_name = 'vta_codi'
    extra = 1
    fields = [
        'art_codi', 'dvt_cant', 'dvt_iuni', 'dvt_itot', 'dvt_iiva',
        'dvt_iOri', 'dvt_cost', 'dvt_igra', 'dvt_iexe', 'dvt_iint', 'dvt_caPi',
    ]


@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaInline]
    list_display = [
        'vta_codi', 'vta_fech', 'vta_cvta', 'cli_codi', 'suc_codi',
        'gen_codi', 'vta_igra', 'vta_iiva',
    ]
    list_filter = ['vta_fech', 'suc_codi', 'vta_cvta', 'gen_codi', 'detalles__art_codi__sru_codi']
    search_fields = ['vta_codi', 'cli_codi__cli_nomb', 'vta_ccom__exact', 'detalles__dvt_codi']
    ordering = ['-vta_fech', '-vta_codi']


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['dvt_codi', 'vta_codi', 'vta_fech_display', 'art_codi', 'dvt_cant', 'dvt_iuni', 'dvt_itot']
    list_filter = ['art_codi', 'vta_codi__vta_fech']
    search_fields = ['dvt_codi', 'art_codi__exact', 'art_codi__art_nomb', 'vta_codi__exact', 'vta_codi__cli_codi__cli_nomb']
    ordering = ['vta_codi']

    @admin.display(description='Vta fech', ordering='vta_codi__vta_fech')
    def vta_fech_display(self, obj):
        return obj.vta_codi.vta_fech


#--------------------------------------------------------COBRANZAS↓-------------------------------------------------------------------------

@admin.register(Cobranzas)
class CobranzasAdmin(admin.ModelAdmin):
    list_display = ['cob_codi', 'cob_fech', 'cli_codi', 'suc_codi', 'cob_itot']
    list_filter = ['suc_codi', 'cob_fech']
    search_fields = ['cob_codi', 'cli_codi__exact', 'cli_codi__cli_nomb']
    ordering = ['-cob_fech']
