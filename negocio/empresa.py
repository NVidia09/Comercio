from logger_base import log

class Empresa:

    def __init__(self, razonsocial=None, nombrefantasia=None, cuit=None, categoria=None, iibb=None, inicioactividades=None, domicilio=None, localidad=None, provincia=None, pais=None, sucursales=None):
        self._razonsocial = razonsocial
        self._nombrefantasia = nombrefantasia
        self._cuit = cuit
        self._categoria = categoria
        self._iibb = iibb
        self._inicioactividades = inicioactividades
        self._domicilio = domicilio
        self._localidad = localidad
        self._provincia = provincia
        self._pais = pais
        self._sucursales = sucursales


    def __str__(self):
        return f'''
            Razon Social: {self._razonsocial}
            Nombre Fantasía: {self._nombrefantasia}
            C.U.I.T. N°: {self._cuit}
            Categoría: {self._categoria}
            IIBB N°: {self._iibb}
            Inicio Actividades: {self._inicioactividades}
            Domicilio: {self._domicilio}
            Localidad: {self._localidad}
            Provincia: {self._provincia}
            País: {self._pais}
            Sucursales: {self._sucursales}
                        
        '''

    @property
    def razonsocial(self):
        return self._razonsocial

    @razonsocial.setter
    def razonsocial(self, razonsocial):
        self._razonsocial = razonsocial


    @property
    def nombrefantasia(self):
        return self._nombrefantasia

    @nombrefantasia.setter
    def nombrefantasia(self, nombrefantasia):
        self._nombrefantasia = nombrefantasia

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = cuit

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, categoria):
        self._categoria = categoria

    @property
    def iibb(self):
        return self._iibb

    @iibb.setter
    def iibb(self, iibb):
        self._iibb = iibb

    @property
    def inicioactividades(self):
        return self._inicioactividades

    @inicioactividades.setter
    def inicioactividades(self, inicioactividades):
        self._inicioactividades = inicioactividades

    @property
    def domicilio(self):
        return self._domicilio

    @domicilio.setter
    def domicilio(self, domicilio):
        self._domicilio = domicilio

    @property
    def localidad(self):
        return self._localidad

    @localidad.setter
    def localidad(self, localidad):
        self._localidad = localidad

    @property
    def provincia(self):
        return self._provincia

    @provincia.setter
    def provincia(self, provincia):
        self._provincia = provincia

    @property
    def pais(self):
        return self._pais

    @pais.setter
    def pais(self, pais):
        self._pais = pais

    @property
    def sucursales(self):
        return self._sucursales

    @sucursales.setter
    def sucursales(self, sucursales):
        self._sucursales = sucursales









