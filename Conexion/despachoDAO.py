import pandas as pd

from Conexion.cursor_del_pool import CursorDelPool
from Conexion.logger_base import log

from Conexion.despacho import Despacho

class DespachoDAO:

    _SELECCIONAR = "SELECT * FROM despacho ORDER BY coddespacho DESC"
    _INSERTAR = "INSERT INTO despacho(coddespacho, fecha, serie, codfactura, codcliente, cliente, estado, tipo, transporte, guia, observaciones) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE despacho SET fecha=%s, serie=%s, codfactura=%s, codcliente=%s, cliente=%s, estado=%s, tipo=%s, transporte=%s, guia=%s, observaciones=%s WHERE coddespacho = %s'
    _ELIMINAR = "DELETE FROM despacho WHERE coddespacho = %s"
    _BUSCA_DESPACHO = "SELECT * FROM despacho WHERE coddespacho = %s"
    _BUSCA_DESPACHO_PENDIENTE = "SELECT * FROM despacho WHERE estado = 'PENDIENTE' ORDER BY coddespacho DESC"


    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            despachos = []
            for registro in registros:
                despacho = Despacho(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                despachos.append(despacho)
            return despachos

    @classmethod
    def buscar_despacho(cls, campo1, campo2, campo3, valor):
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM despacho WHERE {campo1} ILIKE %s OR {campo2} ILIKE %s OR {campo3} ILIKE %s ORDER BY coddespacho ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            despachos = []
            for registro in registros:
                despacho = Despacho(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                despachos.append(despacho)
            return despachos

    @classmethod
    def insertar(cls, despacho):
        with CursorDelPool() as cursor:
            valores = (despacho.coddespacho, despacho.fecha, despacho.serie, despacho.codfactura, despacho.codcliente, despacho.cliente, despacho.estado, despacho.tipo, despacho.transporte, despacho.guia, despacho.observaciones)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Factura ingresada: {despacho}')
            return cursor.rowcount

    @classmethod
    def buscar_despacho_pendiente(cls, campo1):
        with CursorDelPool() as cursor:
            #cursor.execute(cls._BUSCA_FACT_PENDIENTE, pendiente)
            query = f"SELECT * FROM despacho WHERE estado LIKE %s  ORDER BY coddespacho DESC"
            cursor.execute(query, (f'%{campo1}%',))
            registros = cursor.fetchall()
            despachos = []
            for registro in registros:
                despacho = Despacho(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                despachos.append(despacho)
            return despachos



    @classmethod
    def seleccionar_despacho_cliente(cls, campo1, campo2):
        with CursorDelPool() as cursor:
            query = "SELECT * FROM despacho WHERE CAST(codcliente AS TEXT) LIKE %s OR cliente LIKE %s ORDER BY coddespacho DESC"
            cursor.execute(query, (f'%{campo1}%', f'%{campo2}%'))
            registros = cursor.fetchall()
            despachos = []
            for registro in registros:
                despacho = Despacho(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                despachos.append(despacho)
            return despachos


    @classmethod
    def exportar_despachos(cls, ruta_archivo):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            despachos = []
            for registro in registros:
                despacho = Despacho(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                despachos.append(despacho)

        data = {
            'coddespacho': [despacho.coddespacho for despacho in despachos],
            'fecha': [despacho.fecha for despacho in despachos],
            'serie': [despacho.serie for despacho in despachos],
            'codfactura': [despacho.codfactura for despacho in despachos],
            'codcliente': [despacho.codcliente for despacho in despachos],
            'cliente': [despacho.cliente for despacho in despachos],
            'estado': [despacho.estado for despacho in despachos],
            'tipo': [despacho.tipo for despacho in despachos],
            'transporte': [despacho.transporte for despacho in despachos],
            'guia': [despacho.guia for despacho in despachos],
            'observaciones': [despacho.observaciones for despacho in despachos]
        }
        df = pd.DataFrame(data)

        # Guardar el DataFrame en un archivo Excel
        df.to_excel(ruta_archivo, sheet_name="Despachos_Pendientes", merge_cells=True, index=False)


