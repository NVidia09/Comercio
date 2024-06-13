from conexion_db import Conexion
from cursor_del_pool import CursorDelPool
from logger_base import log
import sys

from negocio.empresa import Empresa


class EmpresaDAO:

    _SELECCIONAR = "SELECT * FROM empresa"
    _INSERTAR = "INSERT INTO empresa(razonsocial, nombrefantasia, cuit, categoria, iibb, inicioactividades, domicilio, localidad, provincia, pais, sucursales) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE empresa SET nombrefantasia=%s, cuit=%s, categoria=%s, iibb=%s, inicioactividades=%s, domicilio=%s, localidad=%s, provincia=%s, pais=%s, sucursales=%s WHERE razonsocial = %s'
    _ELIMINAR = "DELETE FROM empresa WHERE razonsocial = %s"



    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            empresas = []
            for registro in registros:
                empresa = Empresa(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7], registro[8], registro[9], registro[10])
                empresas.append(empresa)
            return empresas


    @classmethod
    def insertar(cls, empresa):
        with CursorDelPool() as cursor:
            valores = (empresa.razonsocial, empresa.nombrefantasia, empresa.cuit, empresa.categoria, empresa.iibb, empresa.inicioactividades, empresa.domicilio, empresa.localidad, empresa.provincia, empresa.pais, empresa.sucursales)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Datos de Empresa ingresados: {empresa}')
            return cursor.rowcount

        try:
            archivo_empresa = open('empresa.txt', 'a', encoding='utf8')
            archivo_empresa.write(f'Empresa: {empresa}\n')
        except Exception as e:
            log.error(f'Error al abrir el archivo de empresa: {e}')
        finally:
            archivo.close()

    @classmethod
    def actualizar(cls, empresa):
        with CursorDelPool() as cursor:
            valores = (empresa.nombrefantasia, empresa.cuit, empresa.categoria, empresa.iibb, empresa.inicioactividades, empresa.domicilio, empresa.localidad, empresa.provincia, empresa.pais, empresa.sucursales, empresa.razonsocial)
            cursor.execute(cls._ACTUALIZAR, valores)
            log.debug(f'Cliente actualizado: {empresa}')
            return cursor.rowcount

    @classmethod
    def eliminar(cls, razonsocial):
        with CursorDelPool() as cursor:
            valores = (razonsocial,)
            cursor.execute(cls._ELIMINAR, valores)
            log.debug(f'Datos de Empresa eliminados: {razonsocial}')
            return cursor.rowcount

    @classmethod
    def seleccionar_vacia(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            empresas = []
            if registros is not None:
                for registro in registros:
                    empresa = Empresa(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                      registro[6], registro[7], registro[8], registro[9], registro[10])
                    empresas.append(empresa)
            return empresas
