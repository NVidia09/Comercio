from PyQt5.uic.properties import QtWidgets

from conexion_db import Conexion
from cursor_del_pool import CursorDelPool
from logger_base import log
import sys

from negocio.cliente import Cliente


class ClienteDAO:

    _SELECCIONAR = "SELECT * FROM clientes ORDER BY nombre, apellido ASC"
    _ULTIMO_CODIGO_USADO = "SELECT * FROM clientes ORDER BY codigo DESC FETCH FIRST 1 ROWS ONLY"
    _INSERTAR = "INSERT INTO clientes(codigo, nombre, apellido, dni, empresa, cuit, telefono, email, direccion, numero, localidad, provincia, pais, observaciones, condiva) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE clientes SET nombre=%s, apellido=%s, dni=%s, empresa=%s, cuit=%s, telefono=%s, email=%s, direccion=%s, numero=%s, localidad=%s, provincia=%s, pais=%s, observaciones=%s, condiva=%s WHERE codigo = %s'
    _ELIMINAR = "DELETE FROM clientes WHERE codigo = %s"
    _BUSCA_CLIENTE = "SELECT * FROM clientes WHERE codigo = %s"



    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            clientes = []
            for registro in registros:
                cliente = Cliente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10], registro[11], registro[12], registro[13], registro[14])
                clientes.append(cliente)
            return clientes

    @classmethod
    def ultimo_codigo_usado(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._ULTIMO_CODIGO_USADO)
            registros = cursor.fetchall()
            clientes = []
            for registro in registros:
                cliente = Cliente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                  registro[12], registro[13], registro[14])
                clientes.append(cliente)
            return clientes

    @classmethod
    def buscar_cliente(cls, campo1, campo2, campo3, valor):
        # with CursorDelPool() as cursor:
        #     cursor.execute(cls._BUSCA_CLIENTE, (cliente_buscar,))
        #     registro = cursor.fetchone()
        #     if registro is not None:
        #         cliente = Cliente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10], registro[11], registro[12], registro[13], registro[14])
        #         return cliente
        #     else:
        #         return None
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM clientes WHERE {campo1} ILIKE %s OR {campo2} ILIKE %s OR {campo3} ILIKE %s ORDER BY codigo ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            clientes = []
            for registro in registros:
                cliente = Cliente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                            registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                            registro[12], registro[13], registro[14])
                clientes.append(cliente)
            return clientes

    @classmethod
    def insertar(cls, cliente):
        with CursorDelPool() as cursor:
            valores = (cliente.codigo, cliente.nombre, cliente.apellido, cliente.dni, cliente.empresa, cliente.cuit, cliente.telefono, cliente.email, cliente.direccion, cliente.numero, cliente.localidad, cliente.provincia, cliente.pais, cliente.observaciones, cliente.cond_iva)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Cliente ingresado: {cliente}')
            return cursor.rowcount

        try:
            archivo_clientes = open('clientes.txt', 'a', encoding='utf8')
            archivo_clientes.write(f'Cliente: {cliente}\n')
        except Exception as e:
            log.error(f'Error al abrir el archivo de clientes: {e}')
        finally:
            archivo.close()

    @classmethod
    def actualizar(cls, cliente):
        with CursorDelPool() as cursor:
            valores = (cliente.nombre, cliente.apellido, cliente.dni, cliente.empresa, cliente.cuit, cliente.telefono, cliente.email, cliente.direccion, cliente.numero, cliente.localidad, cliente.provincia, cliente.pais, cliente.observaciones, cliente.condiva, cliente.codigo)
            cursor.execute(cls._ACTUALIZAR, valores)
            log.debug(f'Cliente actualizado: {cliente}')
            return cursor.rowcount

    @classmethod
    def eliminar(cls, cliente):
        with CursorDelPool() as cursor:
            valores = (cliente.codigo,)
            cursor.execute(cls._ELIMINAR, valores)
            log.debug(f'Cliente eliminado: {cliente}')
            return cursor.rowcount

    @classmethod
    def importar_desde_excel(cls, ruta_archivo):
        try:
            import pandas as pd

            df = pd.read_excel(ruta_archivo)
            clientes = []
            for index, row in df.iterrows():
                cliente = Cliente(row['codigo'], row['nombre'], row['apellido'], row['dni'],
                                      row['empresa'], row['cuit'], row['telefono'], row['email'], row['direccion'],
                                      row['numero'], row['localidad'], row['provincia'], row['pais'], row['observaciones'], row['condiva'])
                clientes.append(cliente)

            # Insertar cada proveedor en la base de datos
            for cliente in clientes:
                cls.insertar(cliente)

            return clientes

        except Exception as e:
            log.error(f'Error al importar clientes desde Excel: {e}')
            sys.exit(1)

