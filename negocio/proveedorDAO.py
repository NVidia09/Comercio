from cursor_del_pool import CursorDelPool
from logger_base import log
import sys

from negocio.cliente import Cliente
from negocio.proveedor import Proveedor


class ProveedorDAO:

    _SELECCIONAR = "SELECT * FROM proveedores ORDER BY razonSocial ASC"
    _ULTIMO_CODIGO_USADO = "SELECT * FROM proveedores ORDER BY codproveedor DESC FETCH FIRST 1 ROWS ONLY"
    _INSERTAR = "INSERT INTO proveedores(codproveedor, razonsocial, cuit, domicilio, ciudad, provincia, pais, telefono, web, email, cuenta, password, observaciones) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE proveedores SET razonsocial=%s, cuit=%s, domicilio=%s, ciudad=%s, provincia=%s, pais=%s, telefono=%s, web=%s, email=%s, cuenta=%s, password=%s, observaciones=%s WHERE codproveedor = %s'
    _ELIMINAR = "DELETE FROM proveedores WHERE codproveedor = %s"
    _BUSCA_CLIENTE = "SELECT * FROM proveedores WHERE codproveedor = %s"
    _SELECCIONAR_PROVEEDOR = "SELECT DISTINCT razonsocial FROM proveedores ORDER BY razonsocial ASC"



    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            proveedores = []
            for registro in registros:
                proveedor = Proveedor(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10], registro[11], registro[12])
                proveedores.append(proveedor)
            return proveedores

    @classmethod
    def ultimo_codigo_usado(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._ULTIMO_CODIGO_USADO)
            registros = cursor.fetchall()
            proveedores = []
            for registro in registros:
                proveedor = Proveedor(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                      registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                      registro[12])
                proveedores.append(proveedor)
            return proveedores

    @classmethod
    def buscar_proveedor(cls, campo1, campo2, campo3, valor):

        with CursorDelPool() as cursor:
            query = f"SELECT * FROM proveedores WHERE {campo1} ILIKE %s OR {campo2} ILIKE %s OR {campo3} ILIKE %s ORDER BY codproveedor ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            proveedores = []
            for registro in registros:
                proveedor = Proveedor(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                            registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                            registro[12])
                proveedores.append(proveedor)
            return proveedores

    @classmethod
    def insertar(cls, proveedor):
        with CursorDelPool() as cursor:
            valores = (proveedor.codproveedor, proveedor.razonsocial, proveedor.cuit, proveedor.domicilio, proveedor.ciudad, proveedor.provincia, proveedor.pais, proveedor.telefono, proveedor.web, proveedor.email, proveedor.cuenta, proveedor.password, proveedor.observaciones)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Proveedor ingresado: {proveedor}')
            return cursor.rowcount

            try:
                archivo_proveedores = open('proveedor.txt', 'a', encoding='utf8')
                archivo_proveedores.write(f'Proveedor: {proveedor}\n')
            except Exception as e:
                log.error(f'Error al abrir el archivo de proveedor: {e}')
            finally:
                archivo.close()

    @classmethod
    def actualizar(cls, proveedor):
        with CursorDelPool() as cursor:
            valores = (proveedor.razonsocial, proveedor.cuit, proveedor.domicilio, proveedor.ciudad, proveedor.provincia, proveedor.pais, proveedor.telefono, proveedor.web, proveedor.email, proveedor.cuenta, proveedor.password, proveedor.observaciones, proveedor.codproveedor)
            cursor.execute(cls._ACTUALIZAR, valores)
            log.debug(f'Proveedor actualizado: {proveedor}')
            return cursor.rowcount

    @classmethod
    def eliminar(cls, proveedor):
        with CursorDelPool() as cursor:
            valores = (proveedor.codproveedor,)
            cursor.execute(cls._ELIMINAR, valores)
            log.debug(f'Proveedor eliminado: {proveedor}')
            return cursor.rowcount

    @classmethod
    def seleccionar_proveedores(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR_PROVEEDOR)
            registros = cursor.fetchall()
            proveedores = [registro[0] for registro in registros]
            return proveedores

    @classmethod
    def importar_desde_excel(cls, ruta_archivo):
        try:
            import pandas as pd
            #df = pd.read_excel('proveedores.xlsx')
            df = pd.read_excel(ruta_archivo)
            proveedores = []
            for index, row in df.iterrows():
                proveedor = Proveedor(row['codproveedor'], row['razonsocial'], row['cuit'], row['domicilio'], row['ciudad'], row['provincia'], row['pais'], row['telefono'], row['web'], row['email'], row['cuenta'], row['password'], row['observaciones'])
                proveedores.append(proveedor)

            # Insertar cada proveedor en la base de datos
            for proveedor in proveedores:
                cls.insertar(proveedor)

            return proveedores

        except Exception as e:
            log.error(f'Error al importar proveedores desde Excel: {e}')
            sys.exit(1)

    @classmethod
    def actualizar_desde_excel(cls, ruta_archivo):
        try:
            import pandas as pd
            # df = pd.read_excel('proveedores.xlsx')
            df = pd.read_excel(ruta_archivo)
            proveedores = []
            for index, row in df.iterrows():
                proveedor = Proveedor(row['codproveedor'], row['razonsocial'], row['cuit'], row['domicilio'],
                                      row['ciudad'], row['provincia'], row['pais'], row['telefono'], row['web'],
                                      row['email'], row['cuenta'], row['password'], row['observaciones'])
                proveedores.append(proveedor)

            # Insertar cada proveedor en la base de datos
            for proveedor in proveedores:
                cls.actualizar(proveedor)

            return proveedores

        except Exception as e:
            log.error(f'Error al importar proveedores desde Excel: {e}')
            sys.exit(1)



