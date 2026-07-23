from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    api_root,
    GeneralViewSet,
    ZonaViewSet, CanalVentaViewSet, ProvinciaViewSet, LocalidadViewSet,
    CondicionIvaViewSet, LegajoPersonalViewSet, GrupoClienteViewSet,
    ComodinClienteViewSet, ClientesViewSet,
    RubroViewSet, SubRubroViewSet, SubMarcaViewSet, MarcaViewSet,
    ProveedorViewSet, ComodinArticuloViewSet, ArticulosViewSet,
    ComprobanteViewSet, SucursalViewSet, CondicionVentaViewSet,
    ComodinVentaViewSet, VentasViewSet, DetalleVentaViewSet,
    CobranzasViewSet,
    importar_datos,
)

router = DefaultRouter()

#---------------------------------------------------------GENERAL↓------------------------------------------------------------------
router.register(r'general', GeneralViewSet, basename='general')

#----------------------------------------------------------CLIENTES↓--------------------------------------------------------------------
router.register(r'zonas', ZonaViewSet, basename='zona')
router.register(r'canales-venta', CanalVentaViewSet, basename='canalventa')
router.register(r'provincias', ProvinciaViewSet, basename='provincia')
router.register(r'localidades', LocalidadViewSet, basename='localidad')
router.register(r'condiciones-iva', CondicionIvaViewSet, basename='condicioniva')
router.register(r'legajos-personal', LegajoPersonalViewSet, basename='legajopersonal')
router.register(r'grupos-cliente', GrupoClienteViewSet, basename='grupocliente')
router.register(r'comodines-cliente', ComodinClienteViewSet, basename='comodincliente')
router.register(r'clientes', ClientesViewSet, basename='cliente')

#----------------------------------------------------------------ARTICULOS↓------------------------------------------------------------
router.register(r'rubros', RubroViewSet, basename='rubro')
router.register(r'subrubros', SubRubroViewSet, basename='subrubro')
router.register(r'submarcas', SubMarcaViewSet, basename='submarca')
router.register(r'marcas', MarcaViewSet, basename='marca')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'comodines-articulo', ComodinArticuloViewSet, basename='comodinarticulo')
router.register(r'articulos', ArticulosViewSet, basename='articulo')

#---------------------------------------------------------------VENTAS↓-----------------------------------------------------------------
router.register(r'comprobantes', ComprobanteViewSet, basename='comprobante')
router.register(r'sucursales', SucursalViewSet, basename='sucursal')
router.register(r'condiciones-venta', CondicionVentaViewSet, basename='condicionventa')
router.register(r'comodines-venta', ComodinVentaViewSet, basename='comodinventa')
router.register(r'ventas', VentasViewSet, basename='venta')
router.register(r'detalles-venta', DetalleVentaViewSet, basename='detalleventa')

#--------------------------------------------------------COBRANZAS↓---------------------------------------------------------------------
router.register(r'cobranzas', CobranzasViewSet, basename='cobranza')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('importar_datos/', importar_datos, name='importar-datos'),
    path('', include(router.urls)),
]
