from Conexion.logger_base import log
class Articulo:

    def __init__(self, codigo=None, nombre=None, modelo=None, marca=None, categoria=None, sku=None, color=None,
                 caracteristica=None, precio_costo=None, precio_venta=None, iva=None, proveedor=None, tamaño=None,
                 ancho=None, largo=None, profundidad=None, peso=None, peso_envalado=None, stock=None, margen_ganancia=None, stock_minimo=None, cod_barras=None):
        self._codigo = codigo
        self._nombre = nombre
        self._modelo = modelo
        self._marca = marca
        self._categoria = categoria
        self._sku = sku
        self._color = color
        self._caracteristica = caracteristica
        self._precio_costo = precio_costo
        self._precio_venta = precio_venta
        self._iva = iva
        self._proveedor = proveedor
        self._tamaño = tamaño
        self._ancho = ancho
        self._largo = largo
        self._profundidad = profundidad
        self._peso = peso
        self._peso_envalado = peso_envalado
        self._stock = stock
        self._margen_ganancia = margen_ganancia
        self._stock_minimo = stock_minimo
        self._cod_barras = cod_barras

    def __str__(self):
        return f'''
            Código: {self._codigo}
            Nombre: {self._nombre}
            Modelo: {self._modelo}
            Marca: {self._marca}
            Categoría: {self._categoria}
            SKU: {self._sku}
            Color: {self._color}
            Característica: {self._caracteristica}
            Precio de costo: {self._precio_costo}
            Precio de venta: {self._precio_venta}
            IVA: {self._iva}
            Proveedor: {self._proveedor}
            Tamaño: {self._tamaño}
            Ancho: {self._ancho}
            Largo: {self._largo}
            Profundidad: {self._profundidad}
            Peso: {self._peso}
            Peso envalado: {self._peso_envalado}
            Stock: {self._stock}
            Margen de ganancia: {self._margen_ganancia}
            Stock mínimo: {self._stock_minimo}
            Código de barras: {self._cod_barras}
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
    def modelo(self):
        return self._modelo

    @modelo.setter
    def modelo(self, modelo):
        self._modelo = modelo

    @property
    def marca(self):
        return self._marca

    @marca.setter
    def marca(self, marca):
        self._marca = marca

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, categoria):
        self._categoria = categoria

    @property
    def sku(self):
        return self._sku

    @sku.setter
    def sku(self, sku):
        self._sku = sku

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @property
    def caracteristica(self):
        return self._caracteristica

    @caracteristica.setter
    def caracteristica(self, caracteristica):
        self._caracteristica = caracteristica

    @property
    def precio_costo(self):
        return self._precio_costo

    @precio_costo.setter
    def precio_costo(self, precio_costo):
        self._precio_costo = precio_costo

    @property
    def precio_venta(self):
        return self._precio_venta

    @precio_venta.setter
    def precio_venta(self, precio_venta):
        self._precio_venta = precio_venta

    @property
    def iva(self):
        return self._iva

    @iva.setter
    def iva(self, iva):
        self._iva = iva

    @property
    def proveedor(self):
        return self._proveedor

    @proveedor.setter
    def proveedor(self, proveedor):
        self._proveedor = proveedor

    @property
    def tamaño(self):
        return self._tamaño

    @tamaño.setter
    def tamaño(self, tamaño):
        self._tamaño = tamaño

    @property
    def ancho(self):
        return self._ancho

    @ancho.setter
    def ancho(self, ancho):
        self._ancho = ancho

    @property
    def largo(self):
        return self._largo

    @largo.setter
    def largo(self, largo):
        self._largo = largo

    @property
    def profundidad(self):
        return self._profundidad

    @profundidad.setter
    def profundidad(self, profundidad):
        self._profundidad = profundidad

    @property
    def peso(self):
        return self._peso

    @peso.setter
    def peso(self, peso):
        self._peso = peso

    @property
    def peso_envalado(self):
        return self._peso_envalado

    @peso_envalado.setter
    def peso_envalado(self, peso_envalado):
        self._peso_envalado = peso_envalado

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, stock):
        self._stock = stock

    @property
    def margen_ganancia(self):
        return self._margen_ganancia

    @margen_ganancia.setter
    def margen_ganancia(self, margen_ganancia):
        self._margen_ganancia = margen_ganancia

    @property
    def stock_minimo(self):
        return self._stock_minimo

    @stock_minimo.setter
    def stock_minimo(self, stock_minimo):
        self._stock_minimo = stock_minimo

    @property
    def cod_barras(self):
        return self._cod_barras

    @cod_barras.setter
    def cod_barras(self, cod_barras):
        self._cod_barras = cod_barras







