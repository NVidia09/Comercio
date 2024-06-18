
class Caja:
    def __init__(self, id=None, fecha=None, tipo=None, concepto=None, formapago=None, tarjeta=None, banco=None, total=None):
        self._id = id
        self._fecha = fecha
        self._tipo = tipo
        self._concepto = concepto
        self._formapago = formapago
        self._tarjeta = tarjeta
        self._banco = banco
        self._total = total

    def __str__(self):
        return f'''
            ID: {self._id}
            Fecha: {self._fecha}
            Tipo: {self._tipo}
            Concepto: {self._concepto}
            Forma de Pago: {self._formapago}
            Tarjeta: {self._tarjeta}
            Banco: {self._banco}
            Total: {self._total}
        '''

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = fecha

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = tipo

    @property
    def concepto(self):
        return self._concepto

    @concepto.setter
    def concepto(self, concepto):
        self._concepto = concepto

    @property
    def formapago(self):
        return self._formapago

    @formapago.setter
    def formapago(self, formapago):
        self._formapago = formapago

    @property
    def tarjeta(self):
        return self._tarjeta

    @tarjeta.setter
    def tarjeta(self, tarjeta):
        self._tarjeta = tarjeta

    @property
    def banco(self):
        return self._banco

    @banco.setter
    def banco(self, banco):
        self._banco = banco

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, total):
        self._total = total


