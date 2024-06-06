
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView
from logger_base import log





class Funciones:
    '''Funcion para leer todos los campos de una tabla y transformarlo en una lista'''

    @classmethod
    def fx_leerTablaX(cls, tabla, desdeColumna=0, hastaCol=None, desdeFila=0, hastaFil=None):
        try:
            hastaColumna = tabla.columnCount()
            if hastaCol:
                hastaColumna = hastaCol

            hastaFila = tabla.rowCount()
            if hastaFil:
                hastaFila = hastaFil

            lista = []
            # Recorremos cada fila de la tabla
            for fila in range(tabla.rowCount()):
                # Creamos una sublista vacía para almacenar los valores de cada columna
                sublista = []
                # Recorremos cada columna de la fila
                for columna in range(desdeColumna, hastaColumna):
                    # Obtenemos el objeto QTableWidgetItem de la celda
                    item = tabla.item(fila, columna)
                    # Obtenemos el valor como una cadena
                    valor = item.text()
                    # Agregamos el valor a la sublista
                    sublista.append(valor)
                # Agregamos la sublista a la lista principal

                lista.append(sublista)
            # Imprimimos la lista resultante
            return lista
        except Exception as e:
            texto = f'Ocurrio un error durante la ejecucion de fx_leerTablaX: {e}'
            log.error(f'{texto}')



    '''Funcion para cargar informacion a cualquier tabla
    * recibe una lista de listas
    '''

    @classmethod
    def fx_cargarTablaX(cls, lista, tabla, limpiaTabla=True):
        try:
            fila = tabla.rowCount()
            # Preguntamos si vaciamos la tabla
            if limpiaTabla:
                tabla.clearContents()
                fila = 0

            for registro in lista:
                columna = 0
                tabla.setRowCount(fila + 1)
                for elemento in registro:
                    # Siempre string para cargar la tabla
                    celda = QTableWidgetItem(str(elemento))
                    celda.setTextAlignment(Qt.AlignCenter)
                    tabla.setItem(fila, columna, celda)
                    columna += 1
                fila += 1


        except Exception as e:
            texto = f'Ocurrio un error durante la ejecucion de fx_cargarTablaX: {e}'
            log.error(f'{texto}')

    @classmethod
    def fx_leer_seleccion_tabla(cls, tabla, eliminar_fila=False):
        try:
            if not tabla.selectionModel().selectedRows():
                texto = 'Por favor seleccione un registro de la tabla'
                texto2 = 'Recuerde que puede seleccionar varios registros a la vez'
                log.debug(f'{texto}')
                return [[], []]
            else:
                lista_rows = tabla.selectionModel().selectedRows()

                # Obtengo indice de filas seleccionadas
                indices = [row.row() for row in lista_rows]

                datos = []
                for row in lista_rows:
                    fila = []
                    for column in range(tabla.columnCount()):
                        fila.append(tabla.item(row.row(), column).text())
                    datos.append(fila)

                if eliminar_fila:
                    # elimino filas seleccionadas
                    indice_seleccion = 0
                    contador = 0
                    for i in indices:
                        if indice_seleccion == 0:
                            tabla.removeRow(i)
                            indice_seleccion += 1
                        else:
                            if i - contador < 0:
                                x = 0
                            else:
                                x = i - contador
                            tabla.removeRow(x)
                        contador += 1
                return [datos, indices]

            # Esto imprimirá una lista de listas con los datos de las filas seleccionadas
        except Exception as e:
            texto = f'Ocurrio un error durante la ejecucion de fx_leer_seleccion_tabla: {e}'
            texto2 = 'Verifique que todas las celdas de las filas seleccionadas estan completas'
            log.error(f'{texto}')


