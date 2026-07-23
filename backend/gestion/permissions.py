from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Lectura para cualquier usuario autenticado.
    Escritura (crear/editar/eliminar) reservada a usuarios staff.
    Pensado para tablas maestras/catalogo (zonas, rubros, marcas, comodines, etc.)
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_staff)


class IsAuthenticatedReadWrite(BasePermission):
    """
    Requiere usuario autenticado tanto para lectura como para escritura.
    Pensado para tablas operativas (clientes, articulos, ventas, cobranzas, etc.)
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
