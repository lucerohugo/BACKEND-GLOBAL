import json
import traceback

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import (
    General,
    Zona, CanalVenta, Provincia, Localidad, CondicionIva, LegajoPersonal,
    GrupoCliente, ComodinCliente, Clientes,
    Rubro, SubRubro, SubMarca, Marca, Proveedor, ComodinArticulo, Articulos,
    Sucursal, ComodinVenta, Ventas, DetalleVenta,
    Cobranzas,
)
from .permissions import IsAdminOrReadOnly, IsAuthenticatedReadWrite
from .serializers import (
    GeneralSerializer,
    ZonaSerializer, CanalVentaSerializer, ProvinciaSerializer, LocalidadSerializer,
    CondicionIvaSerializer, LegajoPersonalSerializer, GrupoClienteSerializer,
    ComodinClienteSerializer, ClientesSerializer,
    RubroSerializer, SubRubroSerializer, SubMarcaSerializer, MarcaSerializer,
    ProveedorSerializer, ComodinArticuloSerializer, ArticulosSerializer,
    SucursalSerializer,
    ComodinVentaSerializer, VentasSerializer, DetalleVentaSerializer,
    CobranzasSerializer,
)


@api_view(['GET'])
def api_root(request, format=None):
    endpoints = {
        'general': 'general-list',
        'zonas': 'zona-list',
        'canales-venta': 'canalventa-list',
        'provincias': 'provincia-list',
        'localidades': 'localidad-list',
        'condiciones-iva': 'condicioniva-list',
        'legajos-personal': 'legajopersonal-list',
        'grupos-cliente': 'grupocliente-list',
        'comodin-cliente': 'comodincliente-list',
        'clientes': 'cliente-list',
        'rubros': 'rubro-list',
        'subrubros': 'subrubro-list',
        'submarcas': 'submarca-list',
        'marcas': 'marca-list',
        'proveedores': 'proveedor-list',
        'comodin-articulo': 'comodinarticulo-list',
        'articulos': 'articulo-list',
        'sucursales': 'sucursal-list',
        'condiciones-venta': 'condicionventa-list',
        'comodin-venta': 'comodinventa-list',
        'ventas': 'venta-list',
        'detalles-venta': 'detalleventa-list',
        'cobranzas': 'cobranza-list',
    }
    return Response({
        key: reverse(name, request=request, format=format)
        for key, name in endpoints.items()
    })


# ================================================================
# BASE VIEWSET
# ================================================================

class BaseViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


# ================================================================
# BULK CREATE MIXIN (upsert por PK propia, FK -> *_id)
# ================================================================

class BulkCreateMixin:
    """
    Permite que el POST acepte un objeto unico o una lista de objetos.
    Por cada item hace update_or_create contra su propia PK (lookup_field_name),
    convirtiendo los campos FK (ej. pci_codi) a su forma *_id para Django ORM.
    """
    lookup_field_name = None

    def create(self, request, *args, **kwargs):
        data = request.data

        if not isinstance(data, list):
            data = [data]

        resultados = []

        for item in data:
            try:
                if not item.get(self.lookup_field_name):
                    resultados.append({
                        "error": f"Falta campo {self.lookup_field_name}",
                        "data": item
                    })
                    continue

                model = self.queryset.model
                data_item = item.copy()

                for field in model._meta.fields:
                    if field.is_relation and field.many_to_one:
                        fk_name = field.name
                        if fk_name in data_item:
                            data_item[f"{fk_name}_id"] = data_item.pop(fk_name)

                obj, created = model.objects.update_or_create(
                    **{self.lookup_field_name: data_item[self.lookup_field_name]},
                    defaults={k: v for k, v in data_item.items() if v is not None}
                )

                resultados.append({
                    "id": getattr(obj, self.lookup_field_name),
                    "created": created
                })

            except Exception as e:
                resultados.append({
                    "error": str(e),
                    "data": item
                })

        return Response(resultados, status=status.HTTP_200_OK)


#---------------------------------------------------------GENERAL↓------------------------------------------------------------------

class GeneralViewSet(BulkCreateMixin, BaseViewSet):
    queryset = General.objects.all()
    serializer_class = GeneralSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'gen_codi'
    search_fields = ['gen_nomb', 'gen_cuit']
    ordering = ['gen_nomb']


#----------------------------------------------------------CLIENTES↓--------------------------------------------------------------------

class ZonaViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'zon_codi'
    search_fields = ['zon_nomb']
    ordering = ['zon_nomb']


class CanalVentaViewSet(BulkCreateMixin, BaseViewSet):
    queryset = CanalVenta.objects.all()
    serializer_class = CanalVentaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'can_codi'
    search_fields = ['can_nomb']
    ordering = ['can_nomb']


class ProvinciaViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'pci_codi'
    search_fields = ['pci_nomb']
    ordering = ['pci_nomb']


class LocalidadViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'loc_codi'
    search_fields = ['loc_nomb', 'pci_codi__pci_nomb']
    ordering = ['loc_nomb']


class CondicionIvaViewSet(BulkCreateMixin, BaseViewSet):
    queryset = CondicionIva.objects.all()
    serializer_class = CondicionIvaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'civ_codi'
    search_fields = ['civ_nomb']
    ordering = ['civ_nomb']


class LegajoPersonalViewSet(BulkCreateMixin, BaseViewSet):
    queryset = LegajoPersonal.objects.all()
    serializer_class = LegajoPersonalSerializer
    permission_classes = [IsAuthenticatedReadWrite]
    lookup_field_name = 'per_codi'
    search_fields = ['per_nomb', 'Per_CUIL', 'per_Ndoc']
    ordering = ['per_nomb']


class GrupoClienteViewSet(BulkCreateMixin, BaseViewSet):
    queryset = GrupoCliente.objects.all()
    serializer_class = GrupoClienteSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'grc_codi'
    search_fields = ['grc_nomb']
    ordering = ['grc_nomb']


class ComodinClienteViewSet(BulkCreateMixin, BaseViewSet):
    queryset = ComodinCliente.objects.all()
    serializer_class = ComodinClienteSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'cli_ccom'
    search_fields = ['cli_ncom']
    ordering = ['cli_ncom']


class ClientesViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer
    permission_classes = [IsAuthenticatedReadWrite]
    lookup_field_name = 'cli_codi'
    search_fields = ['cli_nomb', 'cli_cuit', 'cli_ndoc']
    ordering = ['cli_nomb']


#----------------------------------------------------------------ARTICULOS↓------------------------------------------------------------

class RubroViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'rub_codi'
    search_fields = ['rub_nomb']
    ordering = ['rub_nomb']


class SubRubroViewSet(BulkCreateMixin, BaseViewSet):
    queryset = SubRubro.objects.all()
    serializer_class = SubRubroSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'sru_codi'
    search_fields = ['sru_nomb', 'rub_codi__rub_nomb']
    ordering = ['sru_nomb']


class SubMarcaViewSet(BulkCreateMixin, BaseViewSet):
    queryset = SubMarca.objects.all()
    serializer_class = SubMarcaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'smar_codi'
    search_fields = ['smar_nomb']
    ordering = ['smar_nomb']


class MarcaViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'mar_codi'
    search_fields = ['mar_nomb']
    ordering = ['mar_nomb']


class ProveedorViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticatedReadWrite]
    lookup_field_name = 'pro_codi'
    search_fields = ['Pro_nomb', 'pro_Cuit']
    ordering = ['Pro_nomb']


class ComodinArticuloViewSet(BulkCreateMixin, BaseViewSet):
    queryset = ComodinArticulo.objects.all()
    serializer_class = ComodinArticuloSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'art_ccom'
    search_fields = ['art_ncom']
    ordering = ['art_ncom']


class ArticulosViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Articulos.objects.all()
    serializer_class = ArticulosSerializer
    permission_classes = [IsAuthenticatedReadWrite]
    lookup_field_name = 'art_codi'
    search_fields = ['art_nomb']
    ordering = ['art_nomb']


#---------------------------------------------------------------VENTAS↓-----------------------------------------------------------------



class SucursalViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'suc_codi'
    search_fields = ['suc_nomb']
    ordering = ['suc_nomb']


class ComodinVentaViewSet(BulkCreateMixin, BaseViewSet):
    queryset = ComodinVenta.objects.all()
    serializer_class = ComodinVentaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field_name = 'vta_ccom'
    search_fields = ['vta_ncom']
    ordering = ['vta_ncom']


class VentasViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Ventas.objects.all()
    serializer_class = VentasSerializer
    permission_classes = [IsAuthenticatedReadWrite]
    lookup_field_name = 'vta_codi'
    search_fields = ['cli_codi__cli_nomb']
    ordering = ['-vta_fech', '-vta_codi']


class DetalleVentaViewSet(BulkCreateMixin, BaseViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [IsAuthenticatedReadWrite]
    lookup_field_name = 'dvt_codi'
    search_fields = ['art_codi__art_nomb', 'vta_codi__cli_codi__cli_nomb']
    ordering = ['vta_codi']


#--------------------------------------------------------COBRANZAS↓---------------------------------------------------------------------

class CobranzasViewSet(BulkCreateMixin, BaseViewSet):
    queryset = Cobranzas.objects.all()
    serializer_class = CobranzasSerializer
    permission_classes = [IsAuthenticatedReadWrite]
    lookup_field_name = 'cob_codi'
    search_fields = ['cli_codi__cli_nomb']
    ordering = ['-cob_fech']


#--------------------------------------------------------IMPORTAR DATOS↓---------------------------------------------------------------


MODELOS = {
    "general": (General, "gen_codi"),
    "zonas": (Zona, "zon_codi"),
    "canales_venta": (CanalVenta, "can_codi"),
    "provincias": (Provincia, "pci_codi"),
    "condiciones_iva": (CondicionIva, "civ_codi"),
    "legajos_personal": (LegajoPersonal, "per_codi"),
    "grupos_cliente": (GrupoCliente, "grc_codi"),
    "comodines_cliente": (ComodinCliente, "cli_ccom"),
    "localidades": (Localidad, "loc_codi"),                # depende de Provincia
    "rubros": (Rubro, "rub_codi"),
    "submarcas": (SubMarca, "smar_codi"),
    "marcas": (Marca, "mar_codi"),
    "sucursales": (Sucursal, "suc_codi"),
    "comodines_venta": (ComodinVenta, "vta_ccom"),
    "comodines_articulo": (ComodinArticulo, "art_ccom"),
    "clientes": (Clientes, "cli_codi"),                    # depende de ComodinCliente, CanalVenta, Zona, GrupoCliente, Localidad, CondicionIva, LegajoPersonal
    "subrubros": (SubRubro, "sru_codi"),                   # depende de Rubro
    "proveedores": (Proveedor, "pro_codi"),                # depende de Localidad, CondicionIva
    "articulos": (Articulos, "art_codi"),                  # depende de ComodinArticulo, Proveedor, SubRubro, Marca, SubMarca
    "ventas": (Ventas, "vta_codi"),                        # depende de Clientes, Sucursal, ComodinVenta, General
    "detalles_venta": (DetalleVenta, "dvt_codi"),          # depende de Ventas, Articulos
    "cobranzas": (Cobranzas, "cob_codi"),                  # depende de Clientes, Sucursal
}


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def importar_datos(request):
    """
    POST /importar_datos/
    Importa datos en bulk desde JSON.
    Body esperado: {"clientes": [...], "articulos": [...], ...}
    con una clave por cada modelo definido en MODELOS
    """

    if request.method == 'OPTIONS':
        return JsonResponse({'status': 'ok'})

    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'detail': f'JSON inválido: {str(e)}'
        }, status=400)

    resultados = {}

    try:
        # =====================================================
        # TABLA POR TABLA (en orden de dependencias)
        # =====================================================
        for key, (model, lookup) in MODELOS.items():

            items = data.get(key, [])

            resultados[key] = {
                "total": len(items),
                "ok": 0,
                "error": 0,
                "detalle": [],
            }

            # =====================================================
            # REGISTRO POR REGISTRO
            # =====================================================
            for item in items:
                try:
                    # ============================================
                    # TRANSACCION POR REGISTRO
                    # ============================================
                    with transaction.atomic():

                        data_item = (
                            item.copy()
                            if isinstance(item, dict)
                            else dict(item)
                        )

                        # ============================================
                        # LIMPIAR STRINGS / VACIOS -> NULL
                        # ============================================
                        for k, v in list(data_item.items()):
                            if isinstance(v, str):
                                v = v.strip()
                                if v == "":
                                    v = None
                            data_item[k] = v

                        # ============================================
                        # FK -> *_id
                        # ============================================
                        for field in model._meta.fields:
                            if field.is_relation and field.many_to_one:
                                fk_name = field.name
                                if fk_name in data_item:
                                    data_item[f"{fk_name}_id"] = (
                                        data_item.pop(fk_name)
                                    )

                        # ============================================
                        # LOOKUP (PK del propio modelo)
                        # ============================================

                        # ============================================
                        # DETALLE VENTA (NO TIENE dvt_codi)
                        # ============================================
                        if model == DetalleVenta:

                            obj, created = DetalleVenta.objects.update_or_create(
                                vta_codi_id=data_item.pop("vta_codi_id"),
                                art_codi_id=data_item.pop("art_codi_id"),
                                defaults=data_item,
                            )

                        # ============================================
                        # RESTO DE LOS MODELOS
                        # ============================================
                        else:

                            lookup_value = (
                                data_item.get(lookup)
                                or data_item.get(f"{lookup}_id")
                            )

                            if lookup_value is None:
                                resultados[key]["error"] += 1
                                resultados[key]["detalle"].append({
                                    "error": f"Falta campo {lookup}",
                                    "data": item,
                                })
                                continue

                            lookup_field = (
                                f"{lookup}_id"
                                if any(
                                    f.name == lookup and f.is_relation
                                    for f in model._meta.fields
                                )
                                else lookup
                            )

                            data_item.pop(lookup, None)
                            data_item.pop(f"{lookup}_id", None)

                            obj, created = model.objects.update_or_create(
                                **{lookup_field: lookup_value},
                                defaults=data_item,
                            )

                        resultados[key]["ok"] += 1

                except Exception as e:
                    print("\n" + "=" * 100)
                    print(f"ERROR IMPORTANDO TABLA: {key}")
                    print(f"MODELO: {model.__name__}")
                    print(f"LOOKUP: {lookup}")
                    print("ITEM ORIGINAL:")
                    print(item)
                    print("DATA_ITEM:")
                    print(data_item)
                    print("\nTRACEBACK:")
                    traceback.print_exc()
                    print("=" * 100 + "\n")

                    resultados[key]["error"] += 1
                    resultados[key]["detalle"].append({
                        "error": str(e),
                        "data": item,
                    })

        return JsonResponse({
            "success": True,
            "resultados": resultados,
        }, status=200)

    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "error": str(e),
        }, status=500)
