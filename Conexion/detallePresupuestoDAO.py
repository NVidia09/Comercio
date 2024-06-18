from Conexion.cursor_del_pool import CursorDelPool
from Conexion.logger_base import log

from Conexion.detallePresupuesto import detallePresupuesto


class detallePresupuestoDAO:

    _SELECCIONAR = "SELECT * FROM detallepresupuesto ORDER BY codpresupuesto DESC"
    _INSERTAR = "INSERT INTO detallepresupuesto(codpresupuesto, codarticulo, descripcion, cantidad, precio_unitario, subtotal, importe_iva) VALUES(%s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE detallepresupuesto SET codpresupuesto=%s, codarticulo=%s, descripcion=%s, cantidad=%s, precio_unitario=%s, subtotal=%s, importe_iva=%s, total=%s  WHERE codpresupuesto = %s'
    _ELIMINAR = "DELETE FROM detallepresupuesto WHERE codpresupuesto = %s"
    _BUSCA_PRESUPUESTO = "SELECT * FROM detallepresupuesto WHERE codpresupuesto = %s"
    _BUSCA_DETALLE = "SELECT * FROM detallepresupuesto WHERE codpresupuesto = %s"

    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            detallepresupuestos = []
            for registro in registros:
                detallepresupuestos = detallePresupuesto(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6])
                detallepresupuestos.append(detallepresupuestos)
            return detallepresupuestos

    @classmethod
    def buscar_presupuesto(cls, campo1, campo2, campo3, valor):
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM presupuestos WHERE {campo1} ILIKE %s OR {campo2} ILIKE %s OR {campo3} ILIKE %s ORDER BY codpresupuesto ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            detallepresupuestos = []
            for registro in registros:
                detallepresupuesto = detallePresupuesto(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6])
                detallepresupuestos.append(detallepresupuesto)
            return detallepresupuestos

    @classmethod
    def busca_detalle(cls, detalle_buscar):
        with CursorDelPool() as cursor:
            cursor.execute(cls._BUSCA_DETALLE, (detalle_buscar,))
            registros = cursor.fetchall()
            detallepresupuestos = []
            for registro in registros:
                detalle = detallePresupuesto(registro[0], registro[1], registro[2], registro[3], registro[4],
                                             registro[5], registro[6])
                detallepresupuestos.append(detalle)
            return detallepresupuestos

    @classmethod
    def insertar(cls, detallepresupuesto):
        with CursorDelPool() as cursor:
            valores = (detallepresupuesto.codpresupuesto, detallepresupuesto.codarticulo, detallepresupuesto.descripcion, detallepresupuesto.cantidad, float(detallepresupuesto.precio_unitario), detallepresupuesto.subtotal, detallepresupuesto.importe_iva)
            # for df in detallefactura:
            #     valores = (
            #     df.serie, df.codfactura, df.codarticulo, df.descripcion, df.cantidad, df.precioventa, df.importe,
            #     df.iva)
            #     # rest of your code
            print(valores)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Presupuesto ingresada: {detallepresupuesto}')
            return cursor.rowcount

    @classmethod
    def seleccionar_detalle_presupuesto(cls, campo1, campo2):
        with CursorDelPool() as cursor:
            query = "SELECT * FROM detallepresupuesto WHERE CAST(codpresupuesto AS TEXT) LIKE %s ORDER BY codpresupuesto ASC"
            cursor.execute(query, (f'%{campo1}%', f'%{campo2}%'))
            registros = cursor.fetchall()
            presupuestos = []
            for registro in registros:
                detallepresupuesto = detallePresupuesto(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6])
                presupuestos.append(detallepresupuesto)
            return presupuestos

    @classmethod
    def eliminar(cls, codpresupuesto):
        with CursorDelPool() as cursor:
            valores = (codpresupuesto,)
            cursor.execute(cls._ELIMINAR, valores)
            log.debug(f'Datos de Presupuesto eliminados: {codpresupuesto}')

