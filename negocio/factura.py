
class Factura:
    def __init__(self, serie=None, codfactura=None, fecha=None, codcliente=None, cliente=None, estado=None, subtotal=None, iva=None, total=None, formapago=None, tipo=None, entrega=None):
        self._serie = serie
        self._codfactura = codfactura
        self._fecha = fecha
        self._codcliente = codcliente
        self._cliente = cliente
        self._estado = estado
        self._subtotal = subtotal
        self._iva = iva
        self._total = total
        self._formapago = formapago
        self._tipo = tipo
        self._entrega = entrega


    def __str__(self):
        return f'''
            Serie: {self._serie}
            N° Factura: {self._codfactura}
            Fecha: {self._fecha}
            Cod. Cliente: {self._codcliente}
            Cliente: {self._cliente}
            Estado: {self._estado}
            Subtotal: {self._subtotal}
            IVA: {self._iva}
            Total: {self._total}
            Forma de Pago: {self._formapago}
            Tipo: {self._tipo}
            Entrega: {self._entrega}
        '''

    def __iter__(self):
        yield self.serie
        yield self.codfactura
        yield self.fecha
        yield self.codcliente
        yield self.cliente
        yield self.estado
        yield self.subtotal
        yield self.iva
        yield self.total
        yield self.formapago
        yield self.tipo
        yield self.entrega

    @property
    def serie(self):
        return self._serie

    @serie.setter
    def serie(self, serie):
        self._serie = serie

    @property
    def codfactura(self):
        return self._codfactura

    @codfactura.setter
    def codfactura(self, codfactura):
        self._codfactura = codfactura

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = fecha

    @property
    def codcliente(self):
        return self._codcliente

    @codcliente.setter
    def codcliente(self, codcliente):
        self._codcliente = codcliente

    @property
    def cliente(self):
        return self._cliente

    @cliente.setter
    def cliente(self, cliente):
        self._cliente = cliente

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, estado):
        self._estado = estado

    @property
    def subtotal(self):
        return self._subtotal

    @subtotal.setter
    def subtotal(self, subtotal):
        self._subtotal = subtotal

    @property
    def iva(self):
        return self._iva

    @iva.setter
    def iva(self, iva):
        self._iva = iva

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, total):
        self._total = total

    @property
    def formapago(self):
        return self._formapago

    @formapago.setter
    def formapago(self, formapago):
        self._formapago = formapago

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = tipo

    @property
    def entrega(self):
        return self._entrega

    @entrega.setter
    def entrega(self, entrega):
        self._entrega = entrega





