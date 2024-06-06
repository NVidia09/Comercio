
class Pendiente:

    def __init__(self, codpendiente=None, serie=None, codfactura=None, estado=None, fecha=None, codcliente=None, nombre=None,
                     importe=None, pagos=None, saldo=None, fechacancelada=None):
        self._codpendiente = codpendiente
        self._serie = serie
        self._codfactura = codfactura
        self._estado = estado
        self._fecha = fecha
        self._codcliente = codcliente
        self._nombre = nombre
        self._importe = importe
        self._pagos = pagos
        self._saldo = saldo
        self._fechacancelada = fechacancelada

    def __str__(self):
        return f'''
        Codigo Pendiente: {self._codpendiente}
        Serie: {self._serie}
        Cod Factura: {self._codfactura}
        Estado: {self._estado}
        Fecha: {self._fecha}
        Cod Cliente: {self._codcliente}
        Nombre: {self._nombre}
        Importe: {self._importe}
        Pagos: {self._pagos}
        Saldo: {self._saldo}
        Fecha Cancelada: {self._fechacancelada}
        '''

    @property
    def codpendiente(self):
        return self._codpendiente

    @codpendiente.setter
    def codpendiente(self, codpendiente):
        self._codpendiente = codpendiente

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
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, estado):
        self._estado = estado

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
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, nombre):
        self._nombre = nombre

    @property
    def importe(self):
        return self._importe

    @importe.setter
    def importe(self, importe):
        self._importe = importe

    @property
    def pagos(self):
        return self._pagos

    @pagos.setter
    def pagos(self, pagos):
        self._pagos = pagos

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, saldo):
        self._saldo = saldo

    @property
    def fechacancelada(self):
        return self._fechacancelada

    @fechacancelada.setter
    def fechacancelada(self, fechacancelada):
        self._fechacancelada = fechacancelada

