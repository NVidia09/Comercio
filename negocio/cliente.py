from logger_base import log

class Cliente:

    def __init__(self, codigo=None, nombre=None, apellido=None, dni=None, empresa=None, cuit=None, telefono=None, email=None, direccion=None, numero=None, localidad=None, provincia=None, pais=None, observaciones=None, condiva=None):
        self._codigo = codigo
        self._nombre = nombre
        self._apellido = apellido
        self._dni = dni
        self._empresa = empresa
        self._cuit = cuit
        self._telefono = telefono
        self._email = email
        self._direccion = direccion
        self._numero = numero
        self._localidad = localidad
        self._provincia = provincia
        self._pais = pais
        self._observaciones = observaciones
        self._condiva = condiva

    def __str__(self):
        return f'''
            Código: {self._codigo}
            Nombre: {self._nombre}
            Apellido: {self._apellido}
            DNI: {self._dni}
            Empresa: {self._empresa}
            CUIT: {self._cuit}
            Teléfono: {self._telefono}
            Email: {self._email}
            Dirección: {self._direccion}
            Número: {self._numero}
            Localidad: {self._localidad}
            Provincia: {self._provincia}
            País: {self._pais}
            Observaciones: {self._observaciones}
            Condición IVA: {self._condiva}
        '''

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, codigo):
        self._codigo = codigo

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, nombre):
        self._nombre = nombre

    @property
    def apellido(self):
        return self._apellido

    @apellido.setter
    def apellido(self, apellido):
        self._apellido = apellido

    @property
    def dni(self):
        return self._dni

    @dni.setter
    def dni(self, dni):
        self._dni = dni

    @property
    def empresa(self):
        return self._empresa

    @empresa.setter
    def empresa(self, empresa):
        self._empresa = empresa

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = cuit

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, telefono):
        self._telefono = telefono

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, direccion):
        self._direccion = direccion

    @property
    def numero(self):
        return self._numero

    @numero.setter
    def numero(self, numero):
        self._numero = numero

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
    def observaciones(self):
        return self._observaciones

    @observaciones.setter
    def observaciones(self, observaciones):
        self._observaciones = observaciones

    @property
    def condiva(self):
        return self._condiva

    @condiva.setter
    def cond_iva(self, condiva):
        self._condiva = condiva


