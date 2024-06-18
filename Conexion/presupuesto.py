class Presupuesto:
    def __init__(self, codpresupuesto=None, fecha=None, codcliente=None, cliente=None, subtotal=None,
                 iva=None, total=None, formapago=None, fecha_vto=None):
        self._codpresupuesto = codpresupuesto
        self._fecha = fecha
        self._codcliente = codcliente
        self._cliente = cliente
        self._subtotal = subtotal
        self._iva = iva
        self._total = total
        self._formapago = formapago
        self._fecha_vto = fecha_vto

    def __str__(self):
        return f'''
            Código de Presupuesto: {self._codpresupuesto}
            Fecha: {self._fecha}
            Código de Cliente: {self._codcliente}
            Cliente: {self._cliente}
            Subtotal: {self._subtotal}
            IVA: {self._iva}
            Total: {self._total}
            Forma de Pago: {self._formapago}
            Fecha de Vencimiento: {self._fecha_vto}
        '''

    @property
    def codpresupuesto(self):
        return self._codpresupuesto

    @codpresupuesto.setter
    def codpresupuesto(self, codpresupuesto):
        self._codpresupuesto = codpresupuesto

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
    def fecha_vto(self):
        return self._fecha_vto

    @fecha_vto.setter
    def fecha_vto(self, fecha_vto):
        self._fecha_vto = fecha_vto

