class detallePresupuesto:
    def __init__(self, codpresupuesto=None, codarticulo=None, descripcion=None, cantidad=None, precio_unitario=None, subtotal=None, importe_iva=None):
        self._codpresupuesto = codpresupuesto
        self._codarticulo = codarticulo
        self._descripcion = descripcion
        self._cantidad = cantidad
        self._precio_unitario = precio_unitario
        self._subtotal = subtotal
        self._importe_iva = importe_iva

    def __str__(self):
        return f'''
            Código de Presupuesto: {self._codpresupuesto}
            Código de Artículo: {self._codarticulo}
            Descripción: {self._descripcion}
            Cantidad: {self._cantidad}
            Precio de Venta: {self._precio_unitario}
            Importe: {self._subtotal}
            IVA: {self._importe_iva}
        '''

    @property
    def codpresupuesto(self):
        return self._codpresupuesto

    @codpresupuesto.setter
    def codpresupuesto(self, codpresupuesto):
        self._codpresupuesto = codpresupuesto

    @property
    def codarticulo(self):
        return self._codarticulo

    @codarticulo.setter
    def codarticulo(self, codarticulo):
        self._codarticulo = codarticulo

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, descripcion):
        self._descripcion = descripcion

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, cantidad):
        self._cantidad = cantidad

    @property
    def precio_unitario(self):
        return self._precio_unitario

    @precio_unitario.setter
    def precio_unitario(self, precio_unitario):
        self._precio_unitario = precio_unitario

    @property
    def subtotal(self):
        return self._subtotal

    @subtotal.setter
    def subtotal(self, subtotal):
        self._subtotal = subtotal

    @property
    def importe_iva(self):
        return self._importe_iva

    @importe_iva.setter
    def importe_iva(self, importe_iva):
        self._importe_iva = importe_iva

