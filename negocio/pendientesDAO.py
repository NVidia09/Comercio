from conexion_db import Conexion
from cursor_del_pool import CursorDelPool
from logger_base import log
import sys

from negocio.factura import Factura
from negocio.pendientes import Pendiente


class PendientesDAO:

    _SELECCIONAR = "SELECT * FROM pendientes ORDER BY codpendiente ASC"
    _INSERTAR = "INSERT INTO pendientes(serie, codfactura, estado, fecha, codcliente, nombre, importe, pagos, saldo, fechacancelada) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE pendientes SET serie=%s, codfactura=%s, estado=%s, fecha=%s, codcliente=%s, nombre=%s, importe=%s, pagos=%s, saldo=%s, fechacancelada=%s WHERE codpendiente = %s'
    _ELIMINAR = "DELETE FROM pendientes WHERE codpendiente = %s"
    _BUSCA_PENDIENTE = "SELECT * FROM pendientes WHERE codpendiente = %s"
    _BUSCA_PENDIENTE_CLIENTE = "SELECT * FROM pendientes WHERE codcliente = %s ORDER BY codpendiente ASC"
    _BUSCA_PENDIENTE_SALDO = "SELECT * FROM pendientes WHERE saldo > 0 ORDER BY codpendiente ASC"

    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            pendientes = []
            for registro in registros:
                pendiente = Pendiente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                pendientes.append(pendiente)
            return pendientes

    @classmethod
    def buscar_pendiente(cls, campo1, campo2, campo3, valor):
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM pendientes WHERE {campo1} ILIKE %s OR {campo2} ILIKE %s OR {campo3} ILIKE %s ORDER BY codpendiente ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            pendientes = []
            for registro in registros:
                pendiente = Pendiente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                pendientes.append(pendiente)
            return pendientes

    @classmethod
    def buscar_pendiente_cliente(cls, cliente):
        with CursorDelPool() as cursor:
            cursor.execute(cls._BUSCA_PENDIENTE_CLIENTE, cliente)
            registros = cursor.fetchall()
            pendientes = []
            for registro in registros:
                pendiente = Pendiente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                pendientes.append(pendiente)
            return pendientes

    @classmethod
    def buscar_pendiente_saldo(cls, saldo):
        with CursorDelPool() as cursor:
            cursor.execute(cls._BUSCA_PENDIENTE_SALDO, saldo)
            registros = cursor.fetchall()
            pendientes = []
            for registro in registros:
                pendiente = Pendiente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                pendientes.append(pendiente)
            return pendientes

    @classmethod
    def insertar(cls, pendiente):
        with CursorDelPool() as cursor:
            # Ensure that the `valores` tuple has the same number of elements as the placeholders in your `cls._INSERTAR` SQL query
            valores = (pendiente.serie, pendiente.codfactura, pendiente.estado, pendiente.fecha, pendiente.codcliente,
                       pendiente.nombre, pendiente.importe, pendiente.pagos, pendiente.saldo, pendiente.fechacancelada)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Pendiente ingresado: {pendiente}')
            return cursor.rowcount

    @classmethod
    def actualizar(cls, pendiente):
        with CursorDelPool() as cursor:
            valores = (pendiente.serie, pendiente.codfactura, pendiente.estado, pendiente.fecha, pendiente.codcliente, pendiente.nombre, pendiente.importe, pendiente.pagos, pendiente.saldo, pendiente.fechacancelada, pendiente.codpendiente)
            cursor.execute(cls._ACTUALIZAR, valores)
            log.debug(f'Pendiente actualizado: {pendiente}')
            return cursor.rowcount

    @classmethod
    def eliminar(cls, pendiente):
        with CursorDelPool() as cursor:
            valores = (pendiente.codpendiente,)
            cursor.execute(cls._ELIMINAR, valores)
            log.debug(f'Datos de Pendiente eliminados: {pendiente}')
            return cursor.rowcount


