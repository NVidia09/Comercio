from cursor_del_pool import CursorDelPool
from logger_base import log
from negocio.presupuesto import Presupuesto


class PresupuestoDAO:

        _SELECCIONAR = "SELECT * FROM presupuestos ORDER BY codpresupuesto DESC"
        _INSERTAR = "INSERT INTO presupuestos(codpresupuesto, fecha, codcliente, cliente, subtotal, iva, total, fecha_vto) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        _ACTUALIZAR = 'UPDATE presupuestos SET codpresupuesto=%s, fecha=%s, codcliente=%s, cliente=%s, estado=%s, subtotal=%s, iva=%s, total=%s, formapago=%s, tipo=%s, entrega=%s WHERE codpresupuesto = %s'
        _ELIMINAR = "DELETE FROM presupuestos WHERE codpresupuesto = %s"
        _BUSCA_PRESUPUESTO = "SELECT * FROM presupuestos WHERE codpresupuesto = %s"
        _BUSCA_PRESUP_PENDIENTE = "SELECT * FROM presupuestos WHERE entrega = 'ENVIO' ORDER BY codpresupuesto DESC"
        _BUSCA_PRESUP_COBRAR = "SELECT * FROM presupuestos WHERE formapago = %s AND formapago = %s ORDER BY codpresupuesto DESC"
        _COBRAR_PRESUP_CLIENTE = "SELECT * FROM presupuestos WHERE estado = 'PENDIENTE' AND codpresupuesto = %s AND codcliente = %s ORDER BY codpresupuesto DESC"

        @classmethod
        def seleccionar(cls):
            with CursorDelPool() as cursor:
                cursor.execute(cls._SELECCIONAR)
                registros = cursor.fetchall()
                presupuestos = []
                for registro in registros:
                    presupuesto = Presupuesto(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7])
                    presupuestos.append(presupuesto)
                return presupuestos

        @classmethod
        def buscar_presupuesto(cls, campo1, valor):
            with CursorDelPool() as cursor:
                query = f"SELECT * FROM presupuestos WHERE {campo1}::text ILIKE %s ORDER BY codpresupuesto ASC"
                cursor.execute(query, (f'%{valor}%',))
                registros = cursor.fetchall()
                presupuestos = []
                for registro in registros:
                    presupuesto = Presupuesto(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7])
                    presupuestos.append(presupuesto)
                return presupuestos

        @classmethod
        def insertar(cls, presupuesto):
            with CursorDelPool() as cursor:
                valores = (presupuesto.codpresupuesto, presupuesto.fecha, presupuesto.codcliente, presupuesto.cliente, presupuesto.subtotal, presupuesto.iva, presupuesto.total, presupuesto.fecha_vto)
                cursor.execute(cls._INSERTAR, valores)
                log.debug(f'Presupuesto ingresado: {presupuesto}')
                return cursor.rowcount

        @classmethod
        def eliminar(cls, codpresupuesto):
            with CursorDelPool() as cursor:
                valores = (codpresupuesto,)
                cursor.execute(cls._ELIMINAR, valores)
                log.debug(f'Datos de Presupuesto eliminados: {codpresupuesto}')

        @classmethod
        def actualizar(cls, presupuesto):
            with CursorDelPool() as cursor:
                valores = (presupuesto.codpresupuesto, presupuesto.fecha, presupuesto.codcliente, presupuesto.cliente, presupuesto.subtotal, presupuesto.iva, presupuesto.total, presupuesto.codpresupuesto)
                cursor.execute(cls._ACTUALIZAR, valores)
                log.debug(f'Presupuesto actualizado: {presupuesto}')
                return cursor.rowcount

