from conexion_db import Conexion
from cursor_del_pool import CursorDelPool
from logger_base import log
import sys

from negocio.factura import Factura

class FacturaDAO:

    _SELECCIONAR = "SELECT * FROM facturas ORDER BY codfactura DESC"
    _INSERTAR = "INSERT INTO facturas(serie, codfactura, fecha, codcliente, cliente, estado, subtotal, iva, total, formapago, tipo, entrega) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE facturas SET serie=%s, codfactura=%s, fecha=%s, codcliente=%s, cliente=%s, estado=%s, subtotal=%s, iva=%s, total=%s, formapago=%s, tipo=%s, entrega=%s WHERE codfactura = %s'
    _ELIMINAR = "DELETE FROM facturas WHERE codfactura = %s"
    _BUSCA_FACTURA = "SELECT * FROM facturas WHERE codfactura = %s"
    _BUSCA_FACT_PENDIENTE = "SELECT * FROM facturas WHERE entrega = 'ENVIO' ORDER BY codfactura DESC"
    _BUSCA_FACT_COBRAR = "SELECT * FROM facturas WHERE formapago = %s AND formapago = %s ORDER BY codfactura DESC"
    _COBRAR_FACT_CLIENTE = "SELECT * FROM facturas WHERE estado = 'PENDIENTE' AND serie = %s AND codfactura = %s AND codcliente = %s ORDER BY codfactura DESC"

    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                factura = Factura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10], registro[11])
                facturas.append(factura)
            return facturas

    @classmethod
    def buscar_factura(cls, campo1, campo2, campo3, valor):
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM facturas WHERE {campo1} ILIKE %s OR {campo2} ILIKE %s OR {campo3} ILIKE %s ORDER BY codfactura ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                factura = Factura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10], registro[11])
                facturas.append(factura)
            return facturas

    @classmethod
    def insertar(cls, factura):
        with CursorDelPool() as cursor:
            valores = (factura.serie, factura.codfactura, factura.fecha, factura.codcliente, factura.cliente, factura.estado, factura.subtotal, factura.iva, factura.total, factura.formapago, factura.tipo, factura.entrega)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Factura ingresada: {factura}')
            return cursor.rowcount

    @classmethod
    def buscar_factura_pendiente(cls, campo1):
        with CursorDelPool() as cursor:
            #cursor.execute(cls._BUSCA_FACT_PENDIENTE, pendiente)
            query = f"SELECT * FROM facturas WHERE entrega LIKE %s  ORDER BY codfactura DESC"
            cursor.execute(query, (f'%{campo1}%',))
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                factura = Factura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11])
                facturas.append(factura)
            return facturas

    @classmethod
    def buscar_factura_cobrar(cls, campo1):
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM facturas WHERE estado LIKE %s ORDER BY codfactura ASC"
            cursor.execute(query, (f'%{campo1}%', ))
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                factura = Factura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11])
                facturas.append(factura)
            return facturas

    @classmethod
    def seleccionar_factura_cliente(cls, campo1, campo2):
        with CursorDelPool() as cursor:
            query = "SELECT * FROM facturas WHERE CAST(codcliente AS TEXT) LIKE %s OR cliente LIKE %s ORDER BY codfactura DESC"
            cursor.execute(query, (f'%{campo1}%', f'%{campo2}%'))
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                factura = Factura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11])
                facturas.append(factura)
            return facturas

    @classmethod
    def cobrar_factura_cliente(cls, serie, codfactura, codcliente):
        with CursorDelPool() as cursor:
            query = "SELECT * FROM facturas WHERE estado = 'PENDIENTE' AND serie = %s AND codfactura = %s AND codcliente = %s ORDER BY codfactura DESC"
            cursor.execute(query, (serie, codfactura, codcliente))
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                factura = Factura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11])
                facturas.append(factura)
            return facturas

    @classmethod
    def cobrar_factura_cliente1(cls, serie, codfactura):
        with CursorDelPool() as cursor:
            query = "SELECT * FROM facturas WHERE estado = 'PENDIENTE' AND serie = %s AND codfactura = %s ORDER BY codfactura DESC"
            cursor.execute(query, (serie, codfactura))
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                factura = Factura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11])
                facturas.append(factura)
            return facturas



