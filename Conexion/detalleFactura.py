

class detalleFactura:
    def __init__(self, serie=None, codfactura=None, codarticulo=None, descripcion=None, cantidad=None, precioventa=None, importe=None, iva=None, tipo=None):
        self._serie = serie
        self._codfactura = codfactura
        self._codarticulo = codarticulo
        self._descripcion = descripcion
        self._cantidad = cantidad
        self._precioventa = precioventa
        self._importe = importe
        self._iva = iva
        self._tipo = tipo

    def __str__(self):
        return f'''
            Serie: {self._serie}
            N° Factura: {self._codfactura}
            Código Artículo: {self._codarticulo}
            Descripción: {self._descripcion}
            Cantidad: {self._cantidad}
            Precio Venta: {self._precioventa}
            Importe: {self._importe}
            IVA: {self._iva}
            Tipo: {self._tipo}
        '''

    def __iter__(self):
        yield self.serie
        yield self.codfactura
        yield self.codarticulo
        yield self.descripcion
        yield self.cantidad
        yield self.precioventa
        yield self.importe
        yield self.iva
        yield self.tipo

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
    def precioventa(self):
        return self._precioventa

    @precioventa.setter
    def precioventa(self, precioventa):
        self._precioventa = precioventa

    @property
    def importe(self):
        return self._importe

    @importe.setter
    def importe(self, importe):
        self._importe = importe

    @property
    def iva(self):
        return self._iva

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = tipo
