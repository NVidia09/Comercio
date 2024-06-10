import psycopg2

from conexion_db import Conexion
from cursor_del_pool import CursorDelPool
from logger_base import log
import sys

from negocio.articulo import Articulo


class ArticuloDAO:


    _SELECCIONAR = "SELECT * FROM articulos ORDER BY nombre, categoria ASC"
    _SELECCIONAR_ORDENADO = "SELECT * FROM articulos ORDER BY nombre, categoria ASC"
    _ULTIMO_CODIGO_USADO = "SELECT * FROM articulos ORDER BY codigo DESC FETCH FIRST 1 ROWS ONLY"
    _INSERTAR = "INSERT INTO articulos(codigo, nombre, modelo, marca, categoria, sku, color, caracteristica, precio_costo, precio_venta, iva, proveedor, tamaño, ancho, largo, profundidad, peso, peso_envalado, stock, margen_ganancia, stock_minimo, cod_barras) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _ACTUALIZAR = 'UPDATE articulos SET nombre=%s, modelo=%s, marca=%s, categoria=%s, sku=%s, color=%s, caracteristica=%s, precio_costo=%s, precio_venta=%s, iva=%s, proveedor=%s, tamaño=%s, ancho=%s, largo=%s, profundidad=%s, peso=%s, peso_envalado=%s, stock=%s, margen_ganancia=%s, stock_minimo=%s, cod_barras=%s WHERE codigo = %s'
    _ELIMINAR = "DELETE FROM articulos WHERE codigo = %s"
    _BUSCA_ARTICULO = "SELECT * FROM articulos WHERE codigo = %s"
    _BUSCA_ARTICULO_NOMBRE = "SELECT * FROM articulos WHERE nombre  LIKE %s"
    _BUSCA_ARTICULO_MODELO = "SELECT * FROM articulos WHERE modelo  LIKE %s"
    _FILTRAR_ARTICULO_IGUAL = "SELECT * FROM articulos WHERE %s LIKE %s ORDER BY codigo ASC"
    _SELECCIONAR_CATEGORIAS = "SELECT DISTINCT descripcion FROM categoria ORDER BY descripcion ASC"
    _SELECCIONAR_MARCAS = "SELECT DISTINCT descripcion FROM marcas ORDER BY descripcion ASC"
    _DESCONTAR_STOCK = "UPDATE articulos SET stock = stock - %s WHERE codigo = %s"




    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            articulos = []
            for registro in registros:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                  registro[12], registro[13], registro[14], registro[15], registro[16], registro[17], registro[18], registro[19], registro[20], registro[21])
                articulos.append(articulo)
            return articulos

    @classmethod
    def ultimo_codigo_usado(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._ULTIMO_CODIGO_USADO)
            registros = cursor.fetchall()
            articulos = []
            for registro in registros:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                    registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                    registro[12], registro[13], registro[14], registro[15], registro[16], registro[17],
                                    registro[18], registro[19], registro[20], registro[21])
                articulos.append(articulo)
            return articulos

    @classmethod
    def buscar_articulo(cls, articulo_buscar):
        with CursorDelPool() as cursor:
            cursor.execute(cls._BUSCA_ARTICULO, (articulo_buscar,))
            registro = cursor.fetchone()
            if registro is not None:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                  registro[12], registro[13], registro[14], registro[15], registro[16], registro[17], registro[18], registro[19], registro[20], registro[21])
                return articulo
            else:
                return None

    @classmethod
    def buscar_articulo_modelo(cls, articulo_buscar):
        with CursorDelPool() as cursor:
            cursor.execute(cls._BUSCA_ARTICULO_MODELO, (articulo_buscar,))
            registro = cursor.fetchone()
            if registro is not None:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                    registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                    registro[12], registro[13], registro[14], registro[15], registro[16], registro[17],
                                    registro[18], registro[19], registro[20], registro[21])
                return articulo
            else:
                return None

    @classmethod
    def buscar_articulo_nombre(cls, campo1, campo2, campo3, valor):
        # with CursorDelPool() as cursor:
        #     cursor.execute(cls._BUSCA_ARTICULO_NOMBRE, (articulo_buscar3,))
        #     registro = cursor.fetchone()
        #     if registro is not None:
        #         articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
        #                             registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
        #                             registro[12], registro[13], registro[14], registro[15], registro[16], registro[17],
        #                             registro[18], registro[19], registro[20], registro[21])
        #         return articulo
        #     else:
        #         return None
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM articulos WHERE {campo1} ILIKE %s OR {campo2}::text ILIKE %s OR {campo3}::text ILIKE %s ORDER BY codigo ASC"
            cursor.execute(query, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
            registros = cursor.fetchall()
            articulos = []
            for registro in registros:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                            registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                            registro[12], registro[13], registro[14], registro[15], registro[16], registro[17], registro[18], registro[19], registro[20], registro[21])
                articulos.append(articulo)
            return articulos

    @classmethod
    def buscar_articulo_lector(cls, campo1, valor):
        # with CursorDelPool() as cursor:
        #     cursor.execute(cls._BUSCA_ARTICULO_NOMBRE, (articulo_buscar3,))
        #     registro = cursor.fetchone()
        #     if registro is not None:
        #         articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
        #                             registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
        #                             registro[12], registro[13], registro[14], registro[15], registro[16], registro[17],
        #                             registro[18], registro[19], registro[20], registro[21])
        #         return articulo
        #     else:
        #         return None
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM articulos WHERE CAST(cod_barras AS TEXT) ILIKE %s ORDER BY codigo ASC"
            cursor.execute(query, (f'%{valor}%', ))
            registros = cursor.fetchall()
            articulos = []
            for registro in registros:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                    registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                    registro[12], registro[13], registro[14], registro[15], registro[16], registro[17],
                                    registro[18], registro[19], registro[20], registro[21])
                articulos.append(articulo)
            return articulos

    @classmethod
    def insertar(cls, articulo):
        with CursorDelPool() as cursor:
            valores = (articulo.codigo, articulo.nombre, articulo.modelo, articulo.marca, articulo.categoria, articulo.sku, articulo.color, articulo.caracteristica, articulo.precio_costo, articulo.precio_venta, articulo.iva, articulo.proveedor, articulo.tamaño, articulo.ancho, articulo.largo, articulo.profundidad, articulo.peso, articulo.peso_envalado, articulo.stock, articulo.margen_ganancia, articulo.stock_minimo, articulo.cod_barras)
            cursor.execute(cls._INSERTAR, valores)
            log.debug(f'Articulo ingresado: {articulo}')

            try:
                archivo_articulos = open('articulos.txt', 'a', encoding='utf8')
                archivo_articulos.write(f'Articulo: {articulo}\n')
            except Exception as e:
                log.error(f'Error al abrir el archivo de artículos: {e}')
            finally:
                archivo_articulos.close()

            return cursor.rowcount


    @classmethod
    def actualizar(cls, articulo):
        with CursorDelPool() as cursor:
            valores = (articulo.nombre, articulo.modelo, articulo.marca, articulo.categoria, articulo.sku, articulo.color, articulo.caracteristica, articulo.precio_costo, articulo.precio_venta, articulo.iva, articulo.proveedor, articulo.tamaño, articulo.ancho, articulo.largo, articulo.profundidad, articulo.peso, articulo.peso_envalado, articulo.stock, articulo.margen_ganancia, articulo.stock_minimo, articulo.cod_barras, articulo.codigo)
            cursor.execute(cls._ACTUALIZAR, valores)
            log.debug(f'Articulo actualizado: {articulo}')
            return cursor.rowcount

    @classmethod
    def eliminar(cls, articulo):
        with CursorDelPool() as cursor:
            valores = (articulo.codigo,)
            cursor.execute(cls._ELIMINAR, valores)
            log.debug(f'Articulo eliminado: {articulo}')
            return cursor.rowcount

    @classmethod
    def filtrar_articulo_igual(cls, campo, valor):

        with CursorDelPool() as cursor:
            query = f"SELECT * FROM articulos WHERE {campo} LIKE %s ORDER BY codigo ASC"
            cursor.execute(query, (f'%{valor}%',))
            registros = cursor.fetchall()
            articulos = []
            for registro in registros:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                            registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                            registro[12], registro[13], registro[14], registro[15], registro[16], registro[17], registro[18], registro[19], registro[20], registro[21])
                articulos.append(articulo)
            return articulos

    @classmethod
    def filtrar_articulo_mayor(cls, campo, valor):

        with CursorDelPool() as cursor:
            query = f"SELECT * FROM articulos WHERE {campo} > %s ORDER BY codigo ASC"
            cursor.execute(query, (f'{valor}',))
            registros = cursor.fetchall()
            articulos = []
            for registro in registros:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                            registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                            registro[12], registro[13], registro[14], registro[15], registro[16], registro[17], registro[18], registro[19], registro[20], registro[21])
                articulos.append(articulo)
            return articulos

    @classmethod
    def filtrar_articulo_menor(cls, campo, valor):

        with CursorDelPool() as cursor:
            query = f"SELECT * FROM articulos WHERE {campo} < %s ORDER BY codigo ASC"
            cursor.execute(query, (f'{valor}',))
            registros = cursor.fetchall()
            articulos = []
            for registro in registros:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                            registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                            registro[12], registro[13], registro[14], registro[15], registro[16], registro[17], registro[18], registro[19], registro[20], registro[21])
                articulos.append(articulo)
            return articulos

    @classmethod
    def filtrar_articulo_entre(cls, campo, valor1, valor2):
        with CursorDelPool() as cursor:
            query = f"SELECT * FROM articulos WHERE {campo} > %s AND {campo} < %s ORDER BY codigo ASC"
            cursor.execute(query, (valor1, valor2))
            registros = cursor.fetchall()
            articulos = []
            for registro in registros:
                articulo = Articulo(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                    registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                    registro[12], registro[13], registro[14], registro[15], registro[16], registro[17],
                                    registro[18], registro[19], registro[20], registro[21])
                articulos.append(articulo)
            return articulos

    @classmethod
    def seleccionar_categorias(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR_CATEGORIAS)
            registros = cursor.fetchall()
            categorias = [registro[0] for registro in registros]
            return categorias

    @classmethod
    def agregar_categoria(cls, categoria):
        with CursorDelPool() as cursor:
            query = "INSERT INTO categoria (descripcion) VALUES (%s)"
            cursor.execute(query, (categoria,))
            return cursor.rowcount

    @classmethod
    def seleccionar_marcas(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR_MARCAS)
            registros = cursor.fetchall()
            marcas = [registro[0] for registro in registros]
            return marcas

    @classmethod
    def agregar_marca(cls, marca):
        with CursorDelPool() as cursor:
            query = "INSERT INTO marcas (descripcion) VALUES (%s)"
            cursor.execute(query, (marca,))
            return cursor.rowcount

    @classmethod
    def verificar_existencias(cls, articulo):
        with CursorDelPool() as cursor:
            query = "SELECT stock FROM articulos WHERE codigo = %s"
            codigo = articulo.text()  # Get the text value of the QTableWidgetItem
            cursor.execute(query, (codigo,))
            registro = cursor.fetchone()
            if registro is not None:
                return registro[0]
            else:
                return None

    @classmethod
    def importar_desde_excel(cls, ruta_archivo):
        try:
            import pandas as pd

            df = pd.read_excel(ruta_archivo)
            articulos = []
            for index, row in df.iterrows():
                articulo = Articulo(row['codigo'], row['nombre'], row['modelo'], row['marca'],
                                      row['categoria'], row['sku'], row['color'], row['caracteristica'], row['precio_costo'],
                                      row['precio_venta'], row['iva'], row['proveedor'], row['tamaño'], row['ancho'], row['largo'], row['profundidad'], row['peso'], row['peso_envalado'], row['stock'], row['margen_ganancia'], row['stock_minimo'], row['cod_barras'])
                articulos.append(articulo)

            # Insertar cada proveedor en la base de datos
            for articulo in articulos:
                cls.insertar(articulo)

            return articulos
        except Exception as e:
            log.error(f'Error al importar artículos desde Excel: {e}')
            sys.exit(1)