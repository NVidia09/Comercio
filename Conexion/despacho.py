
class Despacho:
    def __init__(self, coddespacho, fecha, serie, codfactura, codcliente, cliente, estado, tipo, transporte, guia):
        self._coddespacho = coddespacho
        self._fecha = fecha
        self._serie = serie
        self._codfactura = codfactura
        self._codcliente = codcliente
        self._cliente = cliente
        self._estado = estado
        self._tipo = tipo
        self._transporte = transporte
        self._guia = guia

    def __str__(self):
        return f'''
        CODIGO DESPACHO: {self.coddespacho}
        FECHA: {self.fecha}
        SERIE: {self.serie}
        CODIGO FACTURA: {self.codfactura}
        CODIGO CLIENTE: {self.codcliente}
        CLIENTE: {self.cliente}
        ESTADO: {self.estado}
        TIPO: {self.tipo}
        TRANSPORTE: {self.transporte}
        GUIA: {self.guia}
        '''

    @property
    def coddespacho(self):
        return self._coddespacho

    @coddespacho.setter
    def coddespacho(self, coddespacho):
        self._coddespacho = coddespacho

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = fecha

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
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = tipo

    @property
    def transporte(self):
        return self._transporte

    @transporte.setter
    def transporte(self, transporte):
        self._transporte = transporte

    @property
    def guia(self):
        return self._guia

    @guia.setter
    def guia(self, guia):
        self

    @guia.setter
    def guia(self, guia):
        self._guia = guia

