from cgi import log

import pandas as pd

from Conexion import caja
from Conexion.caja import Caja
from Conexion.cursor_del_pool import CursorDelPool


class CajaDAO:

    _SELECCIONAR = "SELECT * FROM caja ORDER BY id ASC"
    _SELECCIONAR_COBRO = "SELECT * FROM caja WHERE tipo LIKE 'COBRO' ORDER BY id ASC"
    _SELECCIONAR_PAGO = "SELECT * FROM caja WHERE tipo LIKE 'PAGO' ORDER BY id ASC"
    _INSERTAR = "INSERT INTO caja(id, fecha, tipo, concepto, formapago, tarjeta, banco, total) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE caja SET id=%s, fecha=%s, tipo=%s, concepto=%s, formapago=%s, tarjeta=%s, banco=%s, total=%s WHERE id = %s'
    _ELIMINAR = "DELETE FROM caja WHERE id = %s"
    _BUSCA_REGISTRO = "SELECT * FROM caja WHERE id = %s"

    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            cajas = []
            for registro in registros:
                caja = Caja(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7])
                cajas.append(caja)
            return cajas

    @classmethod
    def seleccionar_cobro(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR_COBRO)
            registros = cursor.fetchall()
            cajas = []
            for registro in registros:
                caja = Caja(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6],
                            registro[7])
                cajas.append(caja)
            return cajas

    @classmethod
    def seleccionar_pago(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR_PAGO)
            registros = cursor.fetchall()
            cajas = []
            for registro in registros:
                caja = Caja(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7])
                cajas.append(caja)
            return cajas

    @classmethod
    def buscar_registro(cls, campo1, campo2, campo3, valor):
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM caja WHERE {campo1} ILIKE %s OR {campo2} ILIKE %s OR {campo3} ILIKE %s ORDER BY id ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            cajas = []
            for registro in registros:
                caja = Caja(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7])
                cajas.append(caja)
            return cajas

    @classmethod
    def insertar(cls, caja):
        with CursorDelPool() as cursor:
            valores = (
            caja.fecha, caja.tipo, caja.concepto, caja.formapago, caja.tarjeta, caja.banco, caja.total)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Cobro ingresado: {caja}')
            return cursor.rowcount

    @classmethod
    def eliminar(cls, registro):
        with CursorDelPool() as cursor:
            valores = (caja.id,)
            cursor.execute(cls._ELIMINAR, valores)
            log.debug(f'Registro eliminado: {registro}')
            return cursor.rowcount

    @classmethod
    def exportar_cobros(cls, ruta_archivo):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR_COBRO)
            registros = cursor.fetchall()
            cajas = []
            for registro in registros:
                caja = Caja(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6],
                            registro[7])
                cajas.append(caja)
        data = {
            'id': [caja.id for caja in cajas],
            'fecha': [caja.fecha for caja in cajas],
            'tipo': [caja.tipo for caja in cajas],
            'concepto': [caja.concepto for caja in cajas],
            'formapago': [caja.formapago for caja in cajas],
            'tarjeta': [caja.tarjeta for caja in cajas],
            'banco': [caja.banco for caja in cajas],
            'total': [caja.total for caja in cajas]
        }
        df = pd.DataFrame(data)

        # Guardar el DataFrame en un archivo Excel
        df.to_excel(ruta_archivo, sheet_name="Cobros", merge_cells=True, index=False)

    @classmethod
    def exportar_pagos(cls, ruta_archivo):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR_PAGO)
            registros = cursor.fetchall()
            cajas = []
            for registro in registros:
                caja = Caja(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6],
                            registro[7])
                cajas.append(caja)
        data = {
            'id': [caja.id for caja in cajas],
            'fecha': [caja.fecha for caja in cajas],
            'tipo': [caja.tipo for caja in cajas],
            'concepto': [caja.concepto for caja in cajas],
            'formapago': [caja.formapago for caja in cajas],
            'tarjeta': [caja.tarjeta for caja in cajas],
            'banco': [caja.banco for caja in cajas],
            'total': [caja.total for caja in cajas]
        }
        df = pd.DataFrame(data)

        # Guardar el DataFrame en un archivo Excel
        df.to_excel(ruta_archivo, sheet_name="Pagos", merge_cells=True, index=False)