
class Proveedor:
    def __init__(self, codproveedor, razonsocial, cuit, domicilio, ciudad, provincia, pais, telefono, email, web, cuenta, password, observaciones):
        self._codproveedor = codproveedor
        self._razonsocial = razonsocial
        self._cuit = cuit
        self._domicilio = domicilio
        self._ciudad = ciudad
        self._provincia = provincia
        self._pais = pais
        self._telefono = telefono
        self._email = email
        self._web = web
        self._cuenta = cuenta
        self._password = password
        self._observaciones = observaciones

    def __str__(self):
        return f'''
            Código: {self._codproveedor}
            Razón Social: {self._razonsocial}
            CUIT: {self._cuit}
            Domicilio: {self._domicilio}
            Ciudad: {self._ciudad}
            Provincia: {self._provincia}
            País: {self._pais}
            Teléfono: {self._telefono}
            Email: {self._email}
            Web: {self._web}
            Cuenta: {self._cuenta}
            Password: {self._password}
            Observaciones: {self._observaciones}
        '''

    @property
    def codproveedor(self):
        return self._codproveedor

    @codproveedor.setter
    def codproveedor(self, codproveedor):
        self._codproveedor = codproveedor

    @property
    def razonsocial(self):
        return self._razonsocial

    @razonsocial.setter
    def razonsocial(self, razonsocial):
        self._razonsocial = razonsocial

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = cuit

    @property
    def domicilio(self):
        return self._domicilio

    @domicilio.setter
    def domicilio(self, domicilio):
        self._domicilio = domicilio

    @property
    def ciudad(self):
        return self._ciudad

    @ciudad.setter
    def ciudad(self, ciudad):
        self._ciudad = ciudad

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
    def web(self):
        return self._web

    @web.setter
    def web(self, web):
        self._web = web

    @property
    def cuenta(self):
        return self._cuenta

    @cuenta.setter
    def cuenta(self, cuenta):
        self._cuenta = cuenta

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def observaciones(self):
        return self._observaciones

    @observaciones.setter
    def observaciones(self, observaciones):
        self._observaciones = observaciones







