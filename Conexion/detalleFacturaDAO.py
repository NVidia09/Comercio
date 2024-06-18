from Conexion.cursor_del_pool import CursorDelPool
from Conexion.logger_base import log

from Conexion.detalleFactura import detalleFactura


class detalleFacturaDAO:

    _SELECCIONAR = "SELECT * FROM detallefactura ORDER BY codfactura ASC"
    _INSERTAR = "INSERT INTO detallefactura(serie, codfactura, codarticulo, descripcion, cantidad, precioventa, importe, iva, tipo) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE detallefactura SET serie=%s, codfactura=%s, codarticulo=%s, descripcion=%s, cantidad=%s, precioventa=%s, importe=%s, iva=%s, total=%s, tipo=%s, WHERE codfactura = %s'
    _ELIMINAR = "DELETE FROM detallefactura WHERE codfactura = %s"
    _BUSCA_FACTURA = "SELECT * FROM detallefactura WHERE codfactura = %s"
    _BUSCA_DETALLE = "SELECT * FROM detallefactura WHERE codfactura = %s"

    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            detallefacturas = []
            for registro in registros:
                detallefactura = detalleFactura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8])
                detallefacturas.append(detallefactura)
            return detallefacturas

    @classmethod
    def buscar_factura(cls, campo1, campo2, campo3, valor):
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM facturas WHERE {campo1} ILIKE %s OR {campo2} ILIKE %s OR {campo3} ILIKE %s ORDER BY nrofactura ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            detallefacturas = []
            for registro in registros:
                detallefactura = detalleFactura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8])
                detallefacturas.append(detallefactura)
            return detallefacturas

    @classmethod
    def busca_detalle(cls, detalle_buscar):
        with CursorDelPool() as cursor:
            cursor.execute(cls._BUSCA_DETALLE, (detalle_buscar,))
            registros = cursor.fetchall()
            detallefacturas = []
            for registro in registros:
                detallefactura = detalleFactura(registro[0], registro[1], registro[2], registro[3], registro[4],
                                                registro[5], registro[6], registro[7], registro[8])
                detallefacturas.append(detallefactura)
            return detallefacturas

    @classmethod
    def insertar(cls, detallefactura):
        with CursorDelPool() as cursor:
            valores = (detallefactura.serie, detallefactura.codfactura, detallefactura.codarticulo, detallefactura.descripcion, detallefactura.cantidad, float(detallefactura.precioventa), detallefactura.importe, detallefactura.iva, detallefactura.tipo)
            # for df in detallefactura:
            #     valores = (
            #     df.serie, df.codfactura, df.codarticulo, df.descripcion, df.cantidad, df.precioventa, df.importe,
            #     df.iva)
            #     # rest of your code
            print(valores)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Factura ingresada: {detallefactura}')
            return cursor.rowcount

    @classmethod
    def seleccionar_detalle_factura_cliente(cls, campo1, campo2):
        with CursorDelPool() as cursor:
            query = "SELECT * FROM detallefactura WHERE CAST(serie AS TEXT) LIKE %s AND CAST(codfactura AS TEXT) LIKE %s ORDER BY codfactura ASC"
            cursor.execute(query, (f'%{campo1}%', f'%{campo2}%'))
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                detallefactura = detalleFactura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8])
                facturas.append(detallefactura)
            return facturas

