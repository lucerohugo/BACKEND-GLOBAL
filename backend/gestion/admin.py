from django.contrib import admin
from .models import (
    General,
    Zona, CanalVenta, Provincia, Localidad, Geocodificacion, CondicionIva, LegajoPersonal, GrupoCliente, Clientes,
    Rubro, SubRubro, Calibre, Envase, Marca, Proveedor, Articulos,
    PuestoVenta, Sucursal, Comprobante, ListaPrecio, Repartidor,DetalleVenta, Ventas,
)


#-----------------------------------------------------------------GENERAL↓------------------------------------------------------------------------------------

@admin.register(General)
class GeneralAdmin(admin.ModelAdmin):
    list_display = ['gen_codi', 'gen_nomb', 'gen_cuit', 'gen_dire', 'gen_celu']
    search_fields = ['gen_codi', 'gen_nomb', 'gen_cuit']
    ordering = ['gen_nomb']


#-----------------------------------------------------------------CLIENTES↓--------------------------------------------------------------------------------

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display= ['zon_codi', 'zon_nomb']
    search_fields = ['zon_codi', 'zon_nomb']
    ordering = ['zon_nomb']


@admin.register(CanalVenta)
class CanalVentaAdmin(admin.ModelAdmin):
    list_display = ['can_codi','can_nomb']
    search_fields = ['can_codi', 'can_nomb']
    ordering = ['can_nomb']     


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display= ['pci_codi', 'pci_nomb']
    search_fields = ['pci_codi', 'pci_nomb']
    ordering = ['pci_nomb']


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ['loc_codi','loc_nomb','loc_cpos','pci_codi']
    list_filter = ['pci_codi']
    search_fields = ['loc_codi', 'loc_nomb', 'pci_codi__pci_nomb']


@admin.register(Geocodificacion)
class GeocodificacionAdmin(admin.ModelAdmin):
    list_display = ['zpl_codi','zpl_nomb']
    search_fields = ['zpl_codi', 'zpl_nomb']
    ordering = ['zpl_nomb']


@admin.register(CondicionIva)
class CondicionIvaAdmin(admin.ModelAdmin):
    list_display = ['civ_codi', 'civ_nomb']
    search_fields = ['civ_codi', 'civ_nomb']
    ordering = ['civ_nomb']


@admin.register(LegajoPersonal)
class LegajoPersonalAdmin(admin.ModelAdmin):
    list_display = ['per_codi','per_nomb'] #falta agregar campos nuevos del models
    search_fields = ['per_codi', 'per_nomb']
    ordering = ['per_codi']


@admin.register(GrupoCliente)
class GrupoClienteAdmin(admin.ModelAdmin):
    list_display = ['grc_codi', 'grc_nomb']
    search_fields = ['grc_codi', 'grc_nomb']
    ordering = ['grc_codi']


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display= ['cli_codi','cli_nomb', 'loc_codi','can_codi', 'zon_codi', 'grc_codi', 'civ_codi', 'per_codi'] #ordenar mejro con datos que faltan
    list_filter = ['loc_codi', 'can_codi', 'zon_codi', 'grc_codi', 'civ_codi', 'per_codi']
    search_fields = ['cli_nomb','cli_cuit']
    fieldsets = (
        ('Datos del Cliente', {
            'fields': ('cli_codi', 'cli_nomb', 'cli_fnac', 'cli_tdoc', 'cli_ndoc', 'cli_cuit')
        }),
        ('Contacto', {
            'fields': ('cli_emai', 'cli_tele', 'cli_dire', 'loc_codi')
        }),
        ('Información Personal', {
            'fields': ('civ_codi', ),
            'classes': ('collapse',)
        }),
        
    )


#------------------------------------------------------------------------ARTICULOS↓----------------------------------------------------------------------
@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    list_display = ['rub_codi', 'rub_nomb']
    search_fields = ['rub_codi', 'rub_nomb']
    ordering = ['rub_nomb']


@admin.register(SubRubro)
class SubRubroAdmin(admin.ModelAdmin):
    list_display = ['sru_codi', 'sru_nomb', 'rub_codi']
    list_filter = ['rub_codi']
    search_fields = ['sru_nomb']
    ordering = ['rub_codi', 'sru_nomb']


@admin.register(Calibre)
class CalibreAdmin(admin.ModelAdmin):
    list_display = ['cal_codi', 'cal_desc']
    search_fields = ['cal_codi', 'cal_desc']
    ordering = ['cal_desc']


@admin.register(Envase)
class EnvaseAdmin(admin.ModelAdmin):
    list_display = ['epv_codi', 'epv_desc']
    search_fields = ['epv_codi', 'epv_desc']
    ordering = ['epv_nomb']

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['mar_codi','mar_nomb']
    search_fields = ['mar_codi', 'mar_nomb']
    ordering = ['mar_nomb']



@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['pro_codi','Pro_nomb','pro_cuit','pro_ibru','grc_codi','loc_codi','civ_codi']
    list_filter = ['grc_codi','loc_codi','civ_codi']
    search_fields = ['pro_codi','Pro_nomb','pro_cuit']
    ordering = ['Pro_nomb']


@admin.register(Articulos)
class ArticulosAdmin(admin.ModelAdmin):
    list_display = ['art_codi','art_nomb', 'art_ucos', 'art_tprec', 'art_prec', 'art_pfin','art_tiva','art_tiva ','art_iint', 'art_habi', 'art_pesa']
    list_filter = ['epv_codi','pro_codi','sru_codi', 'cal_codi','mar_codi']
    search_fields = ['art_codi', 'art_nomb']

    ordering = ['rev_nomb']

#-------------------------------------------------------------------------VENTAS↓---------------------------------------------------------------------------------

@admin.register(PuestoVenta)
class PuestoVentaAdmin(admin.ModelAdmin):
    list_display = ['pve_codi','pve_nomb']
    search_field = ['pve_codi','pve_nomb']
    ordering = ['pve_nomb']


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ['suc_codi', 'suc_nomb']
    search_fields = ['suc_codi', 'suc_nomb']
    ordering = ['suc_nomb']


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ['com_codi', 'com_nomb']
    search_fields = ['com_codi', 'com_nomb']
    ordering = ['com_nomb']


@admin.register(ListaPrecio)
class ListaPrecioAdmin(admin.ModelAdmin):
    list_display = ['lip_codi', 'lip_nomb']
    search_fields = ['lip_codi', 'lip_nomb']
    ordering = ['lip_nomb']


@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ['rep_codi', 'rep_nomb']
    search_fields = ['rep_codi', 'rep_nomb']
    ordering = ['rep_nomb']


@admin.register(DetalleVenta)  #acomodar el venta y detalle de venta, que detalle venta sea subnivel de ventas
class DetalleVentaAdmin(admin.ModelAdmin):
    model = Ventas
    extra = 1
    fields = ['dvt_codi','vta_codi', 'dvt_cant']


@admin.register()
class VentasAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaAdmin]
    list_display = ['vta_codi', 'vta_fech','vta_cvta','vta_itoR','cli_codi', 'per_codi','gen_codi', 'pve_codi','suc_codi','rep_codi ','Fur_codi','lip_codi']
    list_filter = ['vta_codi','vta_fech',] #agregar mas datos / orden
    search_fields = ['vta_codi', 'vta_codi__vta_nomb'] #agregar mas datos / orden
    ordering = ['vta_codi'] #se puede agregar mas datos y orden a todo




#-------------------------------------------------------------------------------------------------------------------------------------------------------



    