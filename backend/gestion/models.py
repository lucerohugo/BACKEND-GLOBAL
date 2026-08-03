from django.db import models


#---------------------------------------------------------GENERAL↓------------------------------------------------------------------------

class General(models.Model):
    gen_codi = models.IntegerField(primary_key=True, editable=True)
    gen_nomb = models.CharField(max_length=150, blank=True, help_text="Nombre de la empresa",null=True)
    gen_logo = models.ImageField(upload_to='logos/', blank=True, null=True, help_text="Logo")
    gen_cuit = models.CharField(max_length=20, default='00-00000000-0', help_text="CUIT de la empresa", null=True)
    gen_dire = models.CharField(max_length=150, blank=True, help_text="Direccion", null=True)
    gen_tele = models.CharField(max_length=20, blank=True, help_text="Telefono", null=True)

    def __str__(self):
        return self.gen_nomb or f"General {self.gen_codi}"




#----------------------------------------------------------CLIENTES↓--------------------------------------------------------------------------

class Zona(models.Model):
    zon_codi = models.IntegerField(primary_key=True, editable=True)
    zon_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre zona",null=True)

    def __str__(self):
        return self.zon_nomb or f"Zona {self.zon_codi}"

class CanalVenta(models.Model):
    can_codi = models.IntegerField(primary_key=True, editable=True)
    can_nomb = models.CharField(max_length=100, help_text="Nombre canal de venta",null=True)

    def __str__(self):
        return self.can_nomb or f"Canal {self.can_codi}"

class Provincia(models.Model):
    pci_codi = models.IntegerField(primary_key=True, editable=True)
    pci_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre provincia",null=True)

    def __str__(self):
        return self.pci_nomb or f"Provincia {self.pci_codi}"

class Localidad(models.Model):
    loc_codi = models.IntegerField(primary_key=True, editable=True)
    loc_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre localidad")
    loc_cpos = models.IntegerField(blank=True, null=True, help_text="Codigo postal")
    pci_codi = models.ForeignKey(Provincia, on_delete=models.PROTECT, related_name="Provincia")

    def __str__(self):
        return self.loc_nomb or f"Localidad {self.loc_codi}"


class CondicionIva(models.Model):
    civ_codi = models.IntegerField(primary_key=True, editable=True)
    civ_nomb = models.CharField(max_length=100, unique=True, null=True)

    def __str__(self):
        return self.civ_nomb


class LegajoPersonal(models.Model): #acomodar tal cual como cliente 
    per_codi = models.IntegerField(primary_key=True, editable=True)
    per_nomb = models.CharField(max_length=100, help_text="Nombre legajo personal", null=True)
    per_Ndoc = models.CharField(max_length=20, blank=True,  help_text="Nro documento", null=True,)
    Per_CUIL = models.CharField(max_length=20, blank=True, help_text="CUIL", null=True)
    Per_Celu = models.CharField(max_length=20, blank=True, help_text="Celular", null=True,)
    Per_mail = models.CharField(max_length=100, blank=True, help_text="Email", null=True)
    per_alta = models.DateField(blank=True, null=True, help_text="Fecha alta legajo", )
    per_baja = models.DateField(blank=True, null=True, help_text="Fecha baja legajo")
    Per_domi = models.CharField(max_length=100, blank=True, help_text="Dirección", null=True)
    loc_codi = models.ForeignKey(Localidad,on_delete=models.PROTECT, related_name="legajo_direccion", null=True)

    def __str__(self):
        return self.per_nomb or f"Legajo {self.per_codi}"


class GrupoCliente(models.Model):
    grc_codi = models.IntegerField(primary_key=True, editable=True)
    grc_nomb = models.CharField(max_length=100 , blank=True, help_text="Nombre grupo cliente", null=True)

    def __str__(self):
        return self.grc_nomb or f"Grupo {self.grc_codi}"


class ComodinCliente(models.Model):
    cli_ccom = models.IntegerField(primary_key=True, editable=True)
    cli_ncom = models.CharField(max_length=100, blank=True, help_text="Nombre comodin", null=True)

    def __str__(self):
        return self.cli_ncom or f"Comodin cliente {self.cli_ccom}"




class Clientes(models.Model):
    cli_codi = models.IntegerField(primary_key=True, editable=True)
    cli_nomb = models.CharField(max_length=100, help_text="Nombre del cliente", null=True)
    cli_dire = models.CharField(max_length=100, blank=True, help_text="Dirección", null=True)
    cli_celu = models.CharField(max_length=20, blank=True, help_text="Celular", null=True)
    cli_emai = models.CharField(max_length=100, blank=True, help_text="Email", null=True)
    cli_ndoc = models.CharField(max_length=20, blank=True, help_text="Numero documento", null=True)
    cli_cuit = models.CharField(max_length=20, blank=True, help_text="CUIT", null=True)
    cli_alta = models.DateField(blank=True, null=True, help_text="Fecha alta cliente", )
    cli_baja = models.DateField(blank=True, null=True, help_text="Fecha baja cliente")	
    #relaciones
    cli_ccom = models.ForeignKey(ComodinCliente, on_delete=models.PROTECT, related_name="ComodinCliente", null=True,blank=True)
    can_codi = models.ForeignKey(CanalVenta, on_delete=models.PROTECT, related_name="clientes_canal",null=True,blank=True)
    zon_codi = models.ForeignKey(Zona, on_delete=models.PROTECT, related_name="Zona",null=True,blank=True)
    grc_codi = models.ForeignKey(GrupoCliente, on_delete=models.PROTECT, related_name="clientes",null=True,blank=True)
    loc_codi = models.ForeignKey(Localidad, on_delete=models.PROTECT, related_name="clientes",null=True,blank=True)
    civ_codi = models.ForeignKey(CondicionIva, on_delete=models.PROTECT, related_name="clientes",null=True,blank=True)
    per_codi = models.ForeignKey(LegajoPersonal, on_delete=models.PROTECT, related_name="clientes",null=True,blank=True)

    def __str__(self):
        return self.cli_nomb or f"Cliente {self.cli_codi}"



#----------------------------------------------------------------ARTICULOS↓------------------------------------------------------------------


class Rubro(models.Model):
    rub_codi = models.IntegerField(primary_key=True, editable=True)
    rub_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre rubro", null=True)

    def __str__(self):
        return self.rub_nomb or f"Rubro {self.rub_codi}"


class SubRubro(models.Model):
    sru_codi = models.IntegerField(primary_key=True, editable=True)
    sru_nomb = models.CharField(max_length=100, blank=True, help_text="Subrubro nombre", null=True)
    rub_codi = models.ForeignKey(Rubro, on_delete=models.PROTECT, related_name="Rubro")

    def __str__(self):
        return self.sru_nomb or f"Subrubro {self.sru_codi}"

#nuevo agregado sin relacion
class SubMarca(models.Model):
    smar_codi = models.IntegerField(primary_key=True, editable=True)
    smar_nomb = models.CharField(max_length=100, blank=True, help_text="Sub marca", null=True)

    def __str__(self):
        return self.smar_nomb or f"Submarca {self.smar_codi}"


class Marca(models.Model):
    mar_codi = models.IntegerField(primary_key=True, editable=True)
    mar_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre marca", null=True)

    def __str__(self):
        return self.mar_nomb or f"Marca {self.mar_codi}"


class Proveedor(models.Model):
    pro_codi = models.IntegerField(primary_key=True, editable=True)
    Pro_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre proveedor", null=True)
    pro_Cuit = models.CharField(max_length=20, blank=True, help_text="CUIT", null=True)
    pro_dire = models.CharField(max_length=100, blank=True, help_text="Dirección", null=True)
    pro_celu = models.CharField(max_length=20, blank=True,  help_text="Celular", null=True,)
    pro_ibru = models.CharField(max_length=30, blank=True, help_text="Ingresos brutos", null=True)
    #relaciones
    loc_codi = models.ForeignKey(Localidad, on_delete=models.PROTECT, related_name="proveedores",null=True,blank=True)
    civ_codi = models.ForeignKey(CondicionIva, on_delete=models.PROTECT, related_name="proveedores",null=True,blank=True)

    def __str__(self):
        return self.Pro_nomb or f"Proveedor {self.pro_codi}"

class ComodinArticulo(models.Model):
    art_ccom = models.IntegerField(primary_key=True, editable=True)
    art_ncom = models.CharField(max_length=100, blank=True, help_text="Nombre comodin", null=True)

    def __str__(self):
        return self.art_ncom or f"Comodin articulo {self.art_ccom}"


class Articulos(models.Model):
    art_codi = models.IntegerField(primary_key=True, editable=True)
    art_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre articulo", null=True)
    art_medi = models.CharField(max_length=100, blank=True, help_text="Medida", null=True)                                       #REVISAR
    art_umed = models.CharField(max_length=100, blank=True, help_text="Unidad de medida", null=True)                             #REVISAR
    art_uequ = models.CharField(max_length=100, blank=True, help_text="Unidades x bulto", null=True)                             #REVISAR
    art_ucos = models.DecimalField(max_digits=30,decimal_places=2, blank=True, help_text="Costo", null=True)
    art_tprec = models.CharField(max_length=20, blank=True, help_text="Tipo precio", null=True)
    art_prec = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Precio articulo", null=True)
    art_pnet = models.DecimalField(max_digits=30, decimal_places=2, blank=True, help_text="Precio neto", null=True)
    art_pfin = models.DecimalField(max_digits=30, decimal_places=2, blank=True, help_text="Precio final", null=True)
    art_tiva = models.DecimalField(max_digits=30, decimal_places=2, default=0, help_text="IVA articulo(%)", null=True)
    art_iint = models.DecimalField(max_digits=30, decimal_places=2, default=0, help_text="Total impuesto interno", null=True)
    art_habi = models.BooleanField(default=False, help_text="Articulo habilitado/no", null=True)
    art_pesa = models.BooleanField(default=False, help_text="Pesable/no", null=True)                  
    #relaciones
    art_ccom = models.ForeignKey(ComodinArticulo, on_delete=models.PROTECT, related_name="ComodinArticulo", null=True, blank=True)
    pro_codi = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="Proveedor",null=True,blank=True)
    sru_codi = models.ForeignKey(SubRubro, on_delete=models.PROTECT, related_name="Subrubro",null=True,blank=True)
    mar_codi = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="Marca",null=True,blank=True)
    smar_codi = models.ForeignKey(SubMarca, on_delete=models.PROTECT, related_name="Submarca",null=True,blank=True)

    def __str__(self):
        return self.art_nomb or f"Articulo {self.art_codi}"


#---------------------------------------------------------------VENTAS↓-------------------------------------------------------------

class Sucursal(models.Model):
    suc_codi = models.IntegerField(primary_key=True, editable=True)
    suc_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre sucursal", null=True)

    def __str__(self):
        return self.suc_nomb or f"Sucursal {self.suc_codi}"

class ComodinVenta(models.Model):
    vta_ccom = models.IntegerField(primary_key=True, editable=True)
    vta_ncom = models.CharField(max_length=100, blank=True, help_text="Nombre comodin", null=True)

    def __str__(self):
        return self.vta_ncom or f"Comodin venta {self.vta_ccom}"

class Ventas(models.Model):
    vta_codi = models.IntegerField(primary_key=True, editable=True)
    vta_fech = models.DateField(blank=True, null=True, help_text="Fecha venta")
    vta_cvta = models.CharField(max_length=3, blank=True, help_text="Condicion de", null=True)
    vta_itoR = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Total real", null=True)
    vta_igra = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe gravado", null=True)
    vta_iexe = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe exento", null=True)
    vta_iiva = models.DecimalField(max_digits=30, decimal_places=2, help_text="IVA del artículo (%)", null=True)
    vta_iiin = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe de impuesto interno", null=True)
    vta_ibts = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Total ingreso brutos", null=True)
    #relaciones
    cli_codi = models.ForeignKey(Clientes,on_delete=models.PROTECT, related_name="ventas")
    suc_codi = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="ventas")
    vta_ccom = models.ForeignKey(ComodinVenta, on_delete=models.PROTECT, related_name="ventas", null=True, blank=True)
    gen_codi = models.ForeignKey(General, on_delete=models.PROTECT, related_name="General")
   


    #hacer restriccion sino
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cli_codi",
                    "vta_fech",
                    "vta_cvta",                    
                    "suc_codi",
                    "vta_ccom",
                    "gen_codi"
                ],
                name="uk_venta"
            )
        ]

    def __str__(self):
        return f"Venta {self.vta_codi} - {self.cli_codi}"


class DetalleVenta(models.Model):
    dvt_codi = models.BigAutoField(primary_key=True, editable=True)
    vta_codi = models.ForeignKey(Ventas, on_delete=models.PROTECT, related_name="detalles")
    art_codi = models.ForeignKey(Articulos, on_delete=models.PROTECT, related_name="detalles")
    dvt_iOri = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe original sin bonificacion", null=True)
    dvt_iuni = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Precio unitario", null=True)
    dvt_itot = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Total", null=True)
    dvt_cost = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Costo", null=True)
    dvt_iiva = models.DecimalField(max_digits=30, decimal_places=2,  help_text="detalle IVA del artículo (%)", null=True)
    dvt_igra = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe gravado", null=True)
    dvt_iexe = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe exento", null=True)
    dvt_iint = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Impuesto interno unitario", null=True)
    dvt_caPi = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Cantidad de piezas en pesables", null=True)
    dvt_cant = models.IntegerField(blank=True, null=True, help_text="detalle cantidad")


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["vta_codi", "art_codi"],
                name="uk_detalle_venta"
            )
        ]

    def __str__(self):
        return f"Detalle {self.dvt_codi} - {self.art_codi}"


#--------------------------------------------------------COBRANZAS↓-------------------------------------------------------------------------

class Cobranzas(models.Model):
    cob_codi = models.IntegerField(primary_key=True,editable=True) #este creo que va en auto
    cob_fech = models.DateField(blank=True, null=True, help_text="Fecha cobro")
    cob_itot = models.DecimalField(max_digits=30, decimal_places=2,blank=True, help_text="cobro total", null=True)
    cli_codi = models.ForeignKey(Clientes, on_delete=models.PROTECT,related_name="cobranzas",null=True,blank=True)
    suc_codi = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="cobranzas",null=True,blank=True)

    def __str__(self):
        return f"Cobro {self.cob_codi} - {self.cli_codi}"


