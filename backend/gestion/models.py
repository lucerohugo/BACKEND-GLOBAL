from django.db import models


#---------------------------------------------------------GENERAL↓------------------------------------------------------------------------

class General(models.Model):
    gen_codi = models.IntegerField(primary_key=True, editable=True)
    gen_nomb = models.CharField(max_length=150, blank=True, help_text="Nombre de la empresa")
    gen_logo = models.ImageField(upload_to='logos/', blank=True, null=True, help_text="Logo")
    gen_logB = models.ImageField(upload_to='logos/', blank=True, help_text="Logo Brix", null=True)
    gen_cuit = models.CharField(max_length=20, default='00-00000000-0', help_text="CUIT de la empresa")
    gen_dire = models.CharField(max_length=150, blank=True, help_text="Direccion")
    gen_tele = models.CharField(max_length=20, blank=True, help_text="Telefono")


   

#----------------------------------------------------------CLIENTES↓--------------------------------------------------------------------------

class Zona(models.Model):
    zon_codi = models.IntegerField(primary_key=True, editable=True)
    zon_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre zona")

class CanalVenta(models.Model):
    can_codi = models.IntegerField(primary_key=True, editable=True)
    can_nomb = models.CharField(max_length=100, help_text="Nombre canal de venta")

class Provincia(models.Model):
    pci_codi = models.IntegerField(primary_key=True, editable=True)
    pci_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre provincia")

class Localidad(models.Model):
    loc_codi = models.IntegerField(primary_key=True, editable=True)
    loc_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre localidad")
    loc_cpos = models.IntegerField(blank=True, null=True, help_text="Codigo postal")
    pci_codi = models.ForeignKey(Provincia, on_delete=models.PROTECT, related_name="Provincia")


class CondicionIva(models.Model):
    civ_codi = models.IntegerField(primary_key=True, editable=True)
    civ_nomb = models.CharField(max_length=100, unique=True)


class LegajoPersonal(models.Model):
    per_codi = models.IntegerField(primary_key=True, editable=True)
    per_nomb = models.CharField(max_length=100, help_text="Nombre legajo personal", null=True)
    per_Tdoc = models.CharField(max_length=20, blank=True,help_text="Tipo documento",null=True)
    per_Ndoc = models.CharField(max_length=20, blank=True,  help_text="Nro documento", null=True,)
    Per_CUIL = models.CharField(max_length=20, blank=True, help_text="CUIL", null=True)
    Per_Celu = models.CharField(max_length=20, blank=True, help_text="Celular", null=True,)
    Per_mail = models.CharField(max_length=100, blank=True, help_text="Email", null=True)
    Per_domi = models.CharField(max_length=100, blank=True, help_text="Dirección", null=True)
    Per_loca = models.CharField(max_length=100, blank=True, help_text="Localidad Personal", null=True) #no es FK de localidad


class GrupoCliente(models.Model):
    grc_codi = models.IntegerField(primary_key=True, editable=True)
    grc_nomb = models.CharField(max_length=100 , blank=True, help_text="Nombre grupo cliente")


class ComodinCliente(models.Model):
    cli_ccom = models.IntegerField(primary_key=True, editable=True)
    cli_ncom = models.CharField(max_length=100, blank=True, help_text="Nombre comodin", null=True)


    

class Clientes(models.Model):
    cli_codi = models.IntegerField(primary_key=True, editable=True)
    cli_nomb = models.CharField(max_length=100, help_text="Nombre del cliente")
    cli_dire = models.CharField(max_length=100, blank=True, help_text="Dirección", null=True)
    cli_celu = models.CharField(max_length=20, blank=True, help_text="Celular", null=True)
    cli_emai = models.CharField(max_length=100, blank=True, help_text="Email", null=True)
    cli_ndoc = models.CharField(max_length=20, blank=True, help_text="Numero documento", null=True)
    cli_cuit = models.CharField(max_length=20, blank=True, help_text="CUIT", null=True)
    cli_alta = models.DateField(blank=True, null=True, help_text="Fecha alta cliente")
    cli_baja = models.DateField(blank=True, null=True, help_text="Fecha baja cliente")	
    #relaciones
    cli_ccom = models.ForeignKey(ComodinCliente, on_delete=models.PROTECT, related_name="ComodinCliente")
    can_codi = models.ForeignKey(CanalVenta, on_delete=models.PROTECT, related_name="Canal de venta")
    zon_codi = models.ForeignKey(Zona, on_delete=models.PROTECT, related_name="Zona")
    grc_codi = models.ForeignKey(GrupoCliente, on_delete=models.PROTECT, related_name="Grupo cliente")
    loc_codi = models.ForeignKey(Localidad, on_delete=models.PROTECT, related_name="Localidad")
    civ_codi = models.ForeignKey(CondicionIva, on_delete=models.PROTECT, related_name="Condicion IVA")
    per_codi = models.ForeignKey(LegajoPersonal, on_delete=models.PROTECT, related_name="Legajo personal")





#----------------------------------------------------------------ARTICULOS↓------------------------------------------------------------------


class Rubro(models.Model):
    rub_codi = models.IntegerField(primary_key=True, editable=True)
    rub_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre rubro", null=True)


class SubRubro(models.Model):
    sru_codi = models.IntegerField(primary_key=True, editable=True)
    sru_nomb = models.CharField(max_length=100, blank=True, help_text="Subrubro nombre", null=True)
    rub_codi = models.ForeignKey(Rubro, on_delete=models.PROTECT, related_name="Rubro")

#nuevo agregado sin relacion
class SubMarca(models.Model):
    smar_codi = models.IntegerField(primary_key=True, editable=True)
    smar_nomb = models.CharField(max_length=100, blank=True, help_text="Sub marca", null=True)


class Marca(models.Model):
    mar_codi = models.IntegerField(primary_key=True, editable=True)
    mar_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre marca", null=True)


class Proveedor(models.Model):
    pro_codi = models.IntegerField(primary_key=True, editable=True)
    Pro_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre proveedor", null=True)
    pro_Cuit = models.CharField(max_length=20, blank=True, help_text="CUIT", null=True)
    pro_dire = models.CharField(max_length=100, blank=True, help_text="Dirección", null=True)
    pro_celu = models.CharField(max_length=20, blank=True,  help_text="Celular", null=True,)
    pro_ibru = models.CharField(max_length=30, blank=True, help_text="Ingresos brutos", null=True)
    #relaciones
    loc_codi = models.ForeignKey(Localidad, on_delete=models.PROTECT, related_name="Localidad")
    civ_codi = models.ForeignKey(CondicionIva, on_delete=models.PROTECT, related_name="Condicion IVA")

class ComodinArticulo(models.Model):
    art_ccom = models.IntegerField(primary_key=True, editable=True)
    art_ncom = models.CharField(max_length=100, blank=True, help_text="Nombre comodin", null=True)


class Articulos(models.Model):
    art_codi = models.IntegerField(primary_key=True, editable=True)
    art_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre articulo", null=True)
    art_medi = models.CharField(max_length=100, blank=True, help_text="Medida", null=True)                                       #REVISAR
    art_umed = models.CharField(max_length=100, blank=True, help_text="Unidad de medida", null=True)                             #REVISAR
    art_uequ = models.CharField(max_length=100, blank=True, help_text="Unidades x bulto", null=True)                             #REVISAR
    art_ucos = models.DecimalField(max_length=30,decimal_places=2, blank=True, help_text="Costo", null=True)                          
    art_tprec = models.CharField(max_length=20, blank=True, help_text="Tipo precio", null=True)
    art_prec = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Precio articulo", null=True)
    art_pnet = models.DecimalField(max_length=30, blank=True, help_text="Precio neto", null=True)
    art_pfin = models.DecimalField(max_length=30, blank=True, help_text="Precio final", null=True)
    art_tiva = models.DecimalField(max_digits=30, decimal_places=2, default=0, help_text="IVA articulo(%)", null=True)
    art_iint = models.DecimalField(max_length=30, decimal_places=2, default=0, help_text="Total impuesto interno")
    art_habi = models.BooleanField(default=False, help_text="Articulo habilitado/no", null=True)
    art_pesa = models.BooleanField(default=False, help_text="Pesable/no", null=True)                  
    #relaciones
    art_ccom = models.ForeignKey(ComodinArticulo, on_delete=models.PROTECT, related_name="ComodinArticulo")
    pro_codi = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="Proveedor")
    sru_codi = models.ForeignKey(SubRubro, on_delete=models.PROTECT, related_name="Subrubro")
    mar_codi = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="Marca")
    smar_codi = models.ForeignKey(SubMarca, on_delete=models.PROTECT, related_name="Submarca")



#---------------------------------------------------------------VENTAS↓-------------------------------------------------------------

class Comprobante(models.Model):
    com_codi = models.IntegerField(primary_key=True, editable=True)
    com_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre comprobante")

class Sucursal(models.Model):
    suc_codi = models.IntegerField(primary_key=True, editable=True)
    suc_nomb = models.CharField(max_length=100, blank=True, help_text="Nombre sucursal")

class CondicionVenta(models.Model):
    vta_cvta = models.CharField(primary_key=True, editable=True, max_length=3, null=True) #3 ELTRAS PRIMARY KEY 

class ComodinVenta(models.Model):
    vta_ccom = models.IntegerField(primary_key=True, editable=True)
    vta_ncom = models.CharField(max_length=100, blank=True, help_text="Nombre comodin", null=True)

class Ventas(models.Model):
    vta_codi = models.AutoField(primary_key=True, editable=True)
    vta_fech = models.DateField(blank=True, null=True, help_text="Fecha venta")
    vta_itoR = models.CharField(max_length=100, blank=True, help_text="Total real", null=True)
    vta_igra = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe gravado", null=True)
    vta_iexe = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe exento", null=True)
    vta_iiva = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe IVA", null=True)
    vta_iiin = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Importe de impuesto interno", null=True)
    vta_ibts = models.DecimalField(max_digits=30, decimal_places=2,  help_text="Total ingreso brutos", null=True)
    #relaciones
    cli_codi = models.ForeignKey(Clientes,on_delete=models.PROTECT, related_name="ventas")              
    vta_cvta = models.ForeignKey(CondicionVenta, on_delete=models.PROTECT, related_name="Condicion venta") 
    suc_codi = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="Sucursal")               
    vta_ccom = models.ForeignKey(ComodinVenta, on_delete=models.PROTECT, related_name="Comodin venta")
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

    

class DetalleVenta(models.Model):
    dvt_codi = models.BigAutoField(primary_key=True, editable=True)
    vta_codi = models.ForeignKey(Ventas, on_delete=models.PROTECT, related_name="detalles")
    art_codi = models.ForeignKey(Articulos, on_delete=models.PROTECT, related_name="detalles")
    dvt_iOri = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Importe original sin bonificacion", null=True)
    dvt_iuni = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Precio unitario", null=True)
    dvt_itot = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Total", null=True)
    dvt_cost = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Costo", null=True)
    dvt_iiva = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Importe IVA", null=True)
    dvt_igra = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Importe gravado", null=True)
    dvt_iexe = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Importe exento", null=True)
    dvt_iint = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Impuesto interno unitario", null=True)
    dvt_caPi = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Cantidad de piezas en pesables", null=True)
    dvt_cant = models.DecimalField(max_digits=30, decimal_places=6,  help_text="Cantidad", null=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["vta_codi", "art_codi"],
                name="uk_detalle_venta"
            )
        ]


#--------------------------------------------------------COBRANZAS↓-------------------------------------------------------------------------

class Cobranzas(models.Model):
    cob_codi = models.IntegerField(primary_key=True,editable=True)
    cob_fech = models.DateField(blank=True, null=True, help_text="Fecha cobro")
    cob_itot = models.DecimalField(max_length=30, decimal_places=2,blank=True, help_text="cobro total", null=True)
    cli_codi = models.ForeignKey(Clientes, on_delete=models.PROTECT,related_name="Clientes")
    suc_codi = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="Sucursal")

    
