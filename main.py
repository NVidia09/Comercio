import base64
import os
import shutil
import tempfile

import pandas as pd
from afip import Afip, afip
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox
from PyQt5.uic.properties import QtGui
from PyQt5 import QtGui
from pdfkit import pdfkit
from reportlab.pdfgen import canvas
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt

import json

from Conexion.cursor_del_pool import CursorDelPool
from Conexion.clienteDAO import ClienteDAO
from Conexion.articuloDAO import ArticuloDAO
from Conexion.despacho import Despacho
from Conexion.despachoDAO import DespachoDAO
from Conexion.logger_base import log
from PyQt5 import QtWidgets
import sys

from Conexion.pruebadni import DNI_captura
from Interfaz.diseño_nuevo import Ui_MainWindow  # Importa el diseño convertido
from Conexion.EmpresaDAO import EmpresaDAO
from Conexion.articulo import Articulo
from Conexion.cajaDAO import CajaDAO
from Conexion.cliente import Cliente
from Conexion.detalleFactura import detalleFactura
from Conexion.detalleFacturaDAO import detalleFacturaDAO
from Conexion.detallePresupuesto import detallePresupuesto
from Conexion.detallePresupuestoDAO import detallePresupuestoDAO
from Conexion.empresa import Empresa
from Conexion.factura import Factura
from Conexion.facturaDAO import FacturaDAO
from Conexion.funciones import Funciones
from Conexion.pendientes import Pendiente
from Conexion.pendientesDAO import PendientesDAO
from Conexion.presupuesto import Presupuesto
from Conexion.presupuestoDAO import PresupuestoDAO
from Conexion.proveedor import Proveedor
from Conexion.proveedorDAO import ProveedorDAO
from Interfaz.ventana_agregar_articulo import Ui_ventana_agregar_articulo
from Interfaz.ventana_agregar_cliente_factura import Ui_ventana_agregar_cliente_factura
from Interfaz.ventana_datos_empresa import Ui_ventana_Datos_Empresa
from Interfaz.ventana_marca import Ui_ventana_Marca
from Interfaz.ventana_nueva_categoria import Ui_ventana_nueva_categoria
from Interfaz.ventana_nueva_marca import Ui_ventana_nueva_marca
from Interfaz.ventana_proveedor import Ui_ventana_proveedores
from Interfaz.ventana_categoria import Ui_ventana_Categorias
import locale
from datetime import datetime, timedelta

import resources_rc

# Establecer la localización en español (España)
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

item = 0
categoria_seleccionada = ""

try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "Gestion.Empresas.Comercio.v1.0"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)  # Inicializa el diseño
        # self.Ui_ventana_agregar_articulo = QtWidgets.QDialog()
        self.tableWidget_SelecionarArticuloFactura = QtWidgets.QTableWidget()

        self.Ui_ventana_Datos_Empresa = QtWidgets.QDialog()
        self.ui_ventana_empresa = Ui_ventana_Datos_Empresa()
        self.ui_ventana_empresa.setupUi(self.Ui_ventana_Datos_Empresa)

        self.dialogo_categoria = QtWidgets.QDialog()
        self.ui = Ui_ventana_Categorias()
        self.ui.setupUi(self.dialogo_categoria)

        self.dialogo_agregar_cliente_factura = QtWidgets.QDialog()
        self.ui_agregar_cliente_Fact = Ui_ventana_agregar_cliente_factura()
        self.ui_agregar_cliente_Fact.setupUi(self.dialogo_agregar_cliente_factura)

        # self.Ui_ventana_Datos_Empresa = QtWidgets.QDialog()
        # self.ui_ventana_empresa = Ui_ventana_Datos_Empresa()
        # self.ui_ventana_empresa.setupUi(self.Ui_ventana_Datos_Empresa)

        self.dateEdit_fechavencimientoFactura.setDate(datetime.now())
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.bt_Articulos.clicked.connect(self.listar_articulos)
        self.bt_Clientes.clicked.connect(self.listar_clientes)
        self.bt_Proveedores.clicked.connect(self.listar_proveedores)
        self.bt_Empresa.clicked.connect(self.listar_empresa)
        # self.bt_grabar_datos_empresa.clicked.connect(self.grabar_datos_empresa)

        self.bt_inicio.clicked.connect(self.pagina_inicio)

        self.bt_Facturacion.clicked.connect(self.modulo_facturacion)
        self.bt_nuevaFactura.clicked.connect(self.nueva_factura)
        self.tableWidget_ultimasFacturas.cellClicked.connect(self.seleccionar_factura)

        self.bt_NuevoArticulo.clicked.connect(self.mostrar_insertar_articulo)
        self.bt_CancelarNvoArticulo.clicked.connect(self.borrar_campos_nuevo_articulo)
        # self.bt_BuscarArticulo.clicked.connect(self.buscar_articulo)
        self.lineEdit_BuscarArticulo.textChanged.connect(self.buscar_articulo)
        self.bt_ModificarArticulo.clicked.connect(self.modificar_articulo)
        self.bt_EliminarArticulo.clicked.connect(self.eliminar_articulo)
        self.bt_importar_articulos.clicked.connect(self.importar_articulos)
        self.bt_descargar_articulos.clicked.connect(self.descargar_articulos)
        # self.Bt_Actualizar.clicked.connect(self.mostrar_actualizar_persona)
        # self.Bt_Eliminar.clicked.connect(self.mostrar_eliminar_persona)
        self.bt_Minimizar.clicked.connect(self.showMinimized)
        self.bt_Cerrar.clicked.connect(self.close)
        self.bt_Maximizar.clicked.connect(self.showMaximized)
        self.bt_Restaurar.clicked.connect(self.showNormal)
        self.label_capturaSeleccion.hide()
        # obtener "id" al hacer click en un la tabla Articulos
        self.tabla_Articulos.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.tabla_Articulos.itemSelectionChanged.connect(self.on_selec_change)
        # obtener "id" al hacer click en un la tabla Clientes
        self.tablaClientes.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.tablaClientes.itemSelectionChanged.connect(self.on_selec_change_cliente)
        # llamar método para filtrar articulos
        self.bt_FiltrarArticulo.clicked.connect(self.filtrar_articulo)
        # empiezan los botones de los clientes
        self.lineEdit_BuscarArticulo_2.textChanged.connect(self.buscar_cliente)
        self.bt_ModificarCliente.clicked.connect(self.modificar_cliente)
        self.bt_EliminarCliente.clicked.connect(self.eliminar_cliente)
        self.bt_NuevoCliente.clicked.connect(self.mostrar_insertar_cliente)
        self.bt_BuscarCliente.clicked.connect(self.buscar_cliente)
        self.bt_importar_clientes.clicked.connect(self.importar_clientes)
        self.bt_descargar_clientes.clicked.connect(self.descargar_clientes)
        self.bt_seleccionaClienteNvaFactura_4.clicked.connect(self.cliente_afip)
        # empiezan los botones de los proveedores
        self.lineEdit_BuscarArticulo_3.textChanged.connect(self.buscar_proveedor)
        self.bt_ModificarProveedor.clicked.connect(self.modificar_proveedor)
        self.bt_NuevoProveedor.clicked.connect(self.mostrar_insertar_proveedor)
        self.bt_EliminarProveedor.clicked.connect(self.eliminar_proveedor)
        self.bt_BuscarProveedor.clicked.connect(self.buscar_proveedor)
        self.bt_importar_proveedores.clicked.connect(self.importar_proveedores)
        self.bt_descargar_proveedores.clicked.connect(self.descargar_proveedores)
        self.bt_seleccionaClienteNvaFactura_5.clicked.connect(self.proveedor_afip)

        # acciones botones selecciona/agregar nueva categoría
        self.bt_CategoriaNvoArticulo.clicked.connect(self.seleccionar_categoria)
        # acciones botones selecciona/agregar nueva marca
        self.bt_MarcaNvoArticulo.clicked.connect(self.seleccionar_marca)
        # acciones botones selecciona/agregar nuevo proveedor
        self.bt_ProveedorNvoArticulo.clicked.connect(self.seleccionar_proveedor)

        self.ui_ventana_empresa.bt_cancelar_datos_empresa.clicked.connect(self.Ui_ventana_Datos_Empresa.close)
        self.ui_ventana_empresa.bt_modificar_datos_empresa.clicked.connect(self.modificar_datos_empresa)
        self.ui_ventana_empresa.bt_cambiar_datos_empresa.clicked.connect(self.cambiar_datos_empresa)
        self.ui_ventana_empresa.bt_eliminar_datos_empresa_2.clicked.connect(self.eliminar_datos_empresa)
        self.ui_ventana_empresa.bt_subir_foto_empresa.clicked.connect(self.subir_foto_empresa)
        # self.factura_logo = QtWidgets.QLabel(self)

        ##################################################################################
        #
        #                             PAGINA DE INICIO
        #
        ##################################################################################
        self.stackedWidget.setCurrentIndex(14)
        self.crear_grafico_ventas("DIARIO")
        # self.crear_grafico_ventas()
        self.grafico_ventas_por_categoria()
        self.graficoFechas.currentIndexChanged.connect(self.graficoFechas_change)

        ##################################################################
        ##
        ##                     AGREGAR CLIENTE A NUEVA FACTURA
        ##
        ##################################################################

        self.bt_seleccionaClienteNvaFactura.clicked.connect(self.seleccionar_cliente_nueva_factura)
        self.ui_agregar_cliente_Fact.lineEdit_BuscarItemArticuloNvaFactura.textChanged.connect(
            self.buscar_cliente_nueva_factura)
        self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.doubleClicked.connect(
            self.agregar_cliente_click)
        self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.doubleClicked.connect(
            self.agregar_cliente_click_presupuesto)
        self.bt_facturaPDF.clicked.connect(self.factura_pdf)

        #################################################################
        #
        #               BUSCAR ARTICULOS EN NUEVA FACTURA
        #
        #################################################################

        # self.lineEdit_BuscarArticuloNvaFactura1.textChanged.connect(self.buscar_articulo_nueva_factura_lector)
        self.lineEdit_BuscarArticuloNvaFactura1.returnPressed.connect(self.buscar_articulo_nueva_factura_lector)
        self.bt_AgregarArticuloNvaFactura.clicked.connect(self.agregar_articulo_nueva_factura)
        self.dialogo_agregar_Art_Factura = QtWidgets.QDialog()
        self.ui_ventana_agr_articulo = Ui_ventana_agregar_articulo()
        self.ui_ventana_agr_articulo.setupUi(self.dialogo_agregar_Art_Factura)
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.doubleClicked.connect(
            lambda: self.agregar_articulo_nueva_factura2())
        self.bt_Eliminar_Articulo_Detalle.clicked.connect(self.eliminar_articulo_detalle)

        #################################################################
        #
        #            ACTUALIZAR EL VALOR DEL PRECIO UNITARIO AL MODIFICAR LA CELDA DE CANTIDAD DEL ARTICULO
        #################################################################
        self.tableWidgetDetalleNvaFactura.cellChanged.connect(self.actualizar_subtotal)
        self.tableWidgetDetalleNvaFactura.cellChanged.connect(self.actualizar_subtotal_factura)

        ################################################################
        #
        #           PROCESO DE GUARDADO DE LA FACTURA
        #
        ################################################################
        self.bt_Facturar.clicked.connect(self.guardar_factura)
        self.bt_CancelarFactura.clicked.connect(self.cancelar_factura)
        self.bt_descargar_ultimas_facturas.clicked.connect(self.descargar_facturas)
        self.bt_descargar_pendientes_entrega.clicked.connect(self.descargar_facturas_pendientes_entrega)

        ################################################################
        #
        #           SELECCIONAR FACTURA POR CLIENTE
        #
        ################################################################
        # self.tablaClientes.itemSelectionChanged.connect(self.seleccionar_factura_cliente)
        self.tablaClientes.cellClicked.connect(self.seleccionar_factura_cliente)
        # self.tablaFacturasCliente.itemSelectionChanged.connect(self.seleccionar_detalle_factura_cliente)
        self.tablaFacturasCliente.cellClicked.connect(self.seleccionar_detalle_factura_cliente)

        ###############################################################
        #
        #           COBRAR FACTURAS PENDIENTES
        #
        ###############################################################
        self.bt_Cobrar_Factura_Cliente.clicked.connect(self.cobrar_factura_cliente)
        self.tablaCobrarFacturasCliente.cellClicked.connect(self.seleccionar_detalle_factura_cobrar_cliente)
        self.tableWidget_facturasImpagas.cellDoubleClicked.connect(self.cobrar_factura_cliente_facturacion)
        self.bt_Cobrar.clicked.connect(self.cobrar_factura_cliente_pendiente)
        self.comboBox_TpoPagoCobrarFactura.currentTextChanged.connect(self.on_combobox_changed)
        self.bt_descargar_pendientes_cobro.clicked.connect(self.descargar_pendientes)

        ###############################################################
        #
        #           SECCION CAJA
        #
        ###############################################################
        self.bt_Caja.clicked.connect(self.modulo_caja)
        self.comboBox_FormaPagoNvoCobro.currentTextChanged.connect(self.combo_formapago_change)
        self.bt_NvoCobro.clicked.connect(self.nuevo_cobro)
        self.bt_CancelarNvoCobro.clicked.connect(self.cancelar_nuevo_cobro)
        self.bt_descargar_ultimos_cobros.clicked.connect(self.descargar_ultimos_cobros)
        self.bt_descargar_ultimos_pagos.clicked.connect(self.descargar_ultimos_pagos)

        ###############################################################
        #
        #           SECCION STOCK
        #
        ###############################################################
        self.pushButton_ModificarPrecio.clicked.connect(self.modulo_stock_mod_precio)
        self.pushButton_ModificarStock.clicked.connect(self.modulo_stock_mod_stock)
        self.comboBox_ModificarPrecio_2.currentTextChanged.connect(self.combo_mod_precio_change)

        ###############################################################
        #
        #           SECCION CTA. CTE.
        #
        ###############################################################
        self.bt_ctacte_cliente.clicked.connect(self.modulo_ctacte_cliente)
        self.lineEdit_BuscarClienteCtaCte.textChanged.connect(self.buscar_cliente_ctacte)
        self.tablaClientes_3.cellClicked.connect(self.seleccionar_factura_cliente_ctacte)
        self.tablaFacturasCliente_3.cellClicked.connect(self.seleccionar_pendiente_cliente_ctacte)
        self.bt_NvoCobro_2.clicked.connect(self.cobrar_factura_pendiente_ctacte)

        ##############################################################
        #
        #          SECCION PRESUPUESTOS
        #
        ##############################################################
        self.bt_Presupuestos.clicked.connect(self.modulo_presupuestos)
        self.bt_seleccionaClienteNvaFactura_3.clicked.connect(self.seleccionar_cliente_nuevo_presupuesto)
        self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.doubleClicked.connect(
            self.agregar_cliente_click)
        self.bt_AgregarArticuloNvaFactura_3.clicked.connect(self.agregar_articulo_nuevo_presupuesto)
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.doubleClicked.connect(
            lambda: self.agregar_articulo_nuevo_presupuesto2())
        self.tableWidgetDetalleNvaFactura_3.cellChanged.connect(self.actualizar_subtotal_presu)
        self.tableWidgetDetalleNvaFactura_3.cellChanged.connect(self.actualizar_subtotal_presupuesto)
        self.bt_Grabar_presupuesto.clicked.connect(self.guardar_presupuesto)
        self.bt_Nuevo_presupuesto_3.clicked.connect(self.modulo_presupuestos_nuevo)
        self.tableWidgetPresupuestos.cellClicked.connect(self.seleccionar_presupuesto)
        self.bt_Eliminar_Presupuesto.clicked.connect(self.eliminar_presupuesto)
        self.bt_Eliminar_Articulo_Detalle_Presupuesto.clicked.connect(self.eliminar_articulo_detalle_presupuesto)
        # self.tableWidgetDetalleNvaFactura_3.cellChanged.connect(self.actualizar_subtotal_presupuesto)
        self.bt_Facturar_presupuesto_2.clicked.connect(self.facturar_presupuesto)
        self.bt_CancelarFactura_3.clicked.connect(self.cancelar_presupuesto)
        self.bt_presupuestoPDF.clicked.connect(self.presupuesto_pdf)

        ###############################################################################################
        #
        #                        DESPACHOS
        #
        ###############################################################################################
        self.bt_Despacho.clicked.connect(self.modulo_despachos)
        self.tableWidget_ultimasFacturas_3.cellClicked.connect(self.seleccionar_factura_despacho)
        self.bt_escanear_documentos.clicked.connect(self.escanear_documentos)
        self.bt_Despachar.clicked.connect(self.despachar_factura)
        self.bt_VerDespacho.clicked.connect(self.ver_despacho)


    def pagina_inicio(self):
        self.stackedWidget.setCurrentIndex(14)
        ######################################################
        # CANTIDAD DE FACTURAS DEL DIA
        # 1. Obtener la fecha actual
        fecha_actual = datetime.now().date()

        # 2. Formatear la fecha actual al formato utilizado en la base de datos (Asumiendo formato YYYY-MM-DD)
        fecha_formateada = fecha_actual.strftime('%Y-%m-%d')

        # 3. Crear una consulta SQL
        consulta_sql = f"""
            SELECT COUNT(*) FROM facturas
            WHERE fecha = '{fecha_formateada}'
            """

        # 4. Ejecutar la consulta SQL
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql)
            resultado = cursor.fetchone()

        # 5. Asignar el resultado de la consulta a la variable facturasDia
        facturasDia = resultado[0] if resultado else 0
        self.label_423.setText(str(facturasDia))
        ###############################################################
        # CANTIDAD PRESUPUESTOS DEL DIA
        # 3. Crear una consulta SQL
        consulta_sql = f"""
                    SELECT COUNT(*) FROM presupuestos
                    WHERE fecha = '{fecha_formateada}'
                    """

        # 4. Ejecutar la consulta SQL
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql)
            resultado = cursor.fetchone()

        # 5. Asignar el resultado de la consulta a la variable facturasDia
        presupuestosDia = resultado[0] if resultado else 0
        self.label_424.setText(str(presupuestosDia))

        ###############################################################
        #  VENTAS DEL DIA
        # Crear una consulta SQL para sumar el total facturado del día
        consulta_sql_total = f"""
                SELECT SUM(total) FROM facturas
                WHERE fecha = '{fecha_formateada}'
                """

        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        totalFacturadoDia = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_391.setText(str(totalFacturadoDia))

        ###############################################################
        #  COBROS DEL DIA
        # Crear una consulta SQL para sumar el total facturado del día
        consulta_sql_total = f"""
        SELECT SUM(total) FROM caja
        WHERE fecha = '{fecha_formateada}' AND tipo = 'COBRO'
        """

        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        cobrosDia = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_392.setText(str(cobrosDia))

        ###############################################################
        # TOTAL DEL DIA
        totalDia = totalFacturadoDia
        self.label_393.setText(str(totalDia))

        ###############################################################
        # VENTAS DE LA SEMANA
        # Crear una consulta SQL para sumar el total facturado de la semana
        consulta_sql_total = f"""
        SELECT SUM(total) FROM facturas
        WHERE fecha BETWEEN '{fecha_actual - timedelta(days=fecha_actual.weekday())}' AND '{fecha_actual + timedelta(days=6 - fecha_actual.weekday())}'
        """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        facturasSemana = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_401.setText(str(facturasSemana))

        ###############################################################
        # COBROS DE LA SEMANA
        # Convertir fecha_actual y fecha_actual - 30 días al formato 'dd/mm/yyyy, hh:mm:ss'
        fecha_inicio = (fecha_actual - timedelta(days=7)).strftime('%d/%m/%Y, %H:%M:%S')
        fecha_fin = fecha_actual.strftime('%d/%m/%Y, %H:%M:%S')

        consulta_sql_total = f"""
                SELECT SUM(total) FROM caja
                WHERE TO_TIMESTAMP(fecha, 'DD/MM/YYYY, HH24:MI:SS') BETWEEN TO_TIMESTAMP('{fecha_inicio}', 'DD/MM/YYYY, HH24:MI:SS') AND TO_TIMESTAMP('{fecha_fin}', 'DD/MM/YYYY, HH24:MI:SS') AND tipo = 'COBRO'
                """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        cobrosSemana = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_402.setText(str(cobrosSemana))

        ###############################################################
        # TOTAL DE LA SEMANA
        totalSemana = facturasSemana
        self.label_406.setText(str(totalSemana))

        ###############################################################
        # VENTAS DEL MES
        # Crear una consulta SQL para sumar el total facturado del mes
        consulta_sql_total = f"""
        SELECT SUM(total) FROM facturas
        WHERE fecha BETWEEN '{(fecha_actual - timedelta(days=30)).strftime('%Y-%m-%d')}' AND '{fecha_actual.strftime('%Y-%m-%d')}'
        """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado = cursor.fetchone()
        facturasMes = resultado[0] if resultado and resultado[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_412.setText(str(facturasMes))

        ###############################################################
        # COBROS DEL MES
        # Convertir fecha_actual y fecha_actual - 30 días al formato 'dd/mm/yyyy, hh:mm:ss'
        fecha_inicio = (fecha_actual - timedelta(days=30)).strftime('%d/%m/%Y, %H:%M:%S')
        fecha_fin = fecha_actual.strftime('%d/%m/%Y, %H:%M:%S')

        consulta_sql_total = f"""
        SELECT SUM(total) FROM caja
        WHERE TO_TIMESTAMP(fecha, 'DD/MM/YYYY, HH24:MI:SS') BETWEEN TO_TIMESTAMP('{fecha_inicio}', 'DD/MM/YYYY, HH24:MI:SS') AND TO_TIMESTAMP('{fecha_fin}', 'DD/MM/YYYY, HH24:MI:SS') AND tipo = 'COBRO'
        """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        cobrosMes = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_413.setText(str(cobrosMes))

        ###############################################################
        # TOTAL DEL MES
        totalMes = facturasMes
        self.label_417.setText(str(totalMes))

        ###############################################################
        # SALDOS PENDIENTES CUENTAS CORRIENTES
        consulta_sql_total = f"""
                        SELECT SUM(saldo) FROM pendientes
                        WHERE estado = 'PENDIENTE'
                        """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        saldoCtaCte = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_431.setText(str(saldoCtaCte))

        consulta_sql_total = f"""
                SELECT SUM(total) FROM caja
                WHERE tipo = 'COBRO'
                """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        cobrosTotal = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_432.setText(str(cobrosTotal))

        self.label_436.setText(str(saldoCtaCte))

        #######################################################################
        # RESUMEN DESPACHOS MERCADERIA
        consulta_sql = f"""
        SELECT COUNT(DISTINCT codfactura) FROM despacho
        WHERE fecha = '{fecha_formateada}'
        """

        # 4. Ejecutar la consulta SQL
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql)
            resultado = cursor.fetchone()

        # 5. Asignar el resultado de la consulta a la variable facturasDia
        despachosDia = resultado[0] if resultado else 0
        self.label_463.setText(str(despachosDia))

        #######################################################################
        # RESUMEN DESPACHOS MERCADERIA SEMANA
        fecha_inicio = (fecha_actual - timedelta(days=7)).strftime('%d/%m/%Y, %H:%M:%S')
        fecha_fin = fecha_actual.strftime('%d/%m/%Y, %H:%M:%S')

        consulta_sql_total = f"""
                        SELECT COUNT(DISTINCT codfactura) FROM despacho
                        WHERE TO_TIMESTAMP(fecha, 'DD/MM/YYYY, HH24:MI:SS') BETWEEN TO_TIMESTAMP('{fecha_inicio}', 'DD/MM/YYYY, HH24:MI:SS') AND TO_TIMESTAMP('{fecha_fin}', 'DD/MM/YYYY, HH24:MI:SS')
                        """

        # 4. Ejecutar la consulta SQL
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado = cursor.fetchone()

        # 5. Asignar el resultado de la consulta a la variable facturasDia
        despachosSemana = resultado[0] if resultado else 0
        self.label_464.setText(str(despachosSemana))

        #######################################################################
        # RESUMEN DESPACHOS PENDIENTES
        consulta_sql = f"""
                SELECT COUNT(*) FROM despacho
                WHERE estado = 'PENDIENTE'
                """

        # 4. Ejecutar la consulta SQL
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql)
            resultado = cursor.fetchone()

        # 5. Asignar el resultado de la consulta a la variable facturasDia
        despachosPendientes = resultado[0] if resultado else 0
        self.label_466.setText(str(despachosPendientes))

        #######################################################################
        # PAGOS DEL DIA
        # Crear una consulta SQL para sumar el total facturado del día
        consulta_sql_total = f"""
                SELECT SUM(total) FROM caja
                WHERE fecha = '{fecha_formateada}' AND tipo = 'PAGO'
                """

        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        pagoDia = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_442.setText(str(pagoDia))

        ###############################################################
        # PAGOS DE LA SEMANA
        # Convertir fecha_actual y fecha_actual - 30 días al formato 'dd/mm/yyyy, hh:mm:ss'
        fecha_inicio = (fecha_actual - timedelta(days=7)).strftime('%d/%m/%Y, %H:%M:%S')
        fecha_fin = fecha_actual.strftime('%d/%m/%Y, %H:%M:%S')

        consulta_sql_total = f"""
                        SELECT SUM(total) FROM caja
                        WHERE TO_TIMESTAMP(fecha, 'DD/MM/YYYY, HH24:MI:SS') BETWEEN TO_TIMESTAMP('{fecha_inicio}', 'DD/MM/YYYY, HH24:MI:SS') AND TO_TIMESTAMP('{fecha_fin}', 'DD/MM/YYYY, HH24:MI:SS') AND tipo = 'PAGO'
                        """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        pagoSemana = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_443.setText(str(pagoSemana))

        self.label_447.setText(str(pagoSemana))

        ###############################################################
        # PRESUPUESTOS DE LA SEMANA
        # Crear una consulta SQL para sumar el total facturado de la semana
        consulta_sql_total = f"""
                SELECT SUM(total) FROM presupuestos
                WHERE fecha BETWEEN '{fecha_actual - timedelta(days=fecha_actual.weekday())}' AND '{fecha_actual + timedelta(days=6 - fecha_actual.weekday())}'
                """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado_total = cursor.fetchone()
        presupuestosSemana = resultado_total[0] if resultado_total and resultado_total[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_453.setText(str(presupuestosSemana))

        ###############################################################
        # PRESUPUESTOS DEL MES
        # Crear una consulta SQL para sumar el total facturado del mes
        consulta_sql_total = f"""
                SELECT SUM(total) FROM presupuestos
                WHERE fecha BETWEEN '{(fecha_actual - timedelta(days=30)).strftime('%Y-%m-%d')}' AND '{fecha_actual.strftime('%Y-%m-%d')}'
                """
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql_total)
            resultado = cursor.fetchone()
        presupuestosMes = resultado[0] if resultado and resultado[0] is not None else 0
        # Aquí asumimos que tienes un QLabel para mostrar el total facturado del día
        self.label_454.setText(str(presupuestosMes))

        self.label_458.setText(str(presupuestosMes))

###############################################################
    ###############################################################
    ###############################################################

    def listar_articulos(self):
        articulos = ArticuloDAO.seleccionar()
        self.stackedWidget.setCurrentIndex(1)
        self.lineEdit_BuscarArticulo.setFocus()
        self.lineEdit_BuscarArticulo.setCursorPosition(0)
        self.tabla_Articulos.setRowCount(len(articulos))
        for i, articulo in enumerate(articulos):
            self.tabla_Articulos.setItem(i, 0, QtWidgets.QTableWidgetItem(str(articulo.codigo)))
            self.tabla_Articulos.setItem(i, 1, QtWidgets.QTableWidgetItem(articulo.nombre))
            self.tabla_Articulos.setItem(i, 2, QtWidgets.QTableWidgetItem(articulo._modelo))
            self.tabla_Articulos.setItem(i, 3, QtWidgets.QTableWidgetItem(articulo._marca))
            self.tabla_Articulos.setItem(i, 4, QtWidgets.QTableWidgetItem(articulo._categoria))
            self.tabla_Articulos.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
            self.tabla_Articulos.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
            self.tabla_Articulos.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
            self.tabla_Articulos.setItem(i, 8, QtWidgets.QTableWidgetItem(str(articulo._precio_costo)))
            self.tabla_Articulos.setItem(i, 9, QtWidgets.QTableWidgetItem(str(articulo._precio_venta)))
            self.tabla_Articulos.setItem(i, 10, QtWidgets.QTableWidgetItem(str(articulo._iva)))
            self.tabla_Articulos.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
            self.tabla_Articulos.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
            self.tabla_Articulos.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
            self.tabla_Articulos.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
            self.tabla_Articulos.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
            self.tabla_Articulos.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
            self.tabla_Articulos.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
            self.tabla_Articulos.setItem(i, 18, QtWidgets.QTableWidgetItem(str(articulo._stock)))
            self.tabla_Articulos.setItem(i, 19, QtWidgets.QTableWidgetItem(str(articulo._margen_ganancia)))
            self.tabla_Articulos.setItem(i, 20, QtWidgets.QTableWidgetItem(str(articulo._stock_minimo)))
            self.tabla_Articulos.setItem(i, 21, QtWidgets.QTableWidgetItem(str(articulo._cod_barras)))
            log.debug(articulo)

            #######################################################################################################
            # Convertir los artículos a un formato que se pueda serializar a JSON
            articulos_json = [articulo.__dict__ for articulo in articulos]

            # Guardar los artículos en un archivo JSON
            with open('articulos.json', 'w') as f:
                json.dump(articulos_json, f)

        ###########################################################################################

        ultimo_articulo = ArticuloDAO.ultimo_codigo_usado()
        cod = ultimo_articulo[0].codigo
        self.lineEdit_codigoNvoArticulo_2.setText(str(int(cod) + 10))
        # Setea el código del nuevo artículo en 10 unidades más que el último artículo ingresado
        # last_row = self.tabla_Articulos.rowCount() - 1
        # last_codigo = self.tabla_Articulos.item(last_row, 0)
        self.tabla_Articulos.resizeColumnsToContents()
        self.tabla_Articulos.resizeRowsToContents()
        # self.lineEdit_codigoNvoArticulo_2.setText(str(int(last_codigo.text()) + 10))
        self.lineEdit_codigoNvoArticulo_2.setDisabled(True)

        query_art_minimos = "SELECT * FROM articulos WHERE stock <= stock_minimo"
        with CursorDelPool() as cursor:
            cursor.execute(query_art_minimos)
            registros = cursor.fetchall()
            self.tableWidget_StockMinimo.setRowCount(len(registros))
            for i, registro in enumerate(registros):
                self.tableWidget_StockMinimo.setItem(i, 0, QtWidgets.QTableWidgetItem(str(registro[0])))
                self.tableWidget_StockMinimo.setItem(i, 1, QtWidgets.QTableWidgetItem(registro[1]))
                self.tableWidget_StockMinimo.setItem(i, 2, QtWidgets.QTableWidgetItem(str(registro[2])))
                self.tableWidget_StockMinimo.setItem(i, 3, QtWidgets.QTableWidgetItem(str(registro[4])))
                self.tableWidget_StockMinimo.setItem(i, 4, QtWidgets.QTableWidgetItem(str(registro[18])))
                self.tableWidget_StockMinimo.setItem(i, 5, QtWidgets.QTableWidgetItem(str(registro[20])))
                self.tableWidget_StockMinimo.resizeColumnsToContents()
                self.tableWidget_StockMinimo.resizeRowsToContents()

    def listar_clientes(self):
        clientes = ClienteDAO.seleccionar()
        self.stackedWidget.setCurrentIndex(2)
        self.tablaClientes.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            self.tablaClientes.setItem(i, 0, QtWidgets.QTableWidgetItem(str(cliente.codigo)))
            self.tablaClientes.setItem(i, 1, QtWidgets.QTableWidgetItem(cliente.nombre))
            self.tablaClientes.setItem(i, 2, QtWidgets.QTableWidgetItem(cliente.apellido))
            self.tablaClientes.setItem(i, 3, QtWidgets.QTableWidgetItem(cliente.dni))
            self.tablaClientes.setItem(i, 4, QtWidgets.QTableWidgetItem(cliente.empresa))
            self.tablaClientes.setItem(i, 5, QtWidgets.QTableWidgetItem(cliente.cuit))
            self.tablaClientes.setItem(i, 6, QtWidgets.QTableWidgetItem(cliente.telefono))
            self.tablaClientes.setItem(i, 7, QtWidgets.QTableWidgetItem(cliente.email))
            self.tablaClientes.setItem(i, 8, QtWidgets.QTableWidgetItem(cliente.direccion))
            self.tablaClientes.setItem(i, 9, QtWidgets.QTableWidgetItem(cliente.numero))
            self.tablaClientes.setItem(i, 10, QtWidgets.QTableWidgetItem(cliente.localidad))
            self.tablaClientes.setItem(i, 11, QtWidgets.QTableWidgetItem(cliente.provincia))
            self.tablaClientes.setItem(i, 12, QtWidgets.QTableWidgetItem(cliente.pais))
            self.tablaClientes.setItem(i, 13, QtWidgets.QTableWidgetItem(cliente.observaciones))
            self.tablaClientes.setItem(i, 14, QtWidgets.QTableWidgetItem(cliente.condiva))
            log.debug(cliente)

        clientes_json = [cliente.__dict__ for cliente in clientes]

        # Guardar los artículos en un archivo JSON
        with open('clientes.json', 'w') as f:
            json.dump(clientes_json, f)

        # Setea el código del nuevo artículo en 10 unidades más que el último artículo ingresado
        ultimo_cliente = ClienteDAO.ultimo_codigo_usado()
        cod = ultimo_cliente[0].codigo
        self.lineEdit_codigoNvoCliente.setText(str(int(cod) + 10))
        # last_row_cliente = self.tablaClientes.rowCount() - 1
        # last_codigo_cliente = self.tablaClientes.item(last_row_cliente, 0)
        self.tablaClientes.resizeColumnsToContents()
        self.tablaClientes.resizeRowsToContents()
        # self.lineEdit_codigoNvoCliente.setText(str(int(last_codigo_cliente.text()) + 10))
        self.lineEdit_codigoNvoCliente.setDisabled(True)

    def listar_proveedores(self):
        proveedores = ProveedorDAO.seleccionar()
        self.stackedWidget.setCurrentIndex(3)
        self.tablaProveedores.setRowCount(len(proveedores))
        for i, proveedor in enumerate(proveedores):
            self.tablaProveedores.setItem(i, 0, QtWidgets.QTableWidgetItem(str(proveedor.codproveedor)))
            self.tablaProveedores.setItem(i, 1, QtWidgets.QTableWidgetItem(proveedor.razonsocial))
            self.tablaProveedores.setItem(i, 2, QtWidgets.QTableWidgetItem(proveedor.cuit))
            self.tablaProveedores.setItem(i, 3, QtWidgets.QTableWidgetItem(proveedor.domicilio))
            self.tablaProveedores.setItem(i, 4, QtWidgets.QTableWidgetItem(proveedor.ciudad))
            self.tablaProveedores.setItem(i, 5, QtWidgets.QTableWidgetItem(proveedor.provincia))
            self.tablaProveedores.setItem(i, 6, QtWidgets.QTableWidgetItem(proveedor.pais))
            self.tablaProveedores.setItem(i, 7, QtWidgets.QTableWidgetItem(proveedor.telefono))
            self.tablaProveedores.setItem(i, 8, QtWidgets.QTableWidgetItem(proveedor.web))
            self.tablaProveedores.setItem(i, 9, QtWidgets.QTableWidgetItem(proveedor.email))
            self.tablaProveedores.setItem(i, 10, QtWidgets.QTableWidgetItem(proveedor.cuenta))
            self.tablaProveedores.setItem(i, 11, QtWidgets.QTableWidgetItem(proveedor.password))
            self.tablaProveedores.setItem(i, 12, QtWidgets.QTableWidgetItem(proveedor.observaciones))
            log.debug(proveedor)

        proveedores_json = [proveedor.__dict__ for proveedor in proveedores]

        # Guardar los artículos en un archivo JSON
        with open('proveedor.json', 'w') as f:
            json.dump(proveedores_json, f)

        # Setea el código del nuevo proveedor en 10 unidades más que el último proveedor ingresado
        ultimo_proveedor = ProveedorDAO.ultimo_codigo_usado()
        cod = ultimo_proveedor[0].codproveedor
        self.lineEdit_codigoNvoProveedor.setText(str(int(cod) + 10))
        # last_row_proveedor = self.tablaProveedores.rowCount() - 1
        # last_codigo_proveedor = self.tablaProveedores.item(last_row_proveedor, 0)
        self.tablaProveedores.resizeColumnsToContents()
        self.tablaProveedores.resizeRowsToContents()
        ########CAMBIAR EL LINEEDIT DE CODIGO DE PROVEEDOR
        # self.lineEdit_codigoNvoProveedor.setText(str(int(last_codigo_proveedor.text()) + 10))
        self.lineEdit_codigoNvoProveedor.setDisabled(True)

    ###########################################################################################################
    ###########################################################################################################
    #
    #                                   EMPIEZA LA PARTE DE LOS ARTICULOS
    #
    ###########################################################################################################
    ###########################################################################################################

    def mostrar_insertar_articulo(self):
        self.stackedWidget.setCurrentIndex(4)
        self.bt_guardarNvoArticulo.clicked.connect(self.insertar_articulo)

    def insertar_articulo(self):
        codigo = self.lineEdit_codigoNvoArticulo_2.text()
        nombre = self.lineEdit_nombreNvoArticulo.text()
        modelo = self.lineEdit_modeloNvoArticulo.text()
        marca = self.lineEdit_marcaNvoArticulo.text()
        categoria = self.lineEdit_categoriaNvoArticulo.text()
        sku = self.lineEdit_skuNvoArticulo.text()
        color = self.lineEdit_colorNvoArticulo.text()
        caracteristica = self.lineEdit_caracteristicaNvoArticulo.text()
        precio_costo = float(self.lineEdit_preciocostoNvoArticulo.text())
        precio_venta = float(self.lineEdit_precioventaNvoArticulo.text())
        iva = float(self.lineEdit_ivaNvoArticulo.text())
        proveedor = self.lineEdit_proveedorNvoArticulo.text()
        tamaño = self.lineEdit_tamanoNvoArticulo.text()
        ancho = self.lineEdit_anchoNvoArticulo.text()
        largo = self.lineEdit_largoNvoArticulo.text()
        profundidad = self.lineEdit_profundidadNvoArticulo.text()
        peso = self.lineEdit_pesoNvoArticulo.text()
        peso_envalado = self.lineEdit_pesoenvaladoNvoArticulo.text()
        stock = self.lineEdit_stockNvoArticulo.text()
        margen_ganancia = self.lineEdit_margenNvoArticulo.text()
        stock_minimo = self.lineEdit_stockMinimoNvoArticulo.text()
        cod_barras = self.lineEdit_codBarrasNvoArticulo.text()
        articulo = Articulo(codigo, nombre, modelo, marca, categoria, sku, color, caracteristica, precio_costo,
                            precio_venta, iva, proveedor, tamaño, ancho, largo, profundidad, peso, peso_envalado, stock,
                            margen_ganancia, stock_minimo, cod_barras)
        articulos_insertados = ArticuloDAO.insertar(articulo)
        log.debug(f'Articulos insertados: {articulos_insertados}')
        # self.label_ingresar_msg2.setText('Articulo ingresado correctamente')
        QMessageBox.information(self, "Artículo Ingresado",
                                "El artículo ha sido ingresado correctamente", )
        self.listar_articulos()
        ##### BORRA LOS LINEEDIT DESPUES DE INGRESAR EL ARTICULO
        self.borrar_campos_nuevo_articulo()
        ##############
        linea10 = '-'
        linea11 = '0'
        self.lineEdit_nombreNvoArticulo.setText(linea10)
        self.lineEdit_modeloNvoArticulo.setText(linea10)
        self.lineEdit_marcaNvoArticulo.setText(linea10)
        self.lineEdit_categoriaNvoArticulo.setText(linea10)
        self.lineEdit_skuNvoArticulo.setText(linea10)
        self.lineEdit_colorNvoArticulo.setText(linea10)
        self.lineEdit_caracteristicaNvoArticulo.setText(linea10)
        self.lineEdit_preciocostoNvoArticulo.setText(linea11)
        self.lineEdit_precioventaNvoArticulo.setText(linea11)
        self.lineEdit_ivaNvoArticulo.setText(linea11)
        self.lineEdit_proveedorNvoArticulo.setText(linea11)
        self.lineEdit_tamanoNvoArticulo.setText(linea11)
        self.lineEdit_anchoNvoArticulo.setText(linea11)
        self.lineEdit_largoNvoArticulo.setText(linea11)
        self.lineEdit_profundidadNvoArticulo.setText(linea11)
        self.lineEdit_pesoNvoArticulo.setText(linea11)
        self.lineEdit_pesoenvaladoNvoArticulo.setText(linea11)
        self.lineEdit_stockNvoArticulo.setText(linea11)
        self.lineEdit_margenNvoArticulo.setText(linea11)
        self.lineEdit_stockMinimoNvoArticulo.setText(linea11)
        self.lineEdit_codBarrasNvoArticulo.setText('')
        self.label_ingresar_msg2.clear()
        return

    def borrar_campos_nuevo_articulo(self):
        self.lineEdit_nombreNvoArticulo.clear()
        self.lineEdit_modeloNvoArticulo.clear()
        self.lineEdit_marcaNvoArticulo.clear()
        self.lineEdit_categoriaNvoArticulo.clear()
        self.lineEdit_skuNvoArticulo.clear()
        self.lineEdit_colorNvoArticulo.clear()
        self.lineEdit_caracteristicaNvoArticulo.clear()
        self.lineEdit_preciocostoNvoArticulo.clear()
        self.lineEdit_precioventaNvoArticulo.clear()
        self.lineEdit_ivaNvoArticulo.clear()
        self.lineEdit_proveedorNvoArticulo.clear()
        self.lineEdit_tamanoNvoArticulo.clear()
        self.lineEdit_anchoNvoArticulo.clear()
        self.lineEdit_largoNvoArticulo.clear()
        self.lineEdit_profundidadNvoArticulo.clear()
        self.lineEdit_pesoNvoArticulo.clear()
        self.lineEdit_pesoenvaladoNvoArticulo.clear()
        self.lineEdit_stockNvoArticulo.clear()
        self.lineEdit_margenNvoArticulo.clear()
        self.lineEdit_stockMinimoNvoArticulo.clear()
        self.lineEdit_codBarrasNvoArticulo.clear()
        self.label_ingresar_msg2.clear()

    ###########################################################################################################
    #
    #                                 Empieza FACTURAS

    ###########################################################################################################

    def limpiar_busquedas(self):
        self.lineEdit_BuscarArticulo.clear()
        self.lineEdit_BuscarArticulo.setFocus()
        self.lineEdit_BuscarArticulo.setCursorPosition(0)

    def limpiar_busquedas_lector(self):
        self.lineEdit_BuscarArticuloNvaFactura1.clear()
        self.lineEdit_BuscarArticuloNvaFactura1.setFocus()
        self.lineEdit_BuscarArticuloNvaFactura1.setCursorPosition(0)

    def buscar_articulo_nueva_factura_lector(self):
        campo1 = 'cod_barras'
        valor = str(self.lineEdit_BuscarArticuloNvaFactura1.text())
        articulos = ArticuloDAO.buscar_articulo_lector(campo1, valor)
        # self.lineEdit_BuscarArticuloNvaFactura1.returnPressed.connect(self.limpiar_busquedas_lector)
        self.lineEdit_BuscarArticuloNvaFactura1.clear()
        self.lineEdit_BuscarArticuloNvaFactura1.setFocus()
        self.lineEdit_BuscarArticuloNvaFactura1.setCursorPosition(0)
        ########################################################################################################
        # nueva_lista = []
        # for i in articulos:
        #     precio_costo_str = i.precio_costo.replace('$', '').replace(',', '')
        #     importe_iva = (float(precio_costo_str) * float(i.iva)) / 100
        #     precio_unitario = float(precio_costo_str) + importe_iva
        #     nueva_lista.append(
        #         [i.codigo, i.nombre, "1", i.precio_costo, i.iva, importe_iva, precio_unitario, precio_unitario])
        #
        # Funciones.fx_cargarTablaX(nueva_lista, self.tableWidgetDetalleNvaFactura, limpiaTabla=False)
        # self.tableWidgetDetalleNvaFactura.resizeColumnsToContents()
        # self.tableWidgetDetalleNvaFactura.resizeRowsToContents()
        # self.verificarExistencias()
        # self.actualizar_subtotal_factura()
        #######################################################################################################
        # Obtén el código del artículo seleccionado
        codigo_articulo_seleccionado = articulos[0].codigo

        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura.rowCount()

        # Variable para verificar si el artículo ya está en la tabla
        articulo_ya_en_tabla = False

        # Itera sobre cada fila
        for row in range(num_rows):
            # Obtén el código del artículo en la fila actual (asumiendo que es la columna 0)
            codigo_articulo_en_tabla = self.tableWidgetDetalleNvaFactura.item(row, 0).text()

            # Si el código del artículo seleccionado coincide con el código del artículo en la fila actual
            if int(codigo_articulo_seleccionado) == int(codigo_articulo_en_tabla):
                # Incrementa la cantidad del artículo en la fila actual (asumiendo que la cantidad es la columna 2)
                cantidad_actual = int(self.tableWidgetDetalleNvaFactura.item(row, 2).text())
                self.tableWidgetDetalleNvaFactura.setItem(row, 2, QtWidgets.QTableWidgetItem(str(cantidad_actual + 1)))

                # Marca que el artículo ya está en la tabla
                articulo_ya_en_tabla = True
                break

        # Si el artículo no está en la tabla, agrega una nueva fila
        if not articulo_ya_en_tabla:
            nueva_lista = []
            for i in articulos:
                precio_costo_str = i.precio_costo.replace('$', '').replace(',', '')
                importe_iva = (float(precio_costo_str) * float(i.iva)) / 100
                precio_unitario = float(precio_costo_str) + importe_iva
                nueva_lista.append(
                    [i.codigo, i.nombre, "1", i.precio_costo, i.iva, importe_iva, precio_unitario, precio_unitario])
            Funciones.fx_cargarTablaX(nueva_lista, self.tableWidgetDetalleNvaFactura, limpiaTabla=False)
            self.tableWidgetDetalleNvaFactura.resizeColumnsToContents()
            self.tableWidgetDetalleNvaFactura.resizeRowsToContents()
            self.verificarExistencias()
            self.actualizar_subtotal_factura()

    def buscar_articulo(self):
        campo1 = 'nombre'
        campo2 = 'codigo'
        campo3 = 'cod_barras'
        valor = str(self.lineEdit_BuscarArticulo.text())
        articulos = ArticuloDAO.buscar_articulo_nombre(campo1, campo2, campo3, valor)
        ##########################################ELIMINE LA LINEA QUE LIMPIA EL CAMPO DE BUSQUEDA AL DAR ENTER C/LECTOR
        # self.lineEdit_BuscarArticulo.returnPressed.connect(self.limpiar_busquedas)
        #################################################################################
        self.tabla_Articulos.setRowCount(len(articulos))
        for i, articulo in enumerate(articulos):
            self.tabla_Articulos.setItem(i, 0, QtWidgets.QTableWidgetItem(str(articulo.codigo)))
            self.tabla_Articulos.setItem(i, 1, QtWidgets.QTableWidgetItem(articulo.nombre))
            self.tabla_Articulos.setItem(i, 2, QtWidgets.QTableWidgetItem(articulo._modelo))
            self.tabla_Articulos.setItem(i, 3, QtWidgets.QTableWidgetItem(articulo._marca))
            self.tabla_Articulos.setItem(i, 4, QtWidgets.QTableWidgetItem(articulo._categoria))
            self.tabla_Articulos.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
            self.tabla_Articulos.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
            self.tabla_Articulos.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
            self.tabla_Articulos.setItem(i, 8, QtWidgets.QTableWidgetItem(str(articulo._precio_costo)))
            self.tabla_Articulos.setItem(i, 9, QtWidgets.QTableWidgetItem(str(articulo._precio_venta)))
            self.tabla_Articulos.setItem(i, 10, QtWidgets.QTableWidgetItem(str(articulo._iva)))
            self.tabla_Articulos.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
            self.tabla_Articulos.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
            self.tabla_Articulos.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
            self.tabla_Articulos.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
            self.tabla_Articulos.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
            self.tabla_Articulos.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
            self.tabla_Articulos.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
            self.tabla_Articulos.setItem(i, 18, QtWidgets.QTableWidgetItem(str(articulo._stock)))
            self.tabla_Articulos.setItem(i, 19, QtWidgets.QTableWidgetItem(str(articulo._margen_ganancia)))
            self.tabla_Articulos.setItem(i, 20, QtWidgets.QTableWidgetItem(str(articulo._stock_minimo)))
            self.tabla_Articulos.setItem(i, 21, QtWidgets.QTableWidgetItem(str(articulo._cod_barras)))
            self.tabla_Articulos.resizeColumnsToContents()
            self.tabla_Articulos.resizeRowsToContents()
            log.debug(articulo)

    def on_selec_change(self):
        row = self.tabla_Articulos.currentRow()
        item = self.tabla_Articulos.item(row, 0)
        if item is not None:
            self.label_capturaSeleccion.setText(item.text())
            print(f'Fila seleccionada: {item.text()}')

    def modificar_articulo(self):
        # valor_codigo = self.label_capturaSeleccion.text()
        # codigo = self.tabla_Articulos.item(int(valor_codigo), 0).text()
        # row = int(valor_codigo)
        row = self.tabla_Articulos.currentRow()
        codigo = int(self.tabla_Articulos.item(row, 0).text())
        nombre = str(self.tabla_Articulos.item(row, 1).text())
        modelo = str(self.tabla_Articulos.item(row, 2).text())
        marca = str(self.tabla_Articulos.item(row, 3).text())
        categoria = str(self.tabla_Articulos.item(row, 4).text())
        sku = str(self.tabla_Articulos.item(row, 5).text())
        color = str(self.tabla_Articulos.item(row, 6).text())
        caracteristica = str(self.tabla_Articulos.item(row, 7).text())
        precio_costo_str = self.tabla_Articulos.item(row, 8).text()
        precio_costo_str = precio_costo_str.replace('$', '').replace(',', '')
        precio_costo = float(precio_costo_str)
        # precio_costo = float(self.tabla_Articulos.item(row, 8).text())
        precio_venta_str = self.tabla_Articulos.item(row, 9).text()
        precio_venta_str = precio_venta_str.replace('$', '').replace(',', '')
        precio_venta = float(precio_venta_str)
        # precio_venta = float(self.tabla_Articulos.item(row, 9).text())
        # iva_str = self.tabla_Articulos.item(row, 10).text
        # iva = float(iva_str) if iva_str != 'None' else 0.0
        iva = float(self.tabla_Articulos.item(row, 10).text())
        proveedor = str(self.tabla_Articulos.item(row, 11).text())
        tamaño = float(self.tabla_Articulos.item(row, 12).text())
        ancho = float(self.tabla_Articulos.item(row, 13).text())
        largo = float(self.tabla_Articulos.item(row, 14).text())
        profundidad = float(self.tabla_Articulos.item(row, 15).text())
        peso = float(self.tabla_Articulos.item(row, 16).text())
        peso_envalado = float(self.tabla_Articulos.item(row, 17).text())
        stock = int(self.tabla_Articulos.item(row, 18).text())
        margen_ganancia = float(self.tabla_Articulos.item(row, 19).text())
        stock_minimo = int(self.tabla_Articulos.item(row, 20).text())
        cod_barras = str(self.tabla_Articulos.item(row, 21).text())
        button = QMessageBox.question(self, "Modificar Artículo", "Está seguro que desea modificar el artículo?", )

        if button == QMessageBox.Yes:
            print("SI!")
            articulo = Articulo(codigo, nombre, modelo, marca, categoria, sku, color, caracteristica, precio_costo,
                                precio_venta, iva, proveedor, tamaño, ancho, largo, profundidad, peso, peso_envalado,
                                stock, margen_ganancia, stock_minimo, cod_barras)
            articulos_actualizados = ArticuloDAO.actualizar(articulo)
            log.debug(f'Articulos actualizados: {articulos_actualizados}')
            self.label_ingresar_msg2.setText('Articulo actualizado correctamente')
            QMessageBox.information(self, "Artículo Modificado",
                                    "El artículo ha sido modificado correctamente", )
        else:
            print("NO!")
            self.listar_articulos()
            return

    def filtrar_articulo(self):

        campo = self.comboBox_FiltrarArticuloCampo.currentText()
        condicion = self.comboBox_FiltrarArticuloCondicion.currentText()
        valor1 = self.lineEditValor1.text()
        valor2 = None

        if condicion == 'Igual a...':
            articulos = ArticuloDAO.filtrar_articulo_igual(campo, valor1)
            self.tabla_Articulos.setRowCount(len(articulos))
            for i, articulo in enumerate(articulos):
                self.tabla_Articulos.setItem(i, 0, QtWidgets.QTableWidgetItem(str(articulo.codigo)))
                self.tabla_Articulos.setItem(i, 1, QtWidgets.QTableWidgetItem(articulo.nombre))
                self.tabla_Articulos.setItem(i, 2, QtWidgets.QTableWidgetItem(articulo._modelo))
                self.tabla_Articulos.setItem(i, 3, QtWidgets.QTableWidgetItem(articulo._marca))
                self.tabla_Articulos.setItem(i, 4, QtWidgets.QTableWidgetItem(articulo._categoria))
                self.tabla_Articulos.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
                self.tabla_Articulos.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
                self.tabla_Articulos.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
                self.tabla_Articulos.setItem(i, 8, QtWidgets.QTableWidgetItem(str(articulo._precio_costo)))
                self.tabla_Articulos.setItem(i, 9, QtWidgets.QTableWidgetItem(str(articulo._precio_venta)))
                self.tabla_Articulos.setItem(i, 10, QtWidgets.QTableWidgetItem(str(articulo._iva)))
                self.tabla_Articulos.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
                self.tabla_Articulos.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
                self.tabla_Articulos.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
                self.tabla_Articulos.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
                self.tabla_Articulos.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
                self.tabla_Articulos.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
                self.tabla_Articulos.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
                self.tabla_Articulos.setItem(i, 18, QtWidgets.QTableWidgetItem(str(articulo._stock)))
                self.tabla_Articulos.setItem(i, 19, QtWidgets.QTableWidgetItem(str(articulo._margen_ganancia)))
                self.tabla_Articulos.setItem(i, 20, QtWidgets.QTableWidgetItem(str(articulo._stock_minimo)))
                self.tabla_Articulos.setItem(i, 21, QtWidgets.QTableWidgetItem(str(articulo._cod_barras)))
                log.debug(articulo)
                self.tabla_Articulos.resizeColumnsToContents()
                self.tabla_Articulos.resizeRowsToContents()
                if self.comboBox_FiltrarArticuloCondicion.changeEvent:
                    self.lineEditValor1.setText('')
                    self.lineEditValor1_2.setText('')

        elif condicion == 'Mayor que...':
            articulos = ArticuloDAO.filtrar_articulo_mayor(campo, valor1)
            self.tabla_Articulos.setRowCount(len(articulos))
            for i, articulo in enumerate(articulos):
                self.tabla_Articulos.setItem(i, 0, QtWidgets.QTableWidgetItem(str(articulo.codigo)))
                self.tabla_Articulos.setItem(i, 1, QtWidgets.QTableWidgetItem(articulo.nombre))
                self.tabla_Articulos.setItem(i, 2, QtWidgets.QTableWidgetItem(articulo._modelo))
                self.tabla_Articulos.setItem(i, 3, QtWidgets.QTableWidgetItem(articulo._marca))
                self.tabla_Articulos.setItem(i, 4, QtWidgets.QTableWidgetItem(articulo._categoria))
                self.tabla_Articulos.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
                self.tabla_Articulos.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
                self.tabla_Articulos.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
                self.tabla_Articulos.setItem(i, 8, QtWidgets.QTableWidgetItem(str(articulo._precio_costo)))
                self.tabla_Articulos.setItem(i, 9, QtWidgets.QTableWidgetItem(str(articulo._precio_venta)))
                self.tabla_Articulos.setItem(i, 10, QtWidgets.QTableWidgetItem(str(articulo._iva)))
                self.tabla_Articulos.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
                self.tabla_Articulos.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
                self.tabla_Articulos.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
                self.tabla_Articulos.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
                self.tabla_Articulos.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
                self.tabla_Articulos.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
                self.tabla_Articulos.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
                self.tabla_Articulos.setItem(i, 18, QtWidgets.QTableWidgetItem(str(articulo._stock)))
                self.tabla_Articulos.setItem(i, 19, QtWidgets.QTableWidgetItem(str(articulo._margen_ganancia)))
                self.tabla_Articulos.setItem(i, 20, QtWidgets.QTableWidgetItem(str(articulo._stock_minimo)))
                self.tabla_Articulos.setItem(i, 21, QtWidgets.QTableWidgetItem(str(articulo._cod_barras)))
                log.debug(articulo)
                self.tabla_Articulos.resizeColumnsToContents()
                self.tabla_Articulos.resizeRowsToContents()
                if self.comboBox_FiltrarArticuloCondicion.changeEvent:
                    self.lineEditValor1.setText('')
                    self.lineEditValor1_2.setText('')

        elif condicion == 'Menor que...':
            articulos = ArticuloDAO.filtrar_articulo_menor(campo, valor1)
            self.tabla_Articulos.setRowCount(len(articulos))
            for i, articulo in enumerate(articulos):
                self.tabla_Articulos.setItem(i, 0, QtWidgets.QTableWidgetItem(str(articulo.codigo)))
                self.tabla_Articulos.setItem(i, 1, QtWidgets.QTableWidgetItem(articulo.nombre))
                self.tabla_Articulos.setItem(i, 2, QtWidgets.QTableWidgetItem(articulo._modelo))
                self.tabla_Articulos.setItem(i, 3, QtWidgets.QTableWidgetItem(articulo._marca))
                self.tabla_Articulos.setItem(i, 4, QtWidgets.QTableWidgetItem(articulo._categoria))
                self.tabla_Articulos.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
                self.tabla_Articulos.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
                self.tabla_Articulos.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
                self.tabla_Articulos.setItem(i, 8, QtWidgets.QTableWidgetItem(str(articulo._precio_costo)))
                self.tabla_Articulos.setItem(i, 9, QtWidgets.QTableWidgetItem(str(articulo._precio_venta)))
                self.tabla_Articulos.setItem(i, 10, QtWidgets.QTableWidgetItem(str(articulo._iva)))
                self.tabla_Articulos.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
                self.tabla_Articulos.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
                self.tabla_Articulos.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
                self.tabla_Articulos.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
                self.tabla_Articulos.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
                self.tabla_Articulos.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
                self.tabla_Articulos.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
                self.tabla_Articulos.setItem(i, 18, QtWidgets.QTableWidgetItem(str(articulo._stock)))
                self.tabla_Articulos.setItem(i, 19, QtWidgets.QTableWidgetItem(str(articulo._margen_ganancia)))
                self.tabla_Articulos.setItem(i, 20, QtWidgets.QTableWidgetItem(str(articulo._stock_minimo)))
                self.tabla_Articulos.setItem(i, 21, QtWidgets.QTableWidgetItem(str(articulo._cod_barras)))
                log.debug(articulo)
                self.tabla_Articulos.resizeColumnsToContents()
                self.tabla_Articulos.resizeRowsToContents()
                if self.comboBox_FiltrarArticuloCondicion.changeEvent:
                    self.lineEditValor1.setText('')
                    self.lineEditValor1_2.setText('')

        elif condicion == 'Entre...':
            if self.lineEditValor1_2.text() == 'Valor 2' or self.lineEditValor1.text() == 'Valor 1':
                QMessageBox.information(self, "Información faltante",
                                        "Por favor, ingrese ambos valores para la condición 'Entre...'")
                return
            valor2 = self.lineEditValor1_2.text()
            if not valor1 or not valor2:
                QMessageBox.information(self, "Información faltante",
                                        "Por favor, ingrese ambos valores para la condición 'Entre...'")
                return
            articulos = ArticuloDAO.filtrar_articulo_entre(campo, valor1, valor2)
            self.tabla_Articulos.setRowCount(len(articulos))
            for i, articulo in enumerate(articulos):
                self.tabla_Articulos.setItem(i, 0, QtWidgets.QTableWidgetItem(str(articulo.codigo)))
                self.tabla_Articulos.setItem(i, 1, QtWidgets.QTableWidgetItem(articulo.nombre))
                self.tabla_Articulos.setItem(i, 2, QtWidgets.QTableWidgetItem(articulo._modelo))
                self.tabla_Articulos.setItem(i, 3, QtWidgets.QTableWidgetItem(articulo._marca))
                self.tabla_Articulos.setItem(i, 4, QtWidgets.QTableWidgetItem(articulo._categoria))
                self.tabla_Articulos.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
                self.tabla_Articulos.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
                self.tabla_Articulos.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
                self.tabla_Articulos.setItem(i, 8, QtWidgets.QTableWidgetItem(str(articulo._precio_costo)))
                self.tabla_Articulos.setItem(i, 9, QtWidgets.QTableWidgetItem(str(articulo._precio_venta)))
                self.tabla_Articulos.setItem(i, 10, QtWidgets.QTableWidgetItem(str(articulo._iva)))
                self.tabla_Articulos.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
                self.tabla_Articulos.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
                self.tabla_Articulos.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
                self.tabla_Articulos.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
                self.tabla_Articulos.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
                self.tabla_Articulos.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
                self.tabla_Articulos.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
                self.tabla_Articulos.setItem(i, 18, QtWidgets.QTableWidgetItem(str(articulo._stock)))
                self.tabla_Articulos.setItem(i, 19, QtWidgets.QTableWidgetItem(str(articulo._margen_ganancia)))
                self.tabla_Articulos.setItem(i, 20, QtWidgets.QTableWidgetItem(str(articulo._stock_minimo)))
                self.tabla_Articulos.setItem(i, 21, QtWidgets.QTableWidgetItem(str(articulo._cod_barras)))
                log.debug(articulo)
                self.tabla_Articulos.resizeColumnsToContents()
                self.tabla_Articulos.resizeRowsToContents()
                if self.comboBox_FiltrarArticuloCondicion.changeEvent:
                    self.lineEditValor1.setText('')
                    self.lineEditValor1_2.setText('')

    def eliminar_articulo(self):
        row = self.tabla_Articulos.currentRow()
        item = self.tabla_Articulos.item(row, 0)
        if item is not None:
            self.label_capturaSeleccion.setText(item.text())
            print(f'Fila seleccionada: {item.text()}')
        codigo = self.tabla_Articulos.item(row, 0).text()
        nombre = self.tabla_Articulos.item(row, 1).text()
        modelo = self.tabla_Articulos.item(row, 2).text()
        marca = self.tabla_Articulos.item(row, 3).text()
        categoria = self.tabla_Articulos.item(row, 4).text()
        sku = self.tabla_Articulos.item(row, 5).text()
        color = self.tabla_Articulos.item(row, 6).text()
        caracteristica = self.tabla_Articulos.item(row, 7).text()
        precio_costo = self.tabla_Articulos.item(row, 8).text()
        precio_venta = self.tabla_Articulos.item(row, 9).text()
        iva = self.tabla_Articulos.item(row, 10).text()
        proveedor = self.tabla_Articulos.item(row, 11).text()
        tamaño = self.tabla_Articulos.item(row, 12).text()
        ancho = self.tabla_Articulos.item(row, 13).text()
        largo = self.tabla_Articulos.item(row, 14).text()
        profundidad = self.tabla_Articulos.item(row, 15).text()
        peso = self.tabla_Articulos.item(row, 16).text()
        peso_envalado = self.tabla_Articulos.item(row, 17).text()
        stock = self.tabla_Articulos.item(row, 18).text()
        margen_ganancia = self.tabla_Articulos.item(row, 19).text()
        stock_minimo = self.tabla_Articulos.item(row, 20).text()
        cod_barras = self.tabla_Articulos.item(row, 21).text()
        button = QMessageBox.question(self, "Eliminar Artículo", "Está seguro que desea eliminar el artículo?", )

        if button == QMessageBox.Yes:
            print("SI!")
            articulo = Articulo(codigo, nombre, modelo, marca, categoria, sku, color, caracteristica, precio_costo,
                                precio_venta, iva, proveedor, tamaño, ancho, largo, profundidad, peso, peso_envalado,
                                stock, margen_ganancia, stock_minimo, cod_barras)
            articulos_eliminados = ArticuloDAO.eliminar(articulo)
            log.debug(f'Articulos eliminados: {articulos_eliminados}')
            # self.label_ingresar_msg2.setText('Articulo eliminado correctamente')
            QMessageBox.information(self, "Artículo Eliminado",
                                    "El artículo ha sido eliminado correctamente", )
        else:
            print("NO!")
        self.listar_articulos()
        return

    ###########################################################################################################
    ###########################################################################################################
    #
    #                                   EMPIEZA LA PARTE DEL CLIENTE
    #
    ###########################################################################################################
    ###########################################################################################################

    def on_selec_change_cliente(self):
        row = self.tablaClientes.currentRow()
        item = self.tablaClientes.item(row, 0)
        if item is not None:
            self.label_capturaSeleccion.setText(item.text())
            print(f'Fila seleccionada: {item.text()}')

    def modificar_cliente(self):
        row = self.tablaClientes.currentRow()
        codigo = int(self.tablaClientes.item(row, 0).text())
        nombre = str(self.tablaClientes.item(row, 1).text())
        apellido = str(self.tablaClientes.item(row, 2).text())
        dni = str(self.tablaClientes.item(row, 3).text())
        empresa = str(self.tablaClientes.item(row, 4).text())
        cuit = str(self.tablaClientes.item(row, 5).text())
        telefono = str(self.tablaClientes.item(row, 6).text())
        email = str(self.tablaClientes.item(row, 7).text())
        direccion = str(self.tablaClientes.item(row, 8).text())
        numero = str(self.tablaClientes.item(row, 9).text())
        localidad = str(self.tablaClientes.item(row, 10).text())
        provincia = str(self.tablaClientes.item(row, 11).text())
        pais = str(self.tablaClientes.item(row, 12).text())
        # observaciones = str(self.tablaClientes.item(row, 13).text())
        item = self.tablaClientes.item(row, 13)
        condiva = self.tablaClientes.item(row, 14).text()
        if item is not None:
            observaciones = str(item.text())
        else:
            observaciones = None

        button = QMessageBox.question(self, "Modificar Cliente", "Está seguro que desea modificar el cliente?", )

        if nombre == '' or nombre.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Nombre no puede estar vacío o no ser sólo letras", )
            self.tablaClientes.item(row, 1).setText('')
            self.tablaClientes.setCurrentCell(row, 1)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 1))
            return

        if apellido == '' or apellido.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Apellido no puede estar vacío o no ser sólo letras", )
            self.tablaClientes.item(row, 2).setText('')
            self.tablaClientes.setCurrentCell(row, 2)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 2))
            return

        try:
            int_dni = int(dni)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de DNI no puede estar vacío o no ser números enteros", )
            self.tablaClientes.item(row, 3).setText('')
            self.tablaClientes.setCurrentCell(row, 5)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 3))
            return

        try:
            int_cuit = int(cuit)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de CUIT/CUIL no puede estar vacío o no ser números enteros", )
            self.tablaClientes.item(row, 5).setText('')
            self.tablaClientes.setCurrentCell(row, 5)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 5))
            return

        try:
            int_telefono = int(telefono)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor del Teléfono debe ser sólo números enteros", )
            self.tablaClientes.item(row, 6).setText('')
            self.tablaClientes.setCurrentCell(row, 6)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 6))
            return

        if localidad == '' or localidad.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Localidad no puede estar vacío o no ser sólo letras", )
            self.tablaClientes.item(row, 10).setText('')
            self.tablaClientes.setCurrentCell(row, 10)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 10))
            return

        if provincia == '' or provincia.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Provincia no puede estar vacío o no ser sólo letras", )
            self.tablaClientes.item(row, 11).setText('')
            self.tablaClientes.setCurrentCell(row, 11)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 11))
            return

        if pais == '' or pais.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de País no puede estar vacío o no ser sólo letras", )
            self.tablaClientes.item(row, 12).setText('')
            self.tablaClientes.setCurrentCell(row, 12)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 12))
            return

        if condiva == '' or condiva.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Condición IVA no puede estar vacío o no ser Responsable Inscripto, Monotributista, Consumidor Final o Exento", )
            self.tablaClientes.item(row, 14).setText('')
            self.tablaClientes.setCurrentCell(row, 14)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 14))
            return
        elif condiva != 'RESPONSABLE INSCRIPTO' and condiva != 'MONOTRIBUTISTA' and condiva != 'CONSUMIDOR FINAL' and condiva != 'EXENTO':
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Condición IVA no puede estar vacío o no ser Responsable Inscripto, Monotributista, Consumidor Final o Exento", )
            self.tablaClientes.item(row, 14).setText('')
            self.tablaClientes.setCurrentCell(row, 14)
            self.tablaClientes.editItem(self.tablaClientes.item(row, 14))
            return

        if button == QMessageBox.Yes:
            print("SI!")
            cliente = Cliente(codigo, nombre, apellido, dni, empresa, cuit, telefono, email, direccion, numero,
                              localidad, provincia, pais, observaciones, condiva)
            clientes_actualizados = ClienteDAO.actualizar(cliente)
            log.debug(f'Clientes actualizados: {clientes_actualizados}')
            self.label_ingresar_msg2.setText('Cliente actualizado correctamente')
            QMessageBox.information(self, "Cliente Modificado",
                                    "El cliente ha sido modificado correctamente", )
        else:
            print("NO!")
            self.listar_clientes()
            return

    def eliminar_cliente(self):
        row = self.tablaClientes.currentRow()
        item = self.tablaClientes.item(row, 0)
        if item is not None:
            self.label_capturaSeleccion.setText(item.text())
            print(f'Fila seleccionada: {item.text()}')
        codigo = self.tablaClientes.item(row, 0).text()
        nombre = self.tablaClientes.item(row, 1).text()
        apellido = self.tablaClientes.item(row, 2).text()
        dni = self.tablaClientes.item(row, 3).text()
        empresa = self.tablaClientes.item(row, 4).text()
        cuit = self.tablaClientes.item(row, 5).text()
        telefono = self.tablaClientes.item(row, 6).text()
        email = self.tablaClientes.item(row, 7).text()
        direccion = self.tablaClientes.item(row, 8).text()
        numero = self.tablaClientes.item(row, 9).text()
        localidad = self.tablaClientes.item(row, 10).text()
        provincia = self.tablaClientes.item(row, 11).text()
        pais = self.tablaClientes.item(row, 12).text()
        # observaciones = self.tablaClientes.item(row, 13).text()
        item = self.tablaClientes.item(row, 13)
        condiva = self.tablaClientes.item(row, 14).text()
        if item is not None:
            observaciones = str(item.text())
        else:
            observaciones = None

        button = QMessageBox.question(self, "Eliminar Cliente", "Está seguro que desea eliminar el cliente?", )

        if button == QMessageBox.Yes:
            print("SI!")
            cliente = Cliente(codigo, nombre, apellido, dni, empresa, cuit, telefono, email, direccion, numero,
                              localidad, provincia, pais, observaciones, condiva)
            clientes_eliminados = ClienteDAO.eliminar(cliente)
            log.debug(f'Clientes eliminados: {clientes_eliminados}')
            # self.label_ingresar_msg2.setText('Cliente eliminado correctamente')
            QMessageBox.information(self, "Cliente Eliminado",
                                    "El cliente ha sido eliminado correctamente", )
        else:
            print("NO!")
        self.listar_clientes()
        return

    def mostrar_insertar_cliente(self):
        self.stackedWidget.setCurrentIndex(5)
        self.bt_guardarNvoCliente.clicked.connect(self.insertar_cliente)

    def insertar_cliente(self):
        codigo = self.lineEdit_codigoNvoCliente.text()
        nombre = self.lineEdit_nombreNvoCliente.text()
        apellido = self.lineEdit_apellidoNvoCliente.text()
        dni = self.lineEdit_lineEdit_dniNvoCliente.text()
        empresa = self.lineEdit_empresaNvoCliente.text()
        cuit = self.lineEdit_cuitNvoCliente.text()
        telefono = self.lineEdit_telefonoNvoCliente.text()
        email = self.lineEdit_emailNvoCliente.text()
        direccion = self.lineEdit_direccionNvoCliente.text()
        numero = self.lineEdit_numerolNvoCliente.text()
        localidad = self.lineEdit_localidadNvoCliente.text()
        provincia = self.lineEdit_provinciaNvoCliente.text()
        pais = self.lineEdit_paisNvoCliente.text()
        observaciones = self.lineEdit_obsercacionesNvoCliente.text()
        condiva = self.comboBox_CondIVANvoCliente.currentText()
        # item = self.lineEdit_obsercacionesNvoCliente.text()
        # if item is not None:
        #     observaciones = str(item.text())
        # else:
        #     observaciones = None

        if nombre == '' or nombre.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Nombre no puede estar vacío o no ser sólo letras", )
            self.lineEdit_nombreNvoCliente.setText('')
            self.lineEdit_nombreNvoCliente.setFocus()
            return

        if apellido == '' or apellido.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Apellido no puede estar vacío o no ser sólo letras", )
            self.lineEdit_apellidoNvoCliente.setText('')
            self.lineEdit_apellidoNvoCliente.setFocus()
            return

        try:
            int_dni = int(dni)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de DNI no puede estar vacío o no ser números enteros", )
            self.lineEdit_lineEdit_dniNvoCliente.setText('')
            self.lineEdit_lineEdit_dniNvoCliente.setFocus()
            return

        try:
            int_cuit = int(cuit)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de CUIT/CUIL no puede estar vacío o no ser números enteros", )
            self.lineEdit_cuitNvoCliente.setText('')
            self.lineEdit_cuitNvoCliente.setFocus()
            return

        try:
            int_telefono = int(telefono)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor del Teléfono debe ser sólo números enteros", )
            self.lineEdit_telefonoNvoCliente.setText('')
            self.lineEdit_telefonoNvoCliente.setFocus()
            return

        cliente = Cliente(codigo, nombre, apellido, dni, empresa, cuit, telefono, email, direccion, numero, localidad,
                          provincia, pais, observaciones, condiva)
        clientes_insertados = ClienteDAO.insertar(cliente)
        log.debug(f'Clientes insertados: {clientes_insertados}')
        self.label_ingresar_msg2.setText('Cliente ingresado correctamente')
        QMessageBox.information(self, "Cliente Ingresado",
                                "El cliente ha sido ingresado correctamente", )
        self.listar_clientes()
        return

    def buscar_cliente(self):
        campo1 = 'nombre'
        campo2 = 'apellido'
        campo3 = 'empresa'
        valor = str(self.lineEdit_BuscarArticulo_2.text())
        clientes = ClienteDAO.buscar_cliente(campo1, campo2, campo3, valor)
        self.tablaClientes.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            self.tablaClientes.setItem(i, 0, QtWidgets.QTableWidgetItem(str(cliente.codigo)))
            self.tablaClientes.setItem(i, 1, QtWidgets.QTableWidgetItem(cliente.nombre))
            self.tablaClientes.setItem(i, 2, QtWidgets.QTableWidgetItem(cliente.apellido))
            self.tablaClientes.setItem(i, 3, QtWidgets.QTableWidgetItem(cliente._dni))
            self.tablaClientes.setItem(i, 4, QtWidgets.QTableWidgetItem(cliente.empresa))
            self.tablaClientes.setItem(i, 5, QtWidgets.QTableWidgetItem(cliente._cuit))
            self.tablaClientes.setItem(i, 6, QtWidgets.QTableWidgetItem(cliente._telefono))
            self.tablaClientes.setItem(i, 7, QtWidgets.QTableWidgetItem(cliente._email))
            self.tablaClientes.setItem(i, 8, QtWidgets.QTableWidgetItem(cliente._direccion))
            self.tablaClientes.setItem(i, 9, QtWidgets.QTableWidgetItem(cliente._numero))
            self.tablaClientes.setItem(i, 10, QtWidgets.QTableWidgetItem(cliente._localidad))
            self.tablaClientes.setItem(i, 11, QtWidgets.QTableWidgetItem(cliente._provincia))
            self.tablaClientes.setItem(i, 12, QtWidgets.QTableWidgetItem(cliente._pais))
            self.tablaClientes.setItem(i, 13, QtWidgets.QTableWidgetItem(cliente._observaciones))
            self.tablaClientes.setItem(i, 13, QtWidgets.QTableWidgetItem(cliente._condiva))
            self.tablaClientes.resizeColumnsToContents()
            self.tablaClientes.resizeRowsToContents()
            log.debug(cliente)

    ##############################################################################################
    ##############################################################################################
    #
    #                           EMPIEZA PARTE PROVEEDORES
    #
    #
    ##############################################################################################

    ##############################################################################################

    def modificar_proveedor(self):
        row = self.tablaProveedores.currentRow()
        codproveedor = int(self.tablaProveedores.item(row, 0).text())
        razonsocial = str(self.tablaProveedores.item(row, 1).text())
        cuit = str(self.tablaProveedores.item(row, 2).text())
        domicilio = str(self.tablaProveedores.item(row, 3).text())
        ciudad = str(self.tablaProveedores.item(row, 4).text())
        provincia = str(self.tablaProveedores.item(row, 5).text())
        pais = str(self.tablaProveedores.item(row, 6).text())
        telefono = str(self.tablaProveedores.item(row, 7).text())
        web = str(self.tablaProveedores.item(row, 8).text())
        email = str(self.tablaProveedores.item(row, 9).text())
        cuenta = str(self.tablaProveedores.item(row, 10).text())
        password = str(self.tablaProveedores.item(row, 11).text())
        # observaciones = str(self.tablaProveedores.item(row, 12).text())
        item = self.tablaProveedores.item(row, 12)
        if item is not None:
            observaciones = str(item.text())
        else:
            observaciones = None
        button = QMessageBox.question(self, "Modificar Proveedor", "Está seguro que desea modificar el proveedor?", )

        try:
            int_cuit = int(cuit)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de CUIT no puede estar vacío o no ser números enteros", )
            self.tablaProveedores.item(row, 2).setText('')
            self.tablaProveedores.setCurrentCell(row, 2)
            self.tablaProveedores.editItem(self.tablaProveedores.item(row, 2))
            return

        if ciudad == '' or ciudad.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Ciudad no puede estar vacío o no ser sólo letras", )
            self.tablaProveedores.item(row, 4).setText('')
            self.tablaProveedores.setCurrentCell(row, 4)
            self.tablaProveedores.editItem(self.tablaProveedores.item(row, 4))
            return

        if provincia == '' or provincia.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Provincia no puede estar vacío o no ser sólo letras", )
            self.tablaProveedores.item(row, 5).setText('')
            self.tablaProveedores.setCurrentCell(row, 5)
            self.tablaProveedores.editItem(self.tablaProveedores.item(row, 5))
            return

        if pais == '' or pais.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de País no puede estar vacío o no ser sólo letras", )
            self.tablaProveedores.item(row, 6).setText('')
            self.tablaProveedores.setCurrentCell(row, 6)
            self.tablaProveedores.editItem(self.tablaProveedores.item(row, 6))
            return

        try:
            int_telefono = int(telefono)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor del Teléfono debe ser sólo números enteros", )
            self.tablaProveedores.item(row, 7).setText('')
            self.tablaProveedores.setCurrentCell(row, 7)
            self.tablaProveedores.editItem(self.tablaProveedores.item(row, 7))
            return

        if button == QMessageBox.Yes:
            print("SI!")
            proveedor = Proveedor(codproveedor, razonsocial, cuit, domicilio, ciudad, provincia, pais, telefono, web,
                                  email, cuenta, password, observaciones)
            proveedores_actualizados = ProveedorDAO.actualizar(proveedor)
            log.debug(f'Clientes actualizados: {proveedores_actualizados}')
            self.label_ingresar_msg2.setText('Proveedor actualizado correctamente')
            QMessageBox.information(self, "Proveedor Modificado",
                                    "El proveedor ha sido modificado correctamente", )
        else:
            print("NO!")
            self.listar_proveedores()
            return

    def mostrar_insertar_proveedor(self):
        self.stackedWidget.setCurrentIndex(6)
        self.bt_guardarNvoProveedor.clicked.connect(self.insertar_proveedor)

    def insertar_proveedor(self):
        codproveedor = self.lineEdit_codigoNvoProveedor.text()
        razonsocial = self.lineEdit_razonsocialNvoProveedor.text()
        cuit = self.lineEdit_cuitNvoProveedor.text()
        domicilio = self.lineEdit_domicilioNvoProveedor.text()
        ciudad = self.lineEdit_ciudadNvoProveedor.text()
        provincia = self.lineEdit_provinciaNvoProveedor.text()
        pais = self.lineEdit_paisNvoProveedor.text()
        telefono = self.lineEdit_telefonoNvoProveedor.text()
        web = self.lineEdit_weblNvoProveedor.text()
        email = self.lineEdit_emailNvoProveedor.text()
        cuenta = self.lineEdit_cuentaNvoProveedor.text()
        password = self.lineEdit_passwordNvoProveedor.text()
        observaciones = self.lineEdit_obsercacionesNvoProveedor.text()
        # item = self.lineEdit_obsercacionesNvoCliente.text()
        # if item is not None:
        #     observaciones = str(item.text())
        # else:
        #     observaciones = None

        try:
            int_cuit = int(cuit)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de CUIT no puede estar vacío o no ser números enteros", )
            self.lineEdit_cuitNvoProveedor.setText('')
            self.lineEdit_cuitNvoProveedor.setFocus()
            return

        if ciudad == '' or ciudad.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Ciudad no puede estar vacío o no ser sólo letras", )
            self.lineEdit_ciudadNvoProveedor.setText('')
            self.lineEdit_ciudadNvoProveedor.setFocus()
            return

        if provincia == '' or provincia.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de Provincia no puede estar vacío o no ser sólo letras", )
            self.lineEdit_provinciaNvoProveedor.setText('')
            self.lineEdit_provinciaNvoProveedor.setFocus()
            return

        if pais == '' or pais.isdigit():
            QMessageBox.information(self, "Error de Validación",
                                    "El valor de País no puede estar vacío o no ser sólo letras", )
            self.lineEdit_paisNvoProveedor.setText('')
            self.lineEdit_paisNvoProveedor.setFocus()
            return

        try:
            int_telefono = int(telefono)
        except ValueError:
            QMessageBox.information(self, "Error de Validación",
                                    "El valor del Teléfono debe ser sólo números enteros", )
            self.lineEdit_telefonoNvoProveedor.setText('')
            self.lineEdit_telefonoNvoProveedor.setFocus()
            return

        proveedor = Proveedor(codproveedor, razonsocial, cuit, domicilio, ciudad, provincia, pais, telefono, web, email,
                              cuenta, password, observaciones)
        proveedores_insertados = ProveedorDAO.insertar(proveedor)
        log.debug(f'Clientes insertados: {proveedores_insertados}')
        self.label_ingresar_msg2.setText('Proveedor ingresado correctamente')
        QMessageBox.information(self, "Proveedor Ingresado",
                                "El proveedor ha sido ingresado correctamente", )
        self.listar_proveedores()
        return

    def eliminar_proveedor(self):
        row = self.tablaProveedores.currentRow()
        item = self.tablaProveedores.item(row, 0)
        if item is not None:
            self.label_capturaSeleccion.setText(item.text())
            print(f'Fila seleccionada: {item.text()}')
        codproveedor = self.tablaProveedores.item(row, 0).text()
        razonsocial = self.tablaProveedores.item(row, 1).text()
        cuit = self.tablaProveedores.item(row, 2).text()
        domicilio = self.tablaProveedores.item(row, 3).text()
        ciudad = self.tablaProveedores.item(row, 4).text()
        provincia = self.tablaProveedores.item(row, 5).text()
        pais = self.tablaProveedores.item(row, 6).text()
        telefono = self.tablaProveedores.item(row, 7).text()
        web = self.tablaProveedores.item(row, 8).text()
        email = self.tablaProveedores.item(row, 9).text()
        cuenta = self.tablaProveedores.item(row, 10).text()
        password = self.tablaProveedores.item(row, 11).text()
        observaciones = self.tablaProveedores.item(row, 12).text()
        # item = self.tablaProveedores.item(row, 13)
        # if item is not None:
        #    observaciones = str(item.text())
        # else:
        #    observaciones = None

        button = QMessageBox.question(self, "Eliminar Proveedor", "Está seguro que desea eliminar el proveedor?", )

        if button == QMessageBox.Yes:
            print("SI!")
            proveedor = Proveedor(codproveedor, razonsocial, cuit, domicilio, ciudad, provincia, pais, telefono, web,
                                  email, cuenta, password, observaciones)
            proveedores_eliminados = ProveedorDAO.eliminar(proveedor)
            log.debug(f'Proveedores eliminados: {proveedores_eliminados}')
            # self.label_ingresar_msg2.setText('Proveedor eliminado correctamente')
            QMessageBox.information(self, "Proveedor Eliminado",
                                    "El proveedor ha sido eliminado correctamente", )
        else:
            print("NO!")
        self.listar_proveedores()
        return

    def buscar_proveedor(self):
        campo1 = 'razonsocial'
        campo2 = 'cuit'
        campo3 = 'web'
        valor = str(self.lineEdit_BuscarArticulo_3.text())
        proveedores = ProveedorDAO.buscar_proveedor(campo1, campo2, campo3, valor)
        self.tablaProveedores.setRowCount(len(proveedores))
        for i, proveedor in enumerate(proveedores):
            self.tablaProveedores.setItem(i, 0, QtWidgets.QTableWidgetItem(str(proveedor.codproveedor)))
            self.tablaProveedores.setItem(i, 1, QtWidgets.QTableWidgetItem(proveedor.razonsocial))
            self.tablaProveedores.setItem(i, 2, QtWidgets.QTableWidgetItem(proveedor._cuit))
            self.tablaProveedores.setItem(i, 3, QtWidgets.QTableWidgetItem(proveedor._domicilio))
            self.tablaProveedores.setItem(i, 4, QtWidgets.QTableWidgetItem(proveedor._ciudad))
            self.tablaProveedores.setItem(i, 5, QtWidgets.QTableWidgetItem(proveedor._provincia))
            self.tablaProveedores.setItem(i, 6, QtWidgets.QTableWidgetItem(proveedor._pais))
            self.tablaProveedores.setItem(i, 7, QtWidgets.QTableWidgetItem(proveedor._telefono))
            self.tablaProveedores.setItem(i, 8, QtWidgets.QTableWidgetItem(proveedor._web))
            self.tablaProveedores.setItem(i, 9, QtWidgets.QTableWidgetItem(proveedor._email))
            self.tablaProveedores.setItem(i, 10, QtWidgets.QTableWidgetItem(proveedor._cuenta))
            self.tablaProveedores.setItem(i, 11, QtWidgets.QTableWidgetItem(proveedor._password))
            self.tablaProveedores.setItem(i, 12, QtWidgets.QTableWidgetItem(proveedor._observaciones))
            log.debug(proveedor)
            self.tablaProveedores.resizeColumnsToContents()
            self.tablaProveedores.resizeRowsToContents()

    ##############################################################################################
    #
    #                   SELECCIONAR CATEGORIA NUEVO ARTICULO
    #
    ##############################################################################################

    def seleccionar_categoria(self):
        self.dialogo_categoria = QtWidgets.QDialog()
        self.ui = Ui_ventana_Categorias()
        self.ui.setupUi(self.dialogo_categoria)

        # Obtener las categorias de la base de datos
        categorias = ArticuloDAO.seleccionar_categorias()

        # Crear un modelo para la lista
        model = QtGui.QStandardItemModel()

        # Añadir las categorías al modelo
        for categoria in categorias:
            item = QtGui.QStandardItem(categoria)
            model.appendRow(item)

        # Asignar el modelo a la lista
        self.ui.listView_categorias.setModel(model)
        self.ui.bt_SeleccionarCategoria.clicked.connect(self.seleccionada_categoria)
        self.ui.bt_AgregarCategoria.clicked.connect(self.mostrar_agregar_categoria)
        self.dialogo_categoria.exec_()

    def seleccionada_categoria(self):
        index = self.ui.listView_categorias.currentIndex()
        item = index.data()
        self.lineEdit_categoriaNvoArticulo.setText(item)
        self.lineEdit.setText(item)
        categoria_seleccionada = item
        self.dialogo_categoria.close()

    def mostrar_agregar_categoria(self):
        self.dialogo_categoria.close()
        self.dialogo_categoria = QtWidgets.QDialog()
        self.ui = Ui_ventana_nueva_categoria()
        self.ui.setupUi(self.dialogo_categoria)
        self.ui.bt_GuardarCategoria.clicked.connect(self.agregar_categoria)
        self.dialogo_categoria.exec_()

    def agregar_categoria(self):
        categoria = self.ui.lineEdit_nuevoCodCategoria_2.text()
        categorias = ArticuloDAO.agregar_categoria(categoria)
        log.debug(f'Categorias insertadas: {categorias}')
        self.label_ingresar_msg2.setText('Categoría ingresada correctamente')
        QMessageBox.information(self, "Categoría Ingresada",
                                "La categoría ha sido ingresada correctamente", )
        self.dialogo_categoria.close()
        return

    ##############################################################################################
    #
    #                   SELECCIONAR MARCA NUEVO ARTICULO
    #
    ##############################################################################################

    def seleccionar_marca(self):
        self.dialogo_marca = QtWidgets.QDialog()
        self.ui = Ui_ventana_Marca()
        self.ui.setupUi(self.dialogo_marca)

        # Obtener las categorias de la base de datos
        marcas = ArticuloDAO.seleccionar_marcas()

        # Crear un modelo para la lista
        model = QtGui.QStandardItemModel()

        # Añadir las categorías al modelo
        for marca in marcas:
            item = QtGui.QStandardItem(marca)
            model.appendRow(item)

        # Asignar el modelo a la lista
        self.ui.listView_marcas.setModel(model)
        self.ui.bt_SeleccionarMarca.clicked.connect(self.seleccionada_marca)
        self.ui.bt_AgregarMarca.clicked.connect(self.mostrar_agregar_marcas)
        self.dialogo_marca.exec_()

    def seleccionada_marca(self):
        index = self.ui.listView_marcas.currentIndex()
        item = index.data()
        self.lineEdit_marcaNvoArticulo.setText(item)
        categoria_seleccionada = item
        self.dialogo_marca.close()

    def mostrar_agregar_marcas(self):
        self.dialogo_marca.close()
        self.dialogo_marca = QtWidgets.QDialog()
        self.ui = Ui_ventana_nueva_marca()
        self.ui.setupUi(self.dialogo_marca)
        self.ui.bt_GuardarMarca.clicked.connect(self.agregar_marca)
        self.dialogo_marca.exec_()

    def agregar_marca(self):
        marca = self.ui.lineEdit_nuevoDescripcionMarca.text()
        marcas = ArticuloDAO.agregar_marca(marca)
        log.debug(f'Categorias insertadas: {marcas}')
        self.label_ingresar_msg2.setText('Marca ingresada correctamente')
        QMessageBox.information(self, "Marca Ingresada",
                                "La marca ha sido ingresada correctamente", )
        self.dialogo_marca.close()
        return

        ##############################################################################################
        #
        #                   SELECCIONAR PROVEEDOR
        #
        ##############################################################################################

    def seleccionar_proveedor(self):
        self.dialogo_proveedor = QtWidgets.QDialog()
        self.ui = Ui_ventana_proveedores()
        self.ui.setupUi(self.dialogo_proveedor)

        # Obtener las proveedores de la base de datos
        proveedores = ProveedorDAO.seleccionar_proveedores()

        # Crear un modelo para la lista
        model = QtGui.QStandardItemModel()

        # Añadir las categorías al modelo
        for proveedor in proveedores:
            item = QtGui.QStandardItem(proveedor)
            model.appendRow(item)

        # Asignar el modelo a la lista
        self.ui.listView_proveedores.setModel(model)
        self.ui.bt_SeleccionarProveedor.clicked.connect(self.seleccionado_proveedor)
        self.dialogo_proveedor.exec_()

    def seleccionado_proveedor(self):
        index = self.ui.listView_proveedores.currentIndex()
        item = index.data()
        self.lineEdit_proveedorNvoArticulo.setText(item)
        self.dialogo_proveedor.close()

    ##############################################################################################
    #
    #                   NUEVA FACTURA
    #
    ##############################################################################################

    def seleccionar_cliente_nueva_factura(self):
        # self.dialogo_agregar_cliente_factura = QtWidgets.QDialog()
        # self.ui_agregar_cliente_Fact = Ui_ventana_agregar_cliente_factura()
        # self.ui_agregar_cliente_Fact.setupUi(self.dialogo_agregar_cliente_factura)
        self.dialogo_agregar_cliente_factura.setMaximumSize(1029, 540)  # Ancho máximo 800, altura máxima 600
        self.dialogo_agregar_cliente_factura.setMinimumSize(1029, 540)  # Ancho mínimo 400, altura mínima 300

        # Obtener los clientes de la base de datos
        clientes = ClienteDAO.seleccionar()

        self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 0, QtWidgets.QTableWidgetItem(
                str(cliente.codigo)))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 1, QtWidgets.QTableWidgetItem(
                cliente.nombre))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 2, QtWidgets.QTableWidgetItem(
                cliente.apellido))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 3, QtWidgets.QTableWidgetItem(
                cliente.dni))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 4, QtWidgets.QTableWidgetItem(
                cliente.empresa))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(
                cliente.cuit))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(
                cliente.telefono))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(
                cliente.email))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 8, QtWidgets.QTableWidgetItem(
                cliente.direccion))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 9, QtWidgets.QTableWidgetItem(
                cliente.numero))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 10, QtWidgets.QTableWidgetItem(
                cliente.localidad))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 11, QtWidgets.QTableWidgetItem(
                cliente.provincia))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 12, QtWidgets.QTableWidgetItem(
                cliente.pais))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 13, QtWidgets.QTableWidgetItem(
                cliente.observaciones))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 14, QtWidgets.QTableWidgetItem(
                cliente.condiva))

            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.resizeColumnsToContents()
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.resizeRowsToContents()
        # self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.doubleClicked.connect(self.agregar_cliente_click)

        # Crear un modelo para la lista
        # model = QtGui.QStandardItemModel()

        # Añadir las categorías al modelo
        # for cliente in clientes:
        #    item = QtGui.QStandardItem(clientes)
        #    model.appendRow(item)

        # Asignar el modelo a la lista
        # self.ui.listView_clientes.setModel(model)
        # self.ui.tableWidgetAgregarClienteNvaFactura.setModel(model)
        # self.ui.bt_SeleccionarCliente.clicked.connect(self.seleccionado_cliente)
        self.lineEdit_BuscarArticuloNvaFactura1.setFocus()
        self.lineEdit_BuscarArticuloNvaFactura1.setCursorPosition(0)
        self.dialogo_agregar_cliente_factura.exec_()

    def buscar_cliente_nueva_factura(self):
        campo1 = 'nombre'
        campo2 = 'apellido'
        campo3 = 'empresa'
        valor1 = str(self.ui_agregar_cliente_Fact.lineEdit_BuscarItemArticuloNvaFactura.text())
        clientes = ClienteDAO.buscar_cliente(campo1, campo2, campo3, valor1)

        self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 0, QtWidgets.QTableWidgetItem(
                str(cliente.codigo)))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 1, QtWidgets.QTableWidgetItem(
                cliente.nombre))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 2, QtWidgets.QTableWidgetItem(
                cliente.apellido))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 3, QtWidgets.QTableWidgetItem(
                cliente.dni))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 4, QtWidgets.QTableWidgetItem(
                cliente.empresa))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(
                cliente.cuit))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(
                cliente.telefono))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(
                cliente.email))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 8, QtWidgets.QTableWidgetItem(
                cliente.direccion))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 9, QtWidgets.QTableWidgetItem(
                cliente.numero))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 10, QtWidgets.QTableWidgetItem(
                cliente.localidad))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 11, QtWidgets.QTableWidgetItem(
                cliente.provincia))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 12, QtWidgets.QTableWidgetItem(
                cliente.pais))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 13, QtWidgets.QTableWidgetItem(
                cliente.observaciones))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 14, QtWidgets.QTableWidgetItem(
                cliente.cond_iva))

            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.resizeColumnsToContents()
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.resizeRowsToContents()
            self.lineEdit_BuscarArticuloNvaFactura1.setFocus()
            self.lineEdit_BuscarArticuloNvaFactura1.setCursorPosition(0)

    def modulo_facturacion(self):
        self.stackedWidget.setCurrentIndex(0)
        # lista = FacturaDAO.seleccionar()
        # tabla = self.tableWidget_ultimasFacturas
        # Funciones.fx_cargarTablaX(lista, self.tableWidget_ultimasFacturas, limpiaTabla=True)
        facturas = FacturaDAO.seleccionar()
        self.tableWidget_ultimasFacturas.setRowCount(len(facturas))
        for i, factura in enumerate(facturas):
            self.tableWidget_ultimasFacturas.setItem(i, 0, QtWidgets.QTableWidgetItem(str(factura.serie)))
            self.tableWidget_ultimasFacturas.setItem(i, 1, QtWidgets.QTableWidgetItem(str(factura.codfactura)))
            self.tableWidget_ultimasFacturas.setItem(i, 2, QtWidgets.QTableWidgetItem(str(factura.tipo)))
            self.tableWidget_ultimasFacturas.setItem(i, 3, QtWidgets.QTableWidgetItem(str(factura.fecha)))
            self.tableWidget_ultimasFacturas.setItem(i, 4, QtWidgets.QTableWidgetItem(str(factura.codcliente)))
            self.tableWidget_ultimasFacturas.setItem(i, 5, QtWidgets.QTableWidgetItem(str(factura.cliente)))
            self.tableWidget_ultimasFacturas.setItem(i, 6, QtWidgets.QTableWidgetItem(str(factura.estado)))
            self.tableWidget_ultimasFacturas.setItem(i, 7, QtWidgets.QTableWidgetItem(str(factura.subtotal)))
            self.tableWidget_ultimasFacturas.setItem(i, 8, QtWidgets.QTableWidgetItem(str(factura.iva)))
            self.tableWidget_ultimasFacturas.setItem(i, 9, QtWidgets.QTableWidgetItem(str(factura.total)))
            self.tableWidget_ultimasFacturas.setItem(i, 10, QtWidgets.QTableWidgetItem(str(factura.formapago)))

        self.tableWidget_ultimasFacturas.resizeColumnsToContents()
        self.tableWidget_ultimasFacturas.resizeRowsToContents()
        self.buscar_fact_pendiente()
        self.buscar_fact_cobrar()

    def seleccionar_factura(self):
        row = self.tableWidget_ultimasFacturas.currentRow()
        codfactura = int(self.tableWidget_ultimasFacturas.item(row, 1).text())
        detalles = detalleFacturaDAO.busca_detalle(codfactura)
        self.tableWidget_detalleultimasFacturas_2.setRowCount(len(detalles))
        for i, detalle in enumerate(detalles):
            self.tableWidget_detalleultimasFacturas_2.setItem(i, 0,
                                                              QtWidgets.QTableWidgetItem(str(detalle.codarticulo)))
            self.tableWidget_detalleultimasFacturas_2.setItem(i, 1, QtWidgets.QTableWidgetItem(detalle.descripcion))
            self.tableWidget_detalleultimasFacturas_2.setItem(i, 2, QtWidgets.QTableWidgetItem(str(detalle.cantidad)))
            self.tableWidget_detalleultimasFacturas_2.setItem(i, 3,
                                                              QtWidgets.QTableWidgetItem(str(detalle.precioventa)))
            self.tableWidget_detalleultimasFacturas_2.setItem(i, 4, QtWidgets.QTableWidgetItem(str(detalle.importe)))
            self.tableWidget_detalleultimasFacturas_2.setItem(i, 5, QtWidgets.QTableWidgetItem(str(detalle.iva)))
            self.tableWidget_detalleultimasFacturas_2.resizeColumnsToContents()
            self.tableWidget_detalleultimasFacturas_2.resizeRowsToContents()
            log.debug(detalle)
        # Funciones.fx_cargarTablaX(detalles, self.tableWidget_detalleultimasFacturas_2, limpiaTabla=True)
        # self.tableWidget_detalleultimasFacturas_2.resizeColumnsToContents()
        # self.tableWidget_detalleultimasFacturas_2.resizeRowsToContents()
        log.debug(detalles)

    def nueva_factura(self):
        self.stackedWidget.setCurrentIndex(7)
        num_rows = self.tableWidgetDetalleNvaFactura.rowCount()
        for i in range(num_rows):
            self.tableWidgetDetalleNvaFactura.removeRow(0)
        self.lineEdit_clienteNvaFactura.clear()
        self.lineEdit_domclienteNvaFactura.clear()
        self.lineEdit_codclienteNvaFactura.clear()
        self.lineEdit_cuitclienteNvaFactura.clear()
        self.lineEdit_dniclienteNvaFactura_2.clear()
        self.lineEdit_telclienteNvaFactura.clear()
        self.lineEdit_emailclienteNvaFactura.clear()
        self.tableWidgetDetalleNvaFactura.clearContents()
        self.label_subtotal_factura.clear()
        self.label_iva_factura.clear()
        self.label_total_Nva_factura.clear()
        self.lineEdit_BuscarArticuloNvaFactura1.setFocus()
        self.lineEdit_BuscarArticuloNvaFactura1.setCursorPosition(0)

        # Obtener la fecha y hora actual
        now = datetime.now()

        # Convertir la fecha y hora a una cadena de texto en español
        now_str = now.strftime('%d/%m/%Y, %H:%M:%S')

        # Establecer el texto del QLineEdit
        self.lineEdit_fechaNvaFactura.setText(now_str)
        self.lineEdit_fechaNvaFactura.setReadOnly(True)
        ############################################
        #       LLENAR LOS DATOS DE LA FACTURA CON LOS DATOS DE LA EMPRESA DE LA BD#####3
        #
        ###########################################
        empresa = EmpresaDAO.seleccionar()
        if empresa:
            empresa = empresa[0]
            self.label_71.setText(empresa.razonsocial)
            self.label_68.setText(empresa.nombrefantasia)
            self.lineEdit_cuitNvaFactura.setText(str(empresa.cuit))
            self.label_91.setText(empresa.categoria)
            self.lineEdit_IIBBNvaFactura.setText(str(empresa.iibb))
            self.lineEdit_inicioActNvaFactura_2.setText(empresa.inicioactividades)

        else:
            # Handle the case when there are no empresas
            print("Primero debe cargar los datos de su empresa en Módulo Empresa para poder continuar.")
            return
        domicilio = empresa.domicilio
        localidad = empresa.localidad
        provincia = empresa.provincia
        pais = empresa.pais
        direccion_completa_empresa = " , ".join([domicilio, localidad, provincia, pais])
        # self.lineEdit_localidadNvaFactura.setText(empresa.localidad)
        self.label_72.setText(direccion_completa_empresa)
        ############################################################################################
        # CARGAMOS EL LOGO DE LA EMPRESA EN LA NUEVA FACTURA
        # Crear un QPixmap con la ruta de la imagen
        # self.factura_logo.clear()
        # Crear un QPixmap con la ruta de la imagen
        logo_pixmap = QPixmap('_internal/Interfaz/Icons/logo.png')

        # Establecer el tamaño del QLabel
        self.factura_logo.setFixedSize(100, 100)

        # Escalar el QPixmap al tamaño deseado
        logo_pixmap = logo_pixmap.scaled(self.factura_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Establecer el QPixmap en la QLabel
        self.factura_logo.setPixmap(logo_pixmap)

        # Mover la QLabel a la posición deseada
        self.factura_logo.move(70, 60)

        ###############################################################################

        self.lineEdit_serieNvaFactura.setText("1".zfill(5))

        query_NroFactura = "SELECT DISTINCT ON (codfactura) * FROM facturas ORDER BY codfactura DESC"

        with CursorDelPool() as cursor:
            cursor.execute(query_NroFactura)
            registros = cursor.fetchall()
            facturas = []
            for registro in registros:
                factura = Factura(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10])
                facturas.append(factura)
            if facturas:
                self.lineEdit_numeroNvaFactura.setText(str(facturas[0].codfactura + 1).zfill(8))
            else:
                self.lineEdit_numeroNvaFactura.setText("1".zfill(8))  # or handle the error as you see fit
            return facturas

    def agregar_articulo_nueva_factura(self):

        # self.dialogo_agregar_Art_Factura = QtWidgets.QDialog()
        # self.ui_ventana_agr_articulo = Ui_ventana_agregar_articulo()
        # self.ui_ventana_agr_articulo.setupUi(self.dialogo_agregar_Art_Factura)
        # self.ui.lineEdit_BuscarArticuloNvaFactura3.textChanged.connect(self.buscar_articulo_nueva_factura)
        # self.ui.bt_AgregarArticuloNvaFactura.clicked.connect(self.buscar_articulo_nueva_factura)
        articulos = ArticuloDAO.seleccionar()
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setRowCount(len(articulos))
        for i, articulo in enumerate(articulos):
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 0, QtWidgets.QTableWidgetItem(
                str(articulo.codigo)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 1, QtWidgets.QTableWidgetItem(
                articulo.nombre))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 2, QtWidgets.QTableWidgetItem(
                articulo._modelo))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 3, QtWidgets.QTableWidgetItem(
                articulo._marca))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 4, QtWidgets.QTableWidgetItem(
                articulo._categoria))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 5,
                                                                                       QtWidgets.QTableWidgetItem(
                                                                                           str(articulo._precio_costo)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 6,
                                                                                       QtWidgets.QTableWidgetItem(
                                                                                           str(articulo._precio_venta)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(
                str(articulo._iva)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 8, QtWidgets.QTableWidgetItem(
                str(articulo._stock)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 9, QtWidgets.QTableWidgetItem(
                str(articulo._margen_ganancia)))
            log.debug(articulo)
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.resizeColumnsToContents()
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.resizeRowsToContents()
        self.ui_ventana_agr_articulo.lineEdit_BuscarArticuloFacturaNueva.textChanged.connect(
            self.buscar_articulo_nueva_factura)
        self.dialogo_agregar_Art_Factura.exec_()

    def buscar_articulo_nueva_factura(self):
        campo1 = 'nombre'
        campo2 = 'codigo'
        campo3 = 'cod_barras'
        valor1 = self.ui_ventana_agr_articulo.lineEdit_BuscarArticuloFacturaNueva.text()
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.clearContents()
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setRowCount(0)
        articulos = ArticuloDAO.buscar_articulo_nombre(campo1, campo2, campo3, valor1)
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setRowCount(len(articulos))
        for i, articulo in enumerate(articulos):
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 0, QtWidgets.QTableWidgetItem(
                str(articulo.codigo)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 1, QtWidgets.QTableWidgetItem(
                articulo.nombre))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 2, QtWidgets.QTableWidgetItem(
                articulo._modelo))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 3, QtWidgets.QTableWidgetItem(
                articulo._marca))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 4, QtWidgets.QTableWidgetItem(
                articulo._categoria))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(
                str(articulo._precio_costo)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(
                str(articulo._precio_venta)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(
                str(articulo._iva)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 8, QtWidgets.QTableWidgetItem(
                str(articulo._stock)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 9, QtWidgets.QTableWidgetItem(
                str(articulo._margen_ganancia)))
            log.debug(articulo)
        return

        # self.bt_guardarNvaFactura.clicked.connect(self.guardar_nueva_factura)

    def agregar_articulo_nueva_factura2(self):
        tabla = self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura
        lista = Funciones.fx_leer_seleccion_tabla(tabla)[0]
        print(lista)
        print("metodo llamado")
        precio_costo_str = tabla.item(tabla.currentRow(), 5).text().replace('$', '').replace(',', '')
        importe_iva = (float(precio_costo_str) * float(tabla.item(tabla.currentRow(), 7).text())) / 100
        precio_unitario = float(precio_costo_str) + importe_iva
        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura.rowCount()
        total = 0
        ################################################################################################
        # nueva_lista = []
        # for i in lista:
        #     nueva_lista.append([i[0], i[1], "1", i[5], i[7], importe_iva, precio_unitario, precio_unitario])
        #     #self.label_subtotal_factura.setText(str(round(precio_unitario, 2)))
        # print(nueva_lista)
        # Funciones.fx_cargarTablaX(nueva_lista, self.tableWidgetDetalleNvaFactura, limpiaTabla=False)
        # self.tableWidgetDetalleNvaFactura.resizeColumnsToContents()
        # self.tableWidgetDetalleNvaFactura.resizeRowsToContents()
        # self.verificarExistencias()
        # self.actualizar_subtotal_factura()
        ##################################################################################################
        # Obtén el código del artículo seleccionado
        codigo_articulo_seleccionado = lista[0][0]

        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura.rowCount()

        # Variable para verificar si el artículo ya está en la tabla
        articulo_ya_en_tabla = False

        # Itera sobre cada fila
        for row in range(num_rows):
            # Obtén el código del artículo en la fila actual (asumiendo que es la columna 0)
            codigo_articulo_en_tabla = self.tableWidgetDetalleNvaFactura.item(row, 0).text()

            # Si el código del artículo seleccionado coincide con el código del artículo en la fila actual
            if codigo_articulo_seleccionado == codigo_articulo_en_tabla:
                # Incrementa la cantidad del artículo en la fila actual (asumiendo que la cantidad es la columna 2)
                cantidad_actual = int(self.tableWidgetDetalleNvaFactura.item(row, 2).text())
                self.tableWidgetDetalleNvaFactura.setItem(row, 2, QtWidgets.QTableWidgetItem(str(cantidad_actual + 1)))

                # Marca que el artículo ya está en la tabla
                articulo_ya_en_tabla = True
                break

        # Si el artículo no está en la tabla, agrega una nueva fila
        if not articulo_ya_en_tabla:
            nueva_lista = []
            for i in lista:
                nueva_lista.append([i[0], i[1], "1", i[5], i[7], importe_iva, precio_unitario, precio_unitario])
            Funciones.fx_cargarTablaX(nueva_lista, self.tableWidgetDetalleNvaFactura, limpiaTabla=False)

        self.tableWidgetDetalleNvaFactura.resizeColumnsToContents()
        self.tableWidgetDetalleNvaFactura.resizeRowsToContents()
        self.verificarExistencias()
        self.actualizar_subtotal_factura()

    def verificarExistencias(self):
        tabla = self.tableWidgetDetalleNvaFactura
        lista = Funciones.fx_leer_seleccion_tabla(tabla)[0]
        for i in lista:
            codarticulo = i[0]
            cantidad = i[2]
            stock = ArticuloDAO.verificar_existencias(codarticulo)
            if cantidad > stock:
                QMessageBox.warning(self, "Stock Insuficiente",
                                    "El stock del artículo seleccionado es insuficiente", )
                return
            else:
                pass

    def actualizar_subtotal_factura(self):
        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura.rowCount()

        # Inicializa el total
        sub_total_factura = 0.0
        sub_total_iva = 0.0
        total_factura = 0.0

        # Itera sobre cada fila
        for row in range(num_rows):
            # Obtén el valor de la columna subtotal (asumiendo que es la columna 7)
            item_factura = self.tableWidgetDetalleNvaFactura.item(row, 7)
            item_iva = self.tableWidgetDetalleNvaFactura.item(row, 5)

            if item_factura is not None:
                subtotal_factura_str = item_factura.text()
                sub_total_factura += float(subtotal_factura_str)

            if item_iva is not None:
                sub_total_iva_str = item_iva.text()
                sub_total_iva += float(sub_total_iva_str)

        # Actualiza label_subtotal_factura con el total
        self.label_subtotal_factura.setText(str(round(sub_total_factura - sub_total_iva, 2)))
        self.label_iva_factura.setText(str(round(sub_total_iva, 2)))
        self.label_total_Nva_factura.setText(str(float(round(sub_total_factura, 2))))

    def actualizar_subtotal(self, row, column):
        # Verifica si la celda cambiada es de la columna "cantidad" (asumiendo que es la columna 2)
        if column == 2:
            # Obtiene el valor de la celda "cantidad"
            cantidad_item = self.tableWidgetDetalleNvaFactura.item(row, column)
            if cantidad_item is not None:
                cantidad = float(cantidad_item.text())
            else:
                return  # No item in the specified cell, so we return early

            ###########################################################
            codigoarticulo = self.tableWidgetDetalleNvaFactura.item(row, 0)
            cantidad_item = self.tableWidgetDetalleNvaFactura.item(row, 2)
            if cantidad_item is not None:
                cantidad = int(cantidad_item.text())
            else:
                return  # No item in the specified cell, so we return early

            stock = ArticuloDAO.verificar_existencias(codigoarticulo)
            if cantidad > stock:
                QMessageBox.warning(self, "Stock Insuficiente",
                                    "El stock del artículo seleccionado es insuficiente, ha seleccionado '{}' y el stock actual es '{}'".format(
                                        cantidad, stock))
                return
            ####################################################################

            # Obtiene el valor de la celda "precio unitario" (asumiendo que es la columna 6)
            precio_unitario_item = self.tableWidgetDetalleNvaFactura.item(row, 6)
            iva_item = self.tableWidgetDetalleNvaFactura.item(row, 5)
            if precio_unitario_item is not None:
                precio_unitario = float(precio_unitario_item.text())
            else:
                return  # No item in the specified cell, so we return early
            if iva_item is not None:
                iva = float(iva_item.text())
            else:
                return

            # Calcula el subtotal
            subtotal = cantidad * precio_unitario
            importe_iva_item = cantidad * iva

            # Actualiza la celda "subtotal" (asumiendo que es la columna 7)
            self.tableWidgetDetalleNvaFactura.setItem(row, 7, QtWidgets.QTableWidgetItem(str((round(subtotal, 2)))))
            self.tableWidgetDetalleNvaFactura.setItem(row, 5,
                                                      QtWidgets.QTableWidgetItem(str((round(importe_iva_item, 2)))))

            self.actualizar_subtotal_factura()

    def agregar_cliente_click(self):
        row = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.currentRow()
        # row = self.tableWidgetDetalleNvaFactura.currentRow()
        # item1 = self.tableWidgetAgregarClienteNvaFactura.item(row, 0)
        # if item1 is not None:

        ### CONCATENAR VALORES DE NOMBRE Y APELLIDO JUNTOS
        nombre = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 1).text()
        apellido = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 2).text()
        nombre_completo = " ".join([nombre, apellido])
        self.lineEdit_clienteNvaFactura.setText(nombre_completo)
        ###########################################
        # self.lineEdit_clienteNvaFactura.setText(self.ui.tableWidgetAgregarClienteNvaFactura.item(0, 1).text())
        # self.lineEdit_domclienteNvaFactura.setText(self.ui.tableWidgetAgregarClienteNvaFactura.item(0, 8).text())

        # concatenar los valores de direccion, numero, localidad, provincia en un solo lineedit
        direccion = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 8).text()
        numero = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 9).text()
        localidad = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 10).text()
        provincia = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 11).text()
        pais = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 12).text()
        # Concatenar los valores con espacios entre ellos
        direccion_completa = " ".join([direccion, numero, localidad, provincia, pais])
        # cond_iva = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 11).text()

        self.lineEdit_domclienteNvaFactura.setText(direccion_completa)
        ############################
        self.lineEdit_codclienteNvaFactura.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 0).text())
        self.lineEdit_cuitclienteNvaFactura.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 5).text())
        self.lineEdit_dniclienteNvaFactura_2.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 3).text())
        self.lineEdit_telclienteNvaFactura.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 6).text())
        self.lineEdit_emailclienteNvaFactura.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 7).text())
        # self.lineEdit_IvaclienteNvaFactura.setText(self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 14).text())
        item_iva = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 14)
        if item_iva is not None:
            self.lineEdit_IvaclienteNvaFactura.setText(item_iva.text())

        if self.lineEdit_IvaclienteNvaFactura.text() == 'RESPONSABLE INSCRIPTO' and self.label_91.text() == 'RESPONSABLE INSCRIPTO':
            self.label_90.setText('A')
        elif self.lineEdit_IvaclienteNvaFactura.text() == 'CONSUMIDOR FINAL' and self.label_91.text() == 'RESPONSABLE INSCRIPTO':
            self.label_90.setText('B')
        elif self.lineEdit_IvaclienteNvaFactura.text() == 'MONOTRIBUTO' and self.label_91.text() == 'RESPONSABLE INSCRIPTO':
            self.label_90.setText('B')
        else:
            self.label_91.text() == 'MONOTRIBUTO'
            self.label_90.setText('C')

        self.dialogo_agregar_cliente_factura.close()

        self.label_84.setText(provincia)

        self.lineEdit_clienteNvaFactura.setReadOnly(True)
        self.lineEdit_domclienteNvaFactura.setReadOnly(True)
        self.lineEdit_codclienteNvaFactura.setReadOnly(True)
        self.lineEdit_cuitclienteNvaFactura.setReadOnly(True)
        self.lineEdit_dniclienteNvaFactura_2.setReadOnly(True)
        self.lineEdit_telclienteNvaFactura.setReadOnly(True)
        self.lineEdit_emailclienteNvaFactura.setReadOnly(True)
        self.lineEdit_IvaclienteNvaFactura.setReadOnly(True)

        return
        # self.lineEdit_clienteNvaFactura.setText = self.Ui_ventana_agregar_cliente_factura.tableWidgetAgregarClienteNvaFactura.item(row, 0).text()

    def listar_empresa(self):
        # self.Ui_ventana_Datos_Empresa = QtWidgets.QDialog()
        # self.ui_ventana_empresa = Ui_ventana_Datos_Empresa()
        # self.ui_ventana_empresa.setupUi(self.Ui_ventana_Datos_Empresa)
        self.Ui_ventana_Datos_Empresa.setMaximumSize(750, 510)  # Ancho máximo 800, altura máxima 600
        self.Ui_ventana_Datos_Empresa.setMinimumSize(750, 510)  # Ancho mínimo 400, altura mínima 300

        query_vacia = EmpresaDAO.seleccionar_vacia()
        if not query_vacia == []:
            self.ui_ventana_empresa.lineEdit_razon_social_empresa.setText(query_vacia[0].razonsocial)
            self.ui_ventana_empresa.lineEdit_nombre_fantasia_empresa.setText(query_vacia[0].nombrefantasia)
            self.ui_ventana_empresa.lineEdit_cuit_empresa.setText(str(query_vacia[0].cuit))
            self.ui_ventana_empresa.lineEdit_categoria_empresa.setText(query_vacia[0].categoria)
            self.ui_ventana_empresa.lineEdit_iibb_empresa.setText(str(query_vacia[0].iibb))
            # iibb_text = self.ui_ventana_empresa.lineEdit_iibb_empresa.text()
            # if iibb_text:
            #     iibb = int(iibb_text)
            # else:
            #     iibb = 0  # or handle the error as you see fit
            self.ui_ventana_empresa.lineEdit_inicio_actividades_empresa.setText(query_vacia[0].inicioactividades)
            self.ui_ventana_empresa.lineEdit_domicilio_empresa.setText(query_vacia[0].domicilio)
            self.ui_ventana_empresa.lineEdit_localidad_empresa.setText(query_vacia[0].localidad)
            self.ui_ventana_empresa.lineEdit_provincia_empresa.setText(query_vacia[0].provincia)
            self.ui_ventana_empresa.lineEdit_pais_empresa.setText(query_vacia[0].pais)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap = QPixmap('_internal/Interfaz/Icons/logo.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap = logo_pixmap.scaled(self.ui_ventana_empresa.label_11.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.ui_ventana_empresa.label_11.setPixmap(logo_pixmap)

            self.ui_ventana_empresa.lineEdit_razon_social_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_nombre_fantasia_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_cuit_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_categoria_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_iibb_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_inicio_actividades_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_domicilio_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_localidad_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_provincia_empresa.setReadOnly(True)
            self.ui_ventana_empresa.lineEdit_pais_empresa.setReadOnly(True)
        else:
            self.ui_ventana_empresa.lineEdit_razon_social_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_nombre_fantasia_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_cuit_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_categoria_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_iibb_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_inicio_actividades_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_domicilio_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_localidad_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_provincia_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_pais_empresa.setReadOnly(False)

        self.Ui_ventana_Datos_Empresa.bt = QtWidgets.QPushButton(self)
        self.ui_ventana_empresa.bt_grabar_datos_empresa.setObjectName("bt_grabar_datos_empresa")
        self.ui_ventana_empresa.bt_grabar_datos_empresa.clicked.connect(self.ingresar_datos_empresa)
        self.ui_ventana_empresa.bt_cancelar_datos_empresa.clicked.connect(self.Ui_ventana_Datos_Empresa.close)

        self.Ui_ventana_Datos_Empresa.exec_()

    def ingresar_datos_empresa(self):
        query_vacia = EmpresaDAO.seleccionar_vacia()
        if query_vacia == []:
            self.ui_ventana_empresa.lineEdit_razon_social_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_nombre_fantasia_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_cuit_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_categoria_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_iibb_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_inicio_actividades_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_domicilio_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_localidad_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_provincia_empresa.setReadOnly(False)
            self.ui_ventana_empresa.lineEdit_pais_empresa.setReadOnly(False)

            razonsocial = self.ui_ventana_empresa.lineEdit_razon_social_empresa.text()
            nombrefantasia = self.ui_ventana_empresa.lineEdit_nombre_fantasia_empresa.text()
            cuit = self.ui_ventana_empresa.lineEdit_cuit_empresa.text()
            categoria = self.ui_ventana_empresa.lineEdit_categoria_empresa.text()
            iibb = int(self.ui_ventana_empresa.lineEdit_iibb_empresa.text())
            inicioactividades = self.ui_ventana_empresa.lineEdit_inicio_actividades_empresa.text()
            domicilio = self.ui_ventana_empresa.lineEdit_domicilio_empresa.text()
            localidad = self.ui_ventana_empresa.lineEdit_localidad_empresa.text()
            provincia = self.ui_ventana_empresa.lineEdit_provincia_empresa.text()
            pais = self.ui_ventana_empresa.lineEdit_pais_empresa.text()
            direccion_completa_empresa = " , ".join([domicilio, localidad, provincia, pais])
            sucursales = 1

            empresa = Empresa(razonsocial, nombrefantasia, cuit, categoria, iibb, inicioactividades, domicilio,
                              localidad, provincia, pais, sucursales)
            empresas_insertadas = EmpresaDAO.insertar(empresa)
            log.debug(f'Empresas insertadas: {empresas_insertadas}')
            self.label_ingresar_msg2.setText('Empresa ingresada correctamente')
            QMessageBox.information(self, "Empresa Ingresada",
                                    "La empresa ha sido ingresada correctamente", )
            self.Ui_ventana_Datos_Empresa.close()
            return
        else:
            QMessageBox.information(self, "La Empresa ya ha sido Ingresada anteriormente",
                                    "La empresa ha sido ingresada anteriormente, no puede ingresarse los valores de una nueva, modifique los actuales", )

        # empresa = Empresa(razonsocial, nombrefantasia, cuit, categoria, iibb, inicioactividades, domicilio, localidad, provincia, pais)
        # empresas_insertadas = EmpresaDAO.insertar(empresa)
        # log.debug(f'Empresas insertadas: {empresas_insertadas}')
        # self.label_ingresar_msg2.setText('Empresa ingresada correctamente')
        # QMessageBox.information(self, "Empresa Ingresada",
        #                         "La empresa ha sido ingresada correctamente", )
        # self.Ui_ventana_Datos_Empresa.close()
        return

    def guardar_factura(self):
        # Obtener los datos de la factura
        codfactura = str(self.lineEdit_numeroNvaFactura.text().zfill(8))
        codcliente = self.lineEdit_codclienteNvaFactura.text()
        cliente = self.lineEdit_clienteNvaFactura.text()
        fecha = self.lineEdit_fechaNvaFactura.text()
        subtotal = self.label_subtotal_factura.text()
        subtotalFact = subtotal
        iva = self.label_iva_factura.text()
        ivaFactura = iva
        total = self.label_total_Nva_factura.text()
        totalFact = total
        serie = self.lineEdit_serieNvaFactura.text().zfill(5)
        estado = self.comboBox_EstadoFactura.currentText()
        formapago = self.comboBox_FormaPagoFact.currentText()
        tipo = self.label_90.text()
        entrega = self.comboBox_Retira.currentText()

        # Crear un objeto Factura
        factura = Factura(serie, codfactura, fecha, codcliente, cliente, estado, subtotal, iva, total, formapago, tipo,
                          entrega)

        # Insertar la factura en la base de datos
        facturas_insertadas = FacturaDAO.insertar(factura)
        log.debug(f'Facturas insertadas: {facturas_insertadas}')
        ###########################################################################################
        facturas_json = factura.__dict__

        # Guardar las facturas en un archivo JSON
        with open('facturas.json', 'w') as f:
            json.dump(facturas_json, f)
        ###########################################################################################
        query_NroDespacho = "SELECT DISTINCT ON (coddespacho) * FROM despacho ORDER BY coddespacho DESC"

        with CursorDelPool() as cursor:
            cursor.execute(query_NroDespacho)
            registros = cursor.fetchall()
            despachos = []
            for registro in registros:
                despacho = Despacho(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                    registro[6], registro[7], registro[8], registro[9], registro[10])
                despachos.append(despacho)
            if despachos:
                codigo_despacho = despachos[0].coddespacho + 1
            else:
                codigo_despacho = 1
        # return despachos

        estado = "PENDIENTE"
        transporte = "-"
        guia = "-"
        tipo = entrega
        observaciones = "-"

        despacho = Despacho(codigo_despacho, fecha, serie, codfactura, codcliente, cliente, estado, tipo, transporte,
                            guia, observaciones)
        despachos_insertados = DespachoDAO.insertar(despacho)

        #self.generar_despacho()


        # Obtener los detalles de la factura
        alicuota_iva = 0
        # Obtén el número de filas en la tabla
        self.tableWidgetDetalleNvaFactura.rowCount()
        for row in range(self.tableWidgetDetalleNvaFactura.rowCount()):
            codarticulo = self.tableWidgetDetalleNvaFactura.item(row, 0).text()
            descripcion = self.tableWidgetDetalleNvaFactura.item(row, 1).text()
            cantidad = self.tableWidgetDetalleNvaFactura.item(row, 2).text()
            precio_unitario = self.tableWidgetDetalleNvaFactura.item(row, 3).text().replace('$', '').replace(',', '')
            importe_iva = self.tableWidgetDetalleNvaFactura.item(row, 5).text()
            subtotal = self.tableWidgetDetalleNvaFactura.item(row, 7).text()
            alicuota_iva = float(self.tableWidgetDetalleNvaFactura.item(row, 4).text())
            # precioventa = self.detallefactura.precioventa.replace('$', '').replace(',', '')
            # valores = (detallefactura.serie, detallefactura.codfactura, detallefactura.codarticulo, detallefactura.descripcion, detallefactura.cantidad, float(precioventa), detallefactura.importe, detallefactura.iva)
            detalle = detalleFactura(serie, codfactura, codarticulo, descripcion, cantidad, precio_unitario, subtotal,
                                     importe_iva, tipo)
            detalleFacturaDAO.insertar(detalle)
            #################################
            # DESCONTAR STOCK DE LOS ARTICULOS
            #################################
            query_stock = "UPDATE articulos SET stock = stock - %s WHERE codigo = %s"
            valores = (cantidad, codarticulo)
            with CursorDelPool() as cursor:
                cursor.execute(query_stock, valores)

        log.debug(f'Detalles insertados: {detalle}')
        ####################################################################################################################################
        #                          RECOPILAR LOS DATOS PARA LA FACTURA ELECTRONICA
        ####################################################################################################################################

        tipo = self.label_90.text()
        fantasia_empresa = self.label_68.text()
        razon_social = self.label_71.text()
        categoria_iva = self.label_91.text()
        cuit_empresa = self.lineEdit_cuitNvaFactura.text()
        iibb_empresa = self.lineEdit_IIBBNvaFactura.text()
        inicio_actividades = self.lineEdit_inicioActNvaFactura_2.text()
        domicilio_empresa = self.label_72.text()
        cliente = self.lineEdit_clienteNvaFactura.text()
        cuit_cliente = self.lineEdit_cuitclienteNvaFactura.text()
        domicilio_cliente = self.lineEdit_domclienteNvaFactura.text()
        condicion_iva = self.lineEdit_IvaclienteNvaFactura.text()
        condicion_vta = self.comboBox_FormaPagoFact.currentText()

        detalles_factura = detalleFacturaDAO.busca_detalle_lista(codfactura)
        print(detalles_factura)
        # print(lista)

        #############################################################################################################################################################
        if tipo == 'A':
            self.facturaA(tipo, fantasia_empresa, razon_social, serie, codfactura, fecha, cuit_empresa, iibb_empresa,
                          inicio_actividades, domicilio_empresa, categoria_iva, cuit_cliente, codcliente, cliente,
                          condicion_iva, domicilio_cliente, condicion_vta, estado, subtotalFact, iva, total, formapago,
                          alicuota_iva, detalles_factura)
            # self.generar_factura_afip(serie, codfactura, fecha, codcliente, cliente, estado, subtotalFact, ivaFactura, totalFact, formapago, alicuota_iva)
        elif tipo == 'B':
            self.facturaB(tipo, fantasia_empresa, razon_social, serie, codfactura, fecha, cuit_empresa, iibb_empresa,
                          inicio_actividades, domicilio_empresa, categoria_iva, cuit_cliente, codcliente, cliente,
                          condicion_iva, domicilio_cliente, condicion_vta, estado, subtotalFact, iva, total, formapago,
                          alicuota_iva, detalles_factura)
        else:
            self.facturaC(tipo, fantasia_empresa, razon_social, serie, codfactura, fecha, cuit_empresa, iibb_empresa,
                          inicio_actividades, domicilio_empresa, categoria_iva, cuit_cliente, codcliente, cliente,
                          condicion_iva, domicilio_cliente, condicion_vta, estado, subtotalFact, iva, total, formapago,
                          alicuota_iva, detalles_factura)
        ##############################################################################################################################################################

        self.label_ingresar_msg2.setText('Factura ingresada correctamente')
        QMessageBox.information(self, "Factura Ingresada",
                                "La factura ha sido ingresada correctamente", )
        if self.comboBox_EstadoFactura.currentText() == 'COBRADA':
            tipo = 'COBRO'
            concepto = 'COBRO DE FACTURA N° ' + serie + '-' + codfactura
            tarjeta = '-'
            banco = '-'
            query_caja = "INSERT INTO caja (fecha, tipo, concepto, formapago, tarjeta, banco, total) VALUES(%s, %s, %s, %s, %s, %s, %s)"
            valores = (fecha, tipo, concepto, formapago, tarjeta, banco, total)
            with CursorDelPool() as cursor:
                cursor.execute(query_caja, valores)
            QMessageBox.information(self, "Cobro Registrado", "El cobro ha sido registrado correctamente", )

        self.lineEdit_clienteNvaFactura.clear()
        self.lineEdit_domclienteNvaFactura.clear()
        self.lineEdit_codclienteNvaFactura.clear()
        self.lineEdit_cuitclienteNvaFactura.clear()
        self.lineEdit_dniclienteNvaFactura_2.clear()
        self.lineEdit_telclienteNvaFactura.clear()
        self.lineEdit_emailclienteNvaFactura.clear()
        self.tableWidgetDetalleNvaFactura.clearContents()
        while self.tableWidgetDetalleNvaFactura.rowCount() > 0:
            self.tableWidgetDetalleNvaFactura.removeRow(0)

        if self.comboBox_EstadoFactura.currentText() == 'COBRADA':
            self.stackedWidget.setCurrentIndex(1)
        else:
            codpendiente = 10
            nombre = cliente
            importe = total
            pagos = 0
            saldo = total
            fechacancelada = "0"
            pendiente = Pendiente(codpendiente, serie, codfactura, estado, fecha, codcliente, nombre, importe, pagos,
                                  saldo, fechacancelada)

            # Insertar la factura en la base de datos
            pendientes_insertadas = PendientesDAO.insertar(pendiente)
            log.debug(f'Facturas insertadas: {pendientes_insertadas}')

        # Cerrar la ventana
        self.stackedWidget.setCurrentIndex(0)
        return

    def cancelar_factura(self):
        num_rows = self.tableWidgetDetalleNvaFactura.rowCount()
        for i in range(num_rows):
            self.tableWidgetDetalleNvaFactura.removeRow(0)
        self.lineEdit_clienteNvaFactura.clear()
        self.lineEdit_domclienteNvaFactura.clear()
        self.lineEdit_codclienteNvaFactura.clear()
        self.lineEdit_cuitclienteNvaFactura.clear()
        self.lineEdit_dniclienteNvaFactura_2.clear()
        self.lineEdit_telclienteNvaFactura.clear()
        self.lineEdit_emailclienteNvaFactura.clear()
        self.tableWidgetDetalleNvaFactura.clearContents()
        self.label_subtotal_factura.clear()
        self.label_iva_factura.clear()
        self.label_total_Nva_factura.clear()
        return

    def buscar_fact_pendiente(self):
        campo = 'ENVIO'
        pendientes = FacturaDAO.buscar_factura_pendiente(campo)
        if pendientes not in []:
            self.tableWidget_facturaspendientesentrega.setRowCount(len(pendientes))
            for i, pendiente in enumerate(pendientes):
                self.tableWidget_facturaspendientesentrega.setItem(i, 0,
                                                                   QtWidgets.QTableWidgetItem(str(pendiente.serie)))
                self.tableWidget_facturaspendientesentrega.setItem(i, 1, QtWidgets.QTableWidgetItem(
                    str(pendiente.codfactura)))
                self.tableWidget_facturaspendientesentrega.setItem(i, 2,
                                                                   QtWidgets.QTableWidgetItem(str(pendiente.tipo)))
                self.tableWidget_facturaspendientesentrega.setItem(i, 3,
                                                                   QtWidgets.QTableWidgetItem(str(pendiente.fecha)))
                self.tableWidget_facturaspendientesentrega.setItem(i, 4, QtWidgets.QTableWidgetItem(pendiente.estado))
                self.tableWidget_facturaspendientesentrega.setItem(i, 5,
                                                                   QtWidgets.QTableWidgetItem(str(pendiente.subtotal)))
                self.tableWidget_facturaspendientesentrega.setItem(i, 6, QtWidgets.QTableWidgetItem(str(pendiente.iva)))
                self.tableWidget_facturaspendientesentrega.setItem(i, 7,
                                                                   QtWidgets.QTableWidgetItem(str(pendiente.total)))
                self.tableWidget_facturaspendientesentrega.setItem(i, 8,
                                                                   QtWidgets.QTableWidgetItem(str(pendiente.formapago)))
                self.tableWidget_facturaspendientesentrega.resizeColumnsToContents()
                self.tableWidget_facturaspendientesentrega.resizeRowsToContents()
            return

    def buscar_fact_cobrar(self):
        campo1 = 'PENDIENTE'
        # campo2 = 'CHEQUE'
        pendientes = FacturaDAO.buscar_factura_cobrar(campo1)
        self.tableWidget_facturasImpagas.setRowCount(len(pendientes))
        for i, pendiente in enumerate(pendientes):
            self.tableWidget_facturasImpagas.setItem(i, 0, QtWidgets.QTableWidgetItem(str(pendiente.serie)))
            self.tableWidget_facturasImpagas.setItem(i, 1, QtWidgets.QTableWidgetItem(str(pendiente.codfactura)))
            self.tableWidget_facturasImpagas.setItem(i, 2, QtWidgets.QTableWidgetItem(str(pendiente.tipo)))
            self.tableWidget_facturasImpagas.setItem(i, 3, QtWidgets.QTableWidgetItem(str(pendiente.fecha)))
            self.tableWidget_facturasImpagas.setItem(i, 4, QtWidgets.QTableWidgetItem(pendiente.estado))
            self.tableWidget_facturasImpagas.setItem(i, 5, QtWidgets.QTableWidgetItem(str(pendiente.subtotal)))
            self.tableWidget_facturasImpagas.setItem(i, 6, QtWidgets.QTableWidgetItem(str(pendiente.iva)))
            self.tableWidget_facturasImpagas.setItem(i, 7, QtWidgets.QTableWidgetItem(str(pendiente.total)))
            self.tableWidget_facturasImpagas.setItem(i, 8, QtWidgets.QTableWidgetItem(str(pendiente.formapago)))
            self.tableWidget_facturasImpagas.resizeColumnsToContents()
            self.tableWidget_facturaspendientesentrega.resizeRowsToContents()

        # ######################################################################
        # pendientes_json = [registro.__dict__ for registro in pendientes]
        #
        # # Guardar los artículos en un archivo JSON
        # with open('pendientes.json', 'w') as f:
        #     json.dump(pendientes_json, f)
        # #####################################################################
        return

    ######################################################################

    #####################################################################
    def seleccionar_factura_cliente(self):
        self.tablaArticulosFacturaCliente.clearContents()
        row = self.tablaClientes.currentRow()
        codcliente = int(self.tablaClientes.item(row, 0).text())
        nombre = self.tablaClientes.item(row, 2).text()
        facturas = FacturaDAO.seleccionar_factura_cliente(codcliente, nombre)
        self.tablaFacturasCliente.setRowCount(len(facturas))
        for i, factura in enumerate(facturas):
            self.tablaFacturasCliente.setItem(i, 0, QtWidgets.QTableWidgetItem(str(factura.serie)))
            self.tablaFacturasCliente.setItem(i, 1, QtWidgets.QTableWidgetItem(str(factura.codfactura)))
            self.tablaFacturasCliente.setItem(i, 2, QtWidgets.QTableWidgetItem(str(factura.tipo)))
            self.tablaFacturasCliente.setItem(i, 3, QtWidgets.QTableWidgetItem(str(factura.fecha)))
            self.tablaFacturasCliente.setItem(i, 4, QtWidgets.QTableWidgetItem(str(factura.codcliente)))
            self.tablaFacturasCliente.setItem(i, 5, QtWidgets.QTableWidgetItem(str(factura.cliente)))
            self.tablaFacturasCliente.setItem(i, 6, QtWidgets.QTableWidgetItem(str(factura.estado)))
            self.tablaFacturasCliente.setItem(i, 7, QtWidgets.QTableWidgetItem(str(factura.subtotal)))
            self.tablaFacturasCliente.setItem(i, 8, QtWidgets.QTableWidgetItem(str(factura.iva)))
            self.tablaFacturasCliente.setItem(i, 9, QtWidgets.QTableWidgetItem(str(factura.total)))
            self.tablaFacturasCliente.setItem(i, 10, QtWidgets.QTableWidgetItem(str(factura.formapago)))
            self.tablaFacturasCliente.resizeColumnsToContents()
            self.tablaFacturasCliente.resizeRowsToContents()
            log.debug(factura)
        # Funciones.fx_cargarTablaX(detalles, self.tableWidget_detalleultimasFacturas_2, limpiaTabla=True)
        # self.tableWidget_detalleultimasFacturas_2.resizeColumnsToContents()
        # self.tableWidget_detalleultimasFacturas_2.resizeRowsToContents()
        log.debug(facturas)

    def seleccionar_detalle_factura_cliente(self):

        row = self.tablaFacturasCliente.currentRow()
        serie = int(self.tablaFacturasCliente.item(row, 0).text())
        codfactura = self.tablaFacturasCliente.item(row, 1).text()
        detalles = detalleFacturaDAO.seleccionar_detalle_factura_cliente(serie, codfactura)
        self.tablaArticulosFacturaCliente.setRowCount(len(detalles))
        for i, detalle in enumerate(detalles):
            self.tablaArticulosFacturaCliente.setItem(i, 0, QtWidgets.QTableWidgetItem(str(detalle.serie)))
            self.tablaArticulosFacturaCliente.setItem(i, 1, QtWidgets.QTableWidgetItem(str(detalle.codfactura)))
            self.tablaArticulosFacturaCliente.setItem(i, 2, QtWidgets.QTableWidgetItem(str(detalle.tipo)))
            self.tablaArticulosFacturaCliente.setItem(i, 3, QtWidgets.QTableWidgetItem(str(detalle.codarticulo)))
            self.tablaArticulosFacturaCliente.setItem(i, 4, QtWidgets.QTableWidgetItem(str(detalle.descripcion)))
            self.tablaArticulosFacturaCliente.setItem(i, 5, QtWidgets.QTableWidgetItem(str(detalle.cantidad)))
            self.tablaArticulosFacturaCliente.setItem(i, 6, QtWidgets.QTableWidgetItem(str(detalle.precioventa)))
            self.tablaArticulosFacturaCliente.setItem(i, 7, QtWidgets.QTableWidgetItem(str(detalle.importe)))
            self.tablaArticulosFacturaCliente.setItem(i, 8, QtWidgets.QTableWidgetItem(str(detalle.iva)))
            self.tablaArticulosFacturaCliente.resizeColumnsToContents()
            self.tablaArticulosFacturaCliente.resizeRowsToContents()
            log.debug(detalles)
        # Funciones.fx_cargarTablaX(detalles, self.tableWidget_detalleultimasFacturas_2, limpiaTabla=True)
        # self.tableWidget_detalleultimasFacturas_2.resizeColumnsToContents()
        # self.tableWidget_detalleultimasFacturas_2.resizeRowsToContents()
        log.debug(detalles)

    def cobrar_factura_cliente(self):
        # self.lineEdit_ImporteCobrarFactura.clear()
        if not self.tablaFacturasCliente.selectedItems():
            QMessageBox.information(self, "Seleccione una Factura",
                                    "Debe seleccionar una Factura para poder continuar", )
            return
        row = self.tablaFacturasCliente.currentRow()
        serie = int(self.tablaFacturasCliente.item(row, 0).text())
        codfactura = self.tablaFacturasCliente.item(row, 1).text()
        codcliente = self.tablaFacturasCliente.item(row, 4).text()
        if self.tablaFacturasCliente.item(row, 6).text() != 'PENDIENTE':
            QMessageBox.information(self, "La Factura no se puede cobrar ",
                                    "La factura ya ha sido cancelada previamente, no se encuentra pendiente de pago", )
            return

        facturas = FacturaDAO.cobrar_factura_cliente(serie, codfactura, codcliente)

        query_pendientes = "SELECT * FROM pendientes WHERE codfactura = %s"
        valor2 = (codfactura,)
        with CursorDelPool() as cursor:
            cursor.execute(query_pendientes, valor2)
            registros = cursor.fetchall()
            pendientes = []
            for registro in registros:
                pendiente = Pendiente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                      registro[6], registro[7], registro[8], registro[9], registro[10])
                pendientes.append(pendiente)
                # self.lineEdit_clienteCobrarFactura.setText(pendientes[0].nombre)
                # self.lineEdit_codclienteCobrarFactura.setText(pendientes[0].codcliente)
                # self.lineEdit_serieNvaFactura_2.setText(pendientes[0].serie)
                # self.lineEdit_numeroNvaFactura_2.setText(pendientes[0].codfactura)
                # self.lineEdit_fechaNvaFactura_2.setText(pendientes[0].fecha)
                ##########################################################################################################
                self.lineEdit_SaldoCobrarFactura.setText(str(float(pendientes[0].saldo)))
                self.lineEdit_ImporteCobrarFactura.setText(str(float(pendientes[0].saldo)))
                self.lineEdit_PagosCobrarFactura.setText(str(float(pendientes[0].pagos)))
                # self.lineEdit_fechaCobrarFactura.setText(pendientes[0].fechacancelada)
        ##########################################################################################################
        # return pendientes

        self.stackedWidget.setCurrentIndex(8)

        # Obtener la fecha y hora actual
        now = datetime.now()

        # Convertir la fecha y hora a una cadena de texto en español
        now_str = now.strftime('%d/%m/%Y, %H:%M:%S')

        # Establecer el texto del QLineEdit
        self.lineEdit_fechaCobrarFactura.setText(now_str)
        self.lineEdit_fechaCobrarFactura.setReadOnly(True)
        print(facturas)
        self.tablaCobrarFacturasCliente.setRowCount(len(facturas))
        for i, factura in enumerate(facturas):
            self.tablaCobrarFacturasCliente.setItem(i, 0, QtWidgets.QTableWidgetItem(str(factura.serie)))
            self.tablaCobrarFacturasCliente.setItem(i, 1, QtWidgets.QTableWidgetItem(str(factura.codfactura)))
            self.tablaCobrarFacturasCliente.setItem(i, 2, QtWidgets.QTableWidgetItem(str(factura.tipo)))
            self.tablaCobrarFacturasCliente.setItem(i, 3, QtWidgets.QTableWidgetItem(str(factura.fecha)))
            self.tablaCobrarFacturasCliente.setItem(i, 4, QtWidgets.QTableWidgetItem(str(factura.codcliente)))
            self.tablaCobrarFacturasCliente.setItem(i, 5, QtWidgets.QTableWidgetItem(str(factura.cliente)))
            self.tablaCobrarFacturasCliente.setItem(i, 6, QtWidgets.QTableWidgetItem(str(factura.estado)))
            self.tablaCobrarFacturasCliente.setItem(i, 7, QtWidgets.QTableWidgetItem(str(factura.subtotal)))
            self.tablaCobrarFacturasCliente.setItem(i, 8, QtWidgets.QTableWidgetItem(str(factura.iva)))
            self.tablaCobrarFacturasCliente.setItem(i, 9, QtWidgets.QTableWidgetItem(str(factura.total)))
            self.tablaCobrarFacturasCliente.setItem(i, 10, QtWidgets.QTableWidgetItem(str(factura.formapago)))
            self.tablaCobrarFacturasCliente.resizeColumnsToContents()
            self.tablaCobrarFacturasCliente.resizeRowsToContents()
            log.debug(factura)

        # Funciones.fx_cargarTablaX(detalles, self.tableWidget_detalleultimasFacturas_2, limpiaTabla=True)
        # self.tableWidget_detalleultimasFacturas_2.resizeColumnsToContents()
        # self.tableWidget_detalleultimasFacturas_2.resizeRowsToContents()
        log.debug(facturas)

        item = self.tablaCobrarFacturasCliente.item(0, 5)
        if item is not None:
            self.lineEdit_clienteCobrarFactura.setText(item.text())
        else:
            # Handle the case where the item does not exist
            # For example, you might want to clear the line edit or show an error message
            self.lineEdit_clienteCobrarFactura.clear()
        # self.lineEdit_clienteCobrarFactura.setText(self.tablaCobrarFacturasCliente.item(0, 5).text())
        self.lineEdit_codclienteCobrarFactura.setText(self.tablaCobrarFacturasCliente.item(0, 4).text())
        self.lineEdit_serieNvaFactura_2.setText(self.tablaCobrarFacturasCliente.item(0, 0).text())
        self.lineEdit_numeroNvaFactura_2.setText(self.tablaCobrarFacturasCliente.item(0, 1).text())
        self.lineEdit_fechaNvaFactura_2.setText(self.tablaCobrarFacturasCliente.item(0, 3).text())
        self.lineEdit_SaldoCobrarFactura.setText(self.tablaCobrarFacturasCliente.item(0, 9).text())

        cliente = self.tablaCobrarFacturasCliente.item(0, 4).text()
        with CursorDelPool() as cursor:
            # query = f"SELECT * FROM clientes WHERE codcliente = %s ORDER BY codigo ASC"
            query = f"SELECT * FROM clientes WHERE codigo = {cliente} ORDER BY codigo ASC"
            # cursor.execute(query, (f'%{cliente}%'))
            cursor.execute(query, (cliente,))
            registros = cursor.fetchall()
            clientes = []
            for registro in registros:
                cliente = Cliente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                  registro[12], registro[13], registro[14])
                clientes.append(cliente)
                self.lineEdit_dniclienteCobrarFactura.setText(clientes[0].dni)
                self.lineEdit_telclienteCobrarFactura.setText(clientes[0].telefono)
                self.lineEdit_emailclienteCobrarFactura.setText(clientes[0].email)
                self.lineEdit_IvaclienteCobraraFactura.setText(clientes[0].condiva)
                self.lineEdit_domclienteCobrarFactura.setText(clientes[0].direccion)
                self.lineEdit_cuitclienteCobrarFactura.setText(clientes[0].cuit)
            return clientes

    def seleccionar_detalle_factura_cobrar_cliente(self):
        row = self.tablaCobrarFacturasCliente.currentRow()
        serie = int(self.tablaCobrarFacturasCliente.item(row, 0).text())
        codfactura = self.tablaCobrarFacturasCliente.item(row, 1).text()
        detalles = detalleFacturaDAO.seleccionar_detalle_factura_cliente(serie, codfactura)
        self.tablaDetalleCobrarFacturaCliente.setRowCount(len(detalles))
        for i, detalle in enumerate(detalles):
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 0, QtWidgets.QTableWidgetItem(str(detalle.serie)))
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 1, QtWidgets.QTableWidgetItem(str(detalle.codfactura)))
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 2, QtWidgets.QTableWidgetItem(str(detalle.tipo)))
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 3, QtWidgets.QTableWidgetItem(str(detalle.codarticulo)))
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 4, QtWidgets.QTableWidgetItem(str(detalle.descripcion)))
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 5, QtWidgets.QTableWidgetItem(str(detalle.cantidad)))
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 6, QtWidgets.QTableWidgetItem(str(detalle.precioventa)))
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 7, QtWidgets.QTableWidgetItem(str(detalle.importe)))
            self.tablaDetalleCobrarFacturaCliente.setItem(i, 8, QtWidgets.QTableWidgetItem(str(detalle.iva)))
            self.tablaDetalleCobrarFacturaCliente.resizeColumnsToContents()
            self.tablaDetalleCobrarFacturaCliente.resizeRowsToContents()
            log.debug(detalles)
        # Funciones.fx_cargarTablaX(detalles, self.tableWidget_detalleultimasFacturas_2, limpiaTabla=True)
        # self.tableWidget_detalleultimasFacturas_2.resizeColumnsToContents()
        # self.tableWidget_detalleultimasFacturas_2.resizeRowsToContents()
        log.debug(detalles)

    def cobrar_factura_cliente_facturacion(self):
        self.lineEdit_ImporteCobrarFactura.clear()
        row = self.tableWidget_facturasImpagas.currentRow()
        serie = int(self.tableWidget_facturasImpagas.item(row, 0).text())
        codfactura = self.tableWidget_facturasImpagas.item(row, 1).text()
        # codcliente = self.tableWidget_facturasImpagas.item(row, 4).text()
        if self.tableWidget_facturasImpagas.item(row, 4).text() != 'PENDIENTE':
            QMessageBox.information(self, "La Factura no se puede cobrar ",
                                    "La factura ya ha sido cancelada previamente, no está pendiente de pago", )
            return

        facturas = FacturaDAO.cobrar_factura_cliente1(serie, codfactura)

        query_pendientes = "SELECT * FROM pendientes WHERE codfactura = %s"
        valor2 = (codfactura,)
        with CursorDelPool() as cursor:
            cursor.execute(query_pendientes, valor2)
            registros = cursor.fetchall()
            pendientes = []
            for registro in registros:
                pendiente = Pendiente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                      registro[6], registro[7], registro[8], registro[9], registro[10])
                pendientes.append(pendiente)
                # self.lineEdit_clienteCobrarFactura.setText(pendientes[0].nombre)
                # self.lineEdit_codclienteCobrarFactura.setText(pendientes[0].codcliente)
                # self.lineEdit_serieNvaFactura_2.setText(pendientes[0].serie)
                # self.lineEdit_numeroNvaFactura_2.setText(pendientes[0].codfactura)
                # self.lineEdit_fechaNvaFactura_2.setText(pendientes[0].fecha)
                ##########################################################################################################
                self.lineEdit_SaldoCobrarFactura.setText(str(float(pendientes[0].saldo)))
                self.lineEdit_ImporteCobrarFactura.setText(str(float(pendientes[0].saldo)))
                self.lineEdit_PagosCobrarFactura.setText(str(float(pendientes[0].pagos)))
                total = float(pendientes[0].saldo)
                pagos = float(pendientes[0].pagos)
                saldo = total - pagos
                # self.lineEdit_fechaCobrarFactura.setText(pendientes[0].fechacancelada)
                # self.lineEdit_ImporteCobrarFactura.setText(str(saldo))
        ##########################################################################################################
        # return pendientes

        self.stackedWidget.setCurrentIndex(8)

        # Obtener la fecha y hora actual
        now = datetime.now()

        # Convertir la fecha y hora a una cadena de texto en español
        now_str = now.strftime('%d/%m/%Y, %H:%M:%S')

        # Establecer el texto del QLineEdit
        self.lineEdit_fechaCobrarFactura.setText(now_str)
        self.lineEdit_fechaCobrarFactura.setReadOnly(True)

        self.tablaCobrarFacturasCliente.setRowCount(len(facturas))
        for i, factura in enumerate(facturas):
            self.tablaCobrarFacturasCliente.setItem(i, 0, QtWidgets.QTableWidgetItem(str(factura.serie)))
            self.tablaCobrarFacturasCliente.setItem(i, 1, QtWidgets.QTableWidgetItem(str(factura.codfactura)))
            self.tablaCobrarFacturasCliente.setItem(i, 2, QtWidgets.QTableWidgetItem(str(factura.tipo)))
            self.tablaCobrarFacturasCliente.setItem(i, 3, QtWidgets.QTableWidgetItem(str(factura.fecha)))
            self.tablaCobrarFacturasCliente.setItem(i, 4, QtWidgets.QTableWidgetItem(str(factura.codcliente)))
            self.tablaCobrarFacturasCliente.setItem(i, 5, QtWidgets.QTableWidgetItem(str(factura.cliente)))
            self.tablaCobrarFacturasCliente.setItem(i, 6, QtWidgets.QTableWidgetItem(str(factura.estado)))
            self.tablaCobrarFacturasCliente.setItem(i, 7, QtWidgets.QTableWidgetItem(str(factura.subtotal)))
            self.tablaCobrarFacturasCliente.setItem(i, 8, QtWidgets.QTableWidgetItem(str(factura.iva)))
            self.tablaCobrarFacturasCliente.setItem(i, 9, QtWidgets.QTableWidgetItem(str(factura.total)))
            self.tablaCobrarFacturasCliente.setItem(i, 10, QtWidgets.QTableWidgetItem(str(factura.formapago)))
            self.tablaCobrarFacturasCliente.resizeColumnsToContents()
            self.tablaCobrarFacturasCliente.resizeRowsToContents()
            log.debug(factura)
            # Funciones.fx_cargarTablaX(detalles, self.tableWidget_detalleultimasFacturas_2, limpiaTabla=True)
            # self.tableWidget_detalleultimasFacturas_2.resizeColumnsToContents()
            # self.tableWidget_detalleultimasFacturas_2.resizeRowsToContents()
        log.debug(facturas)

        item = self.tablaCobrarFacturasCliente.item(0, 5)
        if item is not None:
            self.lineEdit_clienteCobrarFactura.setText(item.text())
        else:
            # Handle the case where the item does not exist
            # For example, you might want to clear the line edit or show an error message
            self.lineEdit_clienteCobrarFactura.clear()
        # self.lineEdit_clienteCobrarFactura.setText(self.tablaCobrarFacturasCliente.item(0, 5).text())
        self.lineEdit_codclienteCobrarFactura.setText(self.tablaCobrarFacturasCliente.item(0, 4).text())
        self.lineEdit_serieNvaFactura_2.setText(self.tablaCobrarFacturasCliente.item(0, 0).text())
        self.lineEdit_numeroNvaFactura_2.setText(self.tablaCobrarFacturasCliente.item(0, 1).text())
        self.lineEdit_fechaNvaFactura_2.setText(self.tablaCobrarFacturasCliente.item(0, 3).text())
        #####################################################################################################

        self.lineEdit_SaldoCobrarFactura.setText(self.tablaCobrarFacturasCliente.item(0, 9).text())
        ######################################################################################################
        cliente = self.tablaCobrarFacturasCliente.item(0, 4).text()
        with CursorDelPool() as cursor:
            # query = f"SELECT * FROM clientes WHERE codcliente = %s ORDER BY codigo ASC"
            query = f"SELECT * FROM clientes WHERE codigo = {cliente} ORDER BY codigo ASC"
            # cursor.execute(query, (f'%{cliente}%'))
            cursor.execute(query, (cliente,))
            registros = cursor.fetchall()
            clientes = []
            for registro in registros:
                cliente = Cliente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                  registro[6], registro[7], registro[8], registro[9], registro[10], registro[11],
                                  registro[12], registro[13], registro[14])
                clientes.append(cliente)
                self.lineEdit_dniclienteCobrarFactura.setText(clientes[0].dni)
                self.lineEdit_telclienteCobrarFactura.setText(clientes[0].telefono)
                self.lineEdit_emailclienteCobrarFactura.setText(clientes[0].email)
                self.lineEdit_IvaclienteCobraraFactura.setText(clientes[0].condiva)
                self.lineEdit_domclienteCobrarFactura.setText(clientes[0].direccion)
                self.lineEdit_cuitclienteCobrarFactura.setText(clientes[0].cuit)
            return clientes

    def cobrar_factura_cliente_pendiente(self):
        pagos_text = self.lineEdit_PagosCobrarFactura.text()
        pagos = float(pagos_text) if pagos_text else 0.0
        importe = float(self.lineEdit_ImporteCobrarFactura.text())
        pagos = pagos + importe
        saldo = float(self.lineEdit_SaldoCobrarFactura.text()) - pagos
        estado = ''
        fechacancelada = self.lineEdit_fechaCobrarFactura.text()
        print(f"Valor de saldo: {saldo}")
        if saldo == 0:
            estado = 'CANCELADA'
            fechacancelada = self.lineEdit_fechaCobrarFactura.text()
            query_modificar_factura = "UPDATE facturas SET estado = %s WHERE codfactura = %s"
            valor = (estado, self.lineEdit_numeroNvaFactura_2.text())
            with CursorDelPool() as cursor:
                cursor.execute(query_modificar_factura, valor)
            QMessageBox.information(self, "Factura Cobrada", "La factura ha sido cobrada correctamente", )
        else:
            estado = 'PENDIENTE'
            fechacancelada = '-'
            query_modificar_factura = "UPDATE facturas SET estado = %s WHERE codfactura = %s"
            valor = (estado, self.lineEdit_numeroNvaFactura_2.text())
            with CursorDelPool() as cursor:
                cursor.execute(query_modificar_factura, valor)
            QMessageBox.information(self, "Factura Cobrada", "La factura ha sido cobrada parcialmente", )
        query_cobro = "UPDATE pendientes SET estado = %s, importe = %s, pagos = %s, saldo = %s, fechacancelada = %s WHERE codfactura = %s"
        valores = (estado, importe, pagos, saldo, fechacancelada, self.lineEdit_numeroNvaFactura_2.text())
        with CursorDelPool() as cursor:
            cursor.execute(query_cobro, valores)
            self.stackedWidget.setCurrentIndex(1)
            # return

        #######################################################################
        #
        #   CARGAMOS EL REGISTRO DEL PAGO EN LA TABLA CAJA
        ###################################################################
        fecha_cobro = self.lineEdit_fechaCobrarFactura.text()
        tipo = 'COBRO'
        serie = self.lineEdit_serieNvaFactura_2.text()
        codfactura = self.lineEdit_numeroNvaFactura_2.text()
        concepto = 'Factura N° ' + str(serie) + '-' + str(codfactura)
        formapago = self.comboBox_FormaPagoCobrarFactura.currentText()
        tarjeta = self.comboBox_TarjetaCobrarFactura.currentText()
        banco = self.comboBox_BancoCobrarFactura.currentText()
        total = importe

        query_caja = "INSERT INTO caja (fecha, tipo, concepto, formapago, tarjeta, banco, total) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        valores = (fecha_cobro, tipo, concepto, formapago, tarjeta, banco, total)
        with CursorDelPool() as cursor:
            cursor.execute(query_caja, valores)
        QMessageBox.information(self, "Cobro Registrado", "El cobro ha sido registrado correctamente", )
        #####################################################################

        ################################################################################
        self.generar_recibo()

    ################################################################################

    def on_combobox_changed(self):
        row = self.tableWidget_facturasImpagas.currentRow()
        codfactura = self.tableWidget_facturasImpagas.item(row, 1).text()

        query_pendientes = "SELECT * FROM pendientes WHERE codfactura = %s"
        valor2 = (codfactura,)
        saldo_pendiente = 0
        importe_pagar = 0
        with CursorDelPool() as cursor:
            cursor.execute(query_pendientes, valor2)
            registros = cursor.fetchall()
            pendientes = []
            for registro in registros:
                pendiente = Pendiente(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                      registro[6], registro[7], registro[8], registro[9], registro[10])
                pendientes.append(pendiente)
                # self.lineEdit_clienteCobrarFactura.setText(pendientes[0].nombre)
                # self.lineEdit_codclienteCobrarFactura.setText(pendientes[0].codcliente)
                # self.lineEdit_serieNvaFactura_2.setText(pendientes[0].serie)
                # self.lineEdit_numeroNvaFactura_2.setText(pendientes[0].codfactura)
                # self.lineEdit_fechaNvaFactura_2.setText(pendientes[0].fecha)
                ####################################################################################################
                saldo_pendientes = self.tablaCobrarFacturasCliente.item(0, 9).text()
                # self.lineEdit_SaldoCobrarFactura.setText(str(float(saldo_pendientes)
                importe_pagar = float(saldo_pendientes) - float(pendientes[0].pagos)
                self.lineEdit_ImporteCobrarFactura.setText(str(importe_pagar))
                # self.lineEdit_ImporteCobrarFactura.setText(str(float(pendientes[0].saldo)))
                self.lineEdit_PagosCobrarFactura.setText(str(float(pendientes[0].pagos)))
                # self.lineEdit_fechaCobrarFactura.setText(pendientes[0].fechacancelada)
        ####################################################################################################
        # return pendientes
        if not self.lineEdit_PagosCobrarFactura.text() == 0.0 or self.lineEdit_PagosCobrarFactura.text() == '':
            if self.comboBox_TpoPagoCobrarFactura.currentText() == 'TOTAL':
                # saldo_pendiente = float(self.tablaCobrarFacturasCliente.item(0, 9).text()) - float(self.lineEdit_PagosCobrarFactura.text())
                pagos_cobrar_factura_text = self.lineEdit_PagosCobrarFactura.text()
                pagos_cobrar_factura = float(pagos_cobrar_factura_text) if pagos_cobrar_factura_text else 0.0
                saldo_pendiente = float(self.tablaCobrarFacturasCliente.item(0, 9).text()) - pagos_cobrar_factura
                # saldo1 = float(pendientes[0].saldo) - float(pendientes[0].pagos)

                # self.lineEdit_ImporteCobrarFactura.setText(str(float(pendientes[0].saldo)))
                self.lineEdit_ImporteCobrarFactura.setText(str(saldo_pendiente))
                # self.lineEdit_ImporteCobrarFactura.setText(self.tablaCobrarFacturasCliente.item(0, 9).text())
                # self.lineEdit_ImporteCobrarFactura.setText("{:.2f}".format(saldo1))
                self.lineEdit_ImporteCobrarFactura.setReadOnly(True)
                # self.lineEdit_PagosCobrarFactura.setText(str(float(0)))
                self.lineEdit_PagosCobrarFactura.setReadOnly(True)
            elif self.comboBox_TpoPagoCobrarFactura.currentText() == 'PARCIAL':
                self.lineEdit_ImporteCobrarFactura.setText('')
                self.lineEdit_ImporteCobrarFactura.setReadOnly(False)
                # self.lineEdit_PagosCobrarFactura.setText(str(float(0)))
                self.lineEdit_ImporteCobrarFactura.setFocus()  # Poner el foco en el lineEdit
                if self.lineEdit_ImporteCobrarFactura.text() == '':
                    QMessageBox.information(self, "Importe Incorrecto",
                                            "No se ha ingresado un importe. Por favor, ingrese un importe.")
                    self.lineEdit_ImporteCobrarFactura.setFocus()

                else:
                    self.lineEdit_PagosCobrarFactura.setReadOnly(True)
                    self.lineEdit_SaldoCobrarFactura.setReadOnly(True)
                    importe1 = self.lineEdit_ImporteCobrarFactura.text()
                    saldo2 = str(float(pendientes[0].saldo) - float(self.lineEdit_ImporteCobrarFactura.text()))
                    while float(self.lineEdit_ImporteCobrarFactura.text()) > float(saldo2):
                        QMessageBox.information(self, "Importe Incorrecto",
                                                "El importe ingresado es mayor al saldo pendiente. Por favor, ingrese un importe menor o igual al saldo pendiente.")
                        self.lineEdit_ImporteCobrarFactura.setFocus()

                # else:
                #     QMessageBox.information(self, "Importe Incorrecto",
                #                             "No se ha ingresado un importe. Por favor, ingrese un importe.")
                self.lineEdit_ImporteCobrarFactura.setFocus()
            else:
                pagos_text = self.lineEdit_PagosCobrarFactura.text()
                pagos = float(pagos_text) if pagos_text else 0.0
                # resto = float("{:.2f}".format(float(self.lineEdit_SaldoCobrarFactura.text()) - pagos))
                # saldo_pendiente = float(self.tablaCobrarFacturasCliente.item(0, 9).text()) - float(
                pagos_cobrar_factura_text = self.lineEdit_PagosCobrarFactura.text()
                pagos_cobrar_factura = float(pagos_cobrar_factura_text) if pagos_cobrar_factura_text else 0.0
                saldo_pendiente = float(self.tablaCobrarFacturasCliente.item(0, 9).text()) - pagos_cobrar_factura
                self.lineEdit_PagosCobrarFactura.text()
                self.lineEdit_ImporteCobrarFactura.setText(str(saldo_pendiente))
                # self.lineEdit_ImporteCobrarFactura.setText(str(float(pendientes[0].saldo)))
                self.lineEdit_SaldoCobrarFactura.setReadOnly(True)

    ########################################################################
    #
    #          PARTE DEL MODULO CAJA
    #
    ########################################################################
    def modulo_caja(self):
        self.stackedWidget.setCurrentIndex(9)
        self.lineEdit_fechaCobrarFactura_4.setReadOnly(True)
        # Obtener la fecha y hora actual
        now = datetime.now()
        # Convertir la fecha y hora a una cadena de texto en español
        now_str = now.strftime('%d/%m/%Y, %H:%M:%S')

        registros = CajaDAO.seleccionar_cobro()
        self.tableWidget_ultimosCobros.setRowCount(len(registros))
        for i, detalle in enumerate(registros):
            self.tableWidget_ultimosCobros.setItem(i, 0, QtWidgets.QTableWidgetItem(str(detalle.id)))
            self.tableWidget_ultimosCobros.setItem(i, 1, QtWidgets.QTableWidgetItem(str(detalle.fecha)))
            self.tableWidget_ultimosCobros.setItem(i, 2, QtWidgets.QTableWidgetItem(str(detalle.tipo)))
            self.tableWidget_ultimosCobros.setItem(i, 3, QtWidgets.QTableWidgetItem(str(detalle.concepto)))
            self.tableWidget_ultimosCobros.setItem(i, 4, QtWidgets.QTableWidgetItem(str(detalle.formapago)))
            self.tableWidget_ultimosCobros.setItem(i, 5, QtWidgets.QTableWidgetItem(str(detalle.tarjeta)))
            self.tableWidget_ultimosCobros.setItem(i, 6, QtWidgets.QTableWidgetItem(str(detalle.banco)))
            self.tableWidget_ultimosCobros.setItem(i, 7, QtWidgets.QTableWidgetItem(str(detalle.total)))
            self.tableWidget_ultimosCobros.resizeColumnsToContents()
            self.tableWidget_ultimosCobros.resizeRowsToContents()
            log.debug(registros)

        cobros_json = [registro.__dict__ for registro in registros]

        # Guardar los artículos en un archivo JSON
        with open('caja.json', 'w') as f:
            json.dump(cobros_json, f)

        registros = CajaDAO.seleccionar_pago()
        self.tableWidget_ultimosCobros_2.setRowCount(len(registros))
        for i, detalle in enumerate(registros):
            self.tableWidget_ultimosCobros_2.setItem(i, 0, QtWidgets.QTableWidgetItem(str(detalle.id)))
            self.tableWidget_ultimosCobros_2.setItem(i, 1, QtWidgets.QTableWidgetItem(str(detalle.fecha)))
            self.tableWidget_ultimosCobros_2.setItem(i, 2, QtWidgets.QTableWidgetItem(str(detalle.tipo)))
            self.tableWidget_ultimosCobros_2.setItem(i, 3, QtWidgets.QTableWidgetItem(str(detalle.concepto)))
            self.tableWidget_ultimosCobros_2.setItem(i, 4, QtWidgets.QTableWidgetItem(str(detalle.formapago)))
            self.tableWidget_ultimosCobros_2.setItem(i, 5, QtWidgets.QTableWidgetItem(str(detalle.tarjeta)))
            self.tableWidget_ultimosCobros_2.setItem(i, 6, QtWidgets.QTableWidgetItem(str(detalle.banco)))
            self.tableWidget_ultimosCobros_2.setItem(i, 7, QtWidgets.QTableWidgetItem(str(detalle.total)))
            self.tableWidget_ultimosCobros_2.resizeColumnsToContents()
            self.tableWidget_ultimosCobros_2.resizeRowsToContents()
            log.debug(registros)

        pagos_json = [registro.__dict__ for registro in registros]

        # Guardar los artículos en un archivo JSON
        with open('caja.json', 'w') as f:
            json.dump(pagos_json, f)

        # Establecer el texto del QLineEdit
        self.lineEdit_fechaCobrarFactura_4.setText(now_str)
        self.lineEdit_fechaCobrarFactura_4.setReadOnly(True)

    def nuevo_cobro(self):
        fecha_cobro = self.lineEdit_fechaCobrarFactura_4.text()
        tipo = self.comboBox_TpoPagoNvoCobro.currentText()
        concepto = self.lineEdit_ConceptoNvoCobro.text()
        formapago = self.comboBox_FormaPagoNvoCobro.currentText()
        tarjeta = self.comboBox_TarjetaCobrarFactura_4.currentText()
        banco = self.comboBox_BancoCobrarFactura_4.currentText()
        total = self.lineEdit_ImporteNvoCobro.text()

        query_caja = "INSERT INTO caja (fecha, tipo, concepto, formapago, tarjeta, banco, total) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        valores = (fecha_cobro, tipo, concepto, formapago, tarjeta, banco, total)
        with CursorDelPool() as cursor:
            cursor.execute(query_caja, valores)
        QMessageBox.information(self, "Cobro Registrado", "El cobro ha sido registrado correctamente", )

        self.lineEdit_ConceptoNvoCobro.setText('')
        self.lineEdit_ImporteNvoCobro.setText('')
        self.lineEdit_ConceptoNvoCobro.setText('')

    def combo_formapago_change(self):
        if self.comboBox_FormaPagoNvoCobro.currentText() == 'CONTADO':
            self.comboBox_TarjetaCobrarFactura_4.setDisabled(True)
            self.comboBox_TarjetaCobrarFactura_4.setText = '-'
            self.comboBox_BancoCobrarFactura_4.setDisabled(True)
            self.comboBox_BancoCobrarFactura_4.setText = '-'
            self.lineEdit_ConceptoNvoCobro.setFocus()
        elif self.comboBox_FormaPagoNvoCobro.currentText() == 'TARJ. CREDITO':
            self.comboBox_TarjetaCobrarFactura_4.setDisabled(False)
            self.comboBox_TarjetaCobrarFactura_4.setFocus()
            self.comboBox_BancoCobrarFactura_4.setDisabled(False)
        elif self.comboBox_FormaPagoNvoCobro.currentText() == 'DEBITO':
            self.comboBox_TarjetaCobrarFactura_4.setDisabled(False)
            self.comboBox_TarjetaCobrarFactura_4.setFocus()
            self.comboBox_BancoCobrarFactura_4.setDisabled(False)
        elif self.comboBox_FormaPagoNvoCobro.currentText() == 'CHEQUE':
            self.comboBox_TarjetaCobrarFactura_4.setDisabled(True)
            self.comboBox_TarjetaCobrarFactura_4.setText = '-'
            self.comboBox_BancoCobrarFactura_4.setDisabled(True)
            self.comboBox_BancoCobrarFactura_4.setText = '-'
            self.lineEdit_ConceptoNvoCobro.setFocus()
        elif self.comboBox_FormaPagoNvoCobro.currentText() == 'TRANSFERENCIA':
            self.comboBox_TarjetaCobrarFactura_4.setDisabled(True)
            self.comboBox_TarjetaCobrarFactura_4.setText = '-'
            self.comboBox_BancoCobrarFactura_4.setDisabled(False)
            self.comboBox_BancoCobrarFactura_4.setFocus()
        elif self.comboBox_FormaPagoNvoCobro.currentText() == 'MERCADOPAGO':
            self.comboBox_TarjetaCobrarFactura_4.setDisabled(True)
            self.comboBox_TarjetaCobrarFactura_4.setText = '-'
            self.comboBox_BancoCobrarFactura_4.setDisabled(True)
            self.comboBox_BancoCobrarFactura_4.setText = '-'
            self.lineEdit_ConceptoNvoCobro.setFocus()
        else:
            self.comboBox_TarjetaCobrarFactura_4.setFocus()

    def cancelar_nuevo_cobro(self):
        self.lineEdit_ConceptoNvoCobro.setText('')
        self.lineEdit_ImporteNvoCobro.setText('')
        self.lineEdit_ConceptoNvoCobro.setText('')

    ########################################################################
    #
    #                       MODIFICAR VALORES DE ARTICULOS
    ########################################################################

    def modulo_stock_mod_precio(self):
        if self.comboBox_ModificarPrecio.currentText() == 'AUMENTAR %':
            if self.comboBox_ModificarPrecio_2.currentText() == 'SOLO ARTICULO':
                if not self.tabla_Articulos.selectedItems():
                    QMessageBox.information(self, "Seleccionar Articulo a Modificar",
                                            "Tiene que seleccionar un Articulo para poder continuar", )
                    return
                else:
                    if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        valor = float(self.lineEdit_ValorModificarPrecio.text())

                        if valor <= 0:
                            QMessageBox.information(self, "Valor Incorrecto",
                                                    "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                            self.lineEdit_ValorModificarPrecio.setFocus()
                        else:
                            valor = valor / 100
                            valor += 1
                            query_mod_valor = "UPDATE articulos SET precio_venta = precio_venta * %s  WHERE codigo = %s"
                            # Obtén la fila seleccionada
                            row = self.tabla_Articulos.currentRow()
                            # Obtén el valor de la columna 0 para la fila seleccionada
                            valor2 = (valor, self.tabla_Articulos.item(row, 0).text())
                            with CursorDelPool() as cursor:
                                cursor.execute(query_mod_valor, valor2)
                            QMessageBox.information(self, "Cambios Registrados",
                                                    "Los cambios han sido registrados correctamente", )

            elif self.comboBox_ModificarPrecio_2.currentText() == 'CATEGORIA':
                if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarPrecio.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarPrecio.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        valor = valor / 100
                        valor += 1
                        query_mod_valor = "UPDATE articulos SET precio_venta = precio_venta * %s WHERE categoria = %s"
                        # Obtén la fila seleccionada
                        # row = self.tabla_Articulos.currentRow()
                        # Obtén el valor de la columna 0 para la fila seleccionada
                        categoria_seleccionada = self.lineEdit.text()
                        valor2 = (valor, categoria_seleccionada)
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, valor2)
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )


            elif self.comboBox_ModificarPrecio_2.currentText() == 'TODOS':
                if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarPrecio.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarPrecio.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        valor = valor / 100
                        valor += 1
                        query_mod_valor = "UPDATE articulos SET precio_venta = precio_venta * %s"
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, (valor,))
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )

        if self.comboBox_ModificarPrecio.currentText() == 'DISMINUIR %':
            if self.comboBox_ModificarPrecio_2.currentText() == 'SOLO ARTICULO':
                if not self.tabla_Articulos.selectedItems():
                    QMessageBox.information(self, "Seleccionar Articulo a Modificar",
                                            "Tiene que seleccionar un Articulo para poder continuar", )
                    return
                else:
                    if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        valor = float(self.lineEdit_ValorModificarPrecio.text())
                        if valor <= 0:
                            QMessageBox.information(self, "Valor Incorrecto",
                                                    "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                            self.lineEdit_ValorModificarPrecio.setFocus()
                        else:
                            valor_nuevo = valor / 100
                            query_mod_valor = "UPDATE articulos SET precio_venta = precio_venta - ((precio_venta * %s) / 100) WHERE codigo = %s"
                            # Obtén la fila seleccionada
                            row = self.tabla_Articulos.currentRow()
                            # Obtén el valor de la columna 0 para la fila seleccionada
                            valor2 = (valor, self.tabla_Articulos.item(row, 0).text())
                            with CursorDelPool() as cursor:
                                cursor.execute(query_mod_valor, valor2)
                            QMessageBox.information(self, "Cambios Registrados",
                                                    "Los cambios han sido registrados correctamente", )

            if self.comboBox_ModificarPrecio_2.currentText() == 'CATEGORIA':
                if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarPrecio.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarPrecio.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        # valor = valor / 100
                        # valor += 1
                        query_mod_valor = "UPDATE articulos SET precio_venta = precio_venta - ((precio_venta * %s) / 100) WHERE categoria = %s"
                        # Obtén la fila seleccionada
                        # row = self.tabla_Articulos.currentRow()
                        # Obtén el valor de la columna 0 para la fila seleccionada
                        categoria_seleccionada = self.lineEdit.text()
                        valor2 = (valor, categoria_seleccionada)
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, valor2)
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )

            elif self.comboBox_ModificarPrecio_2.currentText() == 'TODOS':
                if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarPrecio.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarPrecio.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        valor_nuevo = valor / 100
                        query_mod_valor = "UPDATE articulos SET precio_venta = precio_venta - ((precio_venta * %s) / 100)"
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, (valor,))
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )

        if self.comboBox_ModificarPrecio.currentText() == '+ VALOR FIJO':
            if self.comboBox_ModificarPrecio_2.currentText() == 'SOLO ARTICULO':
                if not self.tabla_Articulos.selectedItems():
                    QMessageBox.information(self, "Seleccionar Articulo a Modificar",
                                            "Tiene que seleccionar un Articulo para poder continuar", )
                    return
                else:
                    if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        valor = float(self.lineEdit_ValorModificarPrecio.text())
                        if valor <= 0:
                            QMessageBox.information(self, "Valor Incorrecto",
                                                    "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                            self.lineEdit_ValorModificarPrecio.setFocus()
                        else:
                            query_mod_valor = "UPDATE articulos SET precio_venta = (precio_venta::numeric + %s)::money WHERE codigo = %s"
                            # Obtén la fila seleccionada
                            row = self.tabla_Articulos.currentRow()
                            # Obtén el valor de la columna 0 para la fila seleccionada
                            valor2 = (valor, self.tabla_Articulos.item(row, 0).text())
                            with CursorDelPool() as cursor:
                                cursor.execute(query_mod_valor, valor2)
                            QMessageBox.information(self, "Cambios Registrados",
                                                    "Los cambios han sido registrados correctamente", )

            if self.comboBox_ModificarPrecio_2.currentText() == 'CATEGORIA':
                if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarPrecio.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarPrecio.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        # valor = valor / 100
                        # valor += 1
                        query_mod_valor = "UPDATE articulos SET precio_venta = (precio_venta::numeric + %s)::money WHERE categoria = %s"
                        # Obtén la fila seleccionada
                        # row = self.tabla_Articulos.currentRow()
                        # Obtén el valor de la columna 0 para la fila seleccionada
                        categoria_seleccionada = self.lineEdit.text()
                        valor2 = (valor, categoria_seleccionada)
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, valor2)
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )


            elif self.comboBox_ModificarPrecio_2.currentText() == 'TODOS':
                if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarPrecio.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarPrecio.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        query_mod_valor = "UPDATE articulos SET precio_venta = (precio_venta::numeric + %s)::money"
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, (valor,))
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )

        if self.comboBox_ModificarPrecio.currentText() == '- VALOR FIJO':
            if self.comboBox_ModificarPrecio_2.currentText() == 'SOLO ARTICULO':
                if not self.tabla_Articulos.selectedItems():
                    QMessageBox.information(self, "Seleccionar Articulo a Modificar",
                                            "Tiene que seleccionar un Articulo para poder continuar", )
                    return
                else:
                    if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        valor = float(self.lineEdit_ValorModificarPrecio.text())
                        if valor <= 0:
                            QMessageBox.information(self, "Valor Incorrecto",
                                                    "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                            self.lineEdit_ValorModificarPrecio.setFocus()
                        else:
                            query_mod_valor = "UPDATE articulos SET precio_venta = (precio_venta::numeric - %s)::money WHERE codigo = %s"
                            # Obtén la fila seleccionada
                            row = self.tabla_Articulos.currentRow()
                            # Obtén el valor de la columna 0 para la fila seleccionada
                            valor2 = (valor, self.tabla_Articulos.item(row, 0).text())
                            with CursorDelPool() as cursor:
                                cursor.execute(query_mod_valor, valor2)
                            QMessageBox.information(self, "Cambios Registrados",
                                                    "Los cambios han sido registrados correctamente", )

            if self.comboBox_ModificarPrecio_2.currentText() == 'CATEGORIA':
                if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarPrecio.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarPrecio.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        # valor = valor / 100
                        # valor += 1
                        query_mod_valor = "UPDATE articulos SET precio_venta = (precio_venta::numeric - %s)::money WHERE categoria = %s"
                        # Obtén la fila seleccionada
                        # row = self.tabla_Articulos.currentRow()
                        # Obtén el valor de la columna 0 para la fila seleccionada
                        categoria_seleccionada = self.lineEdit.text()
                        valor2 = (valor, categoria_seleccionada)
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, valor2)
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )

            elif self.comboBox_ModificarPrecio_2.currentText() == 'TODOS':
                if self.lineEdit_ValorModificarPrecio.text() == '' or self.lineEdit_ValorModificarPrecio.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarPrecio.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarPrecio.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarPrecio.setFocus()
                    else:
                        query_mod_valor = "UPDATE articulos SET precio_venta = (precio_venta::numeric - %s)::money"
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, (valor,))
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )

    def modulo_stock_mod_stock(self):
        if self.comboBox_ModificarStock.currentText() == 'AUMENTAR':
            if self.comboBox_ModificarStock_2.currentText() == 'SOLO ARTICULO':
                if not self.tabla_Articulos.selectedItems():
                    QMessageBox.information(self, "Seleccionar Articulo a Modificar",
                                            "Tiene que seleccionar un Articulo para poder continuar", )
                    return
                else:
                    if self.lineEdit_ValorModificarStock.text() == '' or self.lineEdit_ValorModificarStock.text() == 'Nuevo Valor':
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarStock.setFocus()
                    else:
                        valor = float(self.lineEdit_ValorModificarStock.text())
                        if valor <= 0:
                            QMessageBox.information(self, "Valor Incorrecto",
                                                    "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                            self.lineEdit_ValorModificarStock.setFocus()
                        else:
                            query_mod_valor = "UPDATE articulos SET stock = stock + %s WHERE codigo = %s"
                            # Obtén la fila seleccionada
                            row = self.tabla_Articulos.currentRow()
                            # Obtén el valor de la columna 0 para la fila seleccionada
                            valor2 = (valor, self.tabla_Articulos.item(row, 0).text())
                            with CursorDelPool() as cursor:
                                cursor.execute(query_mod_valor, valor2)
                            QMessageBox.information(self, "Cambios Registrados",
                                                    "Los cambios han sido registrados correctamente", )

            else:
                if self.lineEdit_ValorModificarStock.text() == '' or self.lineEdit_ValorModificarStock.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarStock.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarStock.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarStock.setFocus()
                    else:
                        query_mod_valor = "UPDATE articulos SET stock = stock + %s"
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, (valor,))
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )

        if self.comboBox_ModificarStock.currentText() == 'DISMINUIR':
            if self.comboBox_ModificarStock_2.currentText() == 'SOLO ARTICULO':
                if not self.tabla_Articulos.selectedItems():
                    QMessageBox.information(self, "Seleccionar Articulo a Modificar",
                                            "Tiene que seleccionar un Articulo para poder continuar", )
                    return
                else:
                    if self.lineEdit_ValorModificarStock.text() == '' or self.lineEdit_ValorModificarStock.text() == 'Nuevo Valor':
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarStock.setFocus()
                    else:
                        valor = float(self.lineEdit_ValorModificarStock.text())
                        if valor <= 0:
                            QMessageBox.information(self, "Valor Incorrecto",
                                                    "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                            self.lineEdit_ValorModificarStock.setFocus()
                        else:
                            query_mod_valor = "UPDATE articulos SET stock = stock - %s WHERE codigo = %s"
                            # Obtén la fila seleccionada
                            row = self.tabla_Articulos.currentRow()
                            # Obtén el valor de la columna 0 para la fila seleccionada
                            valor2 = (valor, self.tabla_Articulos.item(row, 0).text())
                            with CursorDelPool() as cursor:
                                cursor.execute(query_mod_valor, valor2)
                            QMessageBox.information(self, "Cambios Registrados",
                                                    "Los cambios han sido registrados correctamente", )

            else:
                if self.lineEdit_ValorModificarStock.text() == '' or self.lineEdit_ValorModificarStock.text() == 'Nuevo Valor':
                    QMessageBox.information(self, "Valor Incorrecto",
                                            "No se ha ingresado un valor. Por favor, ingrese un valor mayor a 0.")
                    self.lineEdit_ValorModificarStock.setFocus()
                else:
                    valor = float(self.lineEdit_ValorModificarStock.text())
                    if valor <= 0:
                        QMessageBox.information(self, "Valor Incorrecto",
                                                "El valor ingresado es incorrecto. Por favor, ingrese un valor mayor a 0.")
                        self.lineEdit_ValorModificarStock.setFocus()
                    else:
                        query_mod_valor = "UPDATE articulos SET stock = stock - %s"
                        with CursorDelPool() as cursor:
                            cursor.execute(query_mod_valor, (valor,))
                        QMessageBox.information(self, "Cambios Registrados",
                                                "Los cambios han sido registrados correctamente", )

    def combo_mod_precio_change(self):
        if self.comboBox_ModificarPrecio_2.currentText() == 'CATEGORIA':

            categorias = ArticuloDAO.seleccionar_categorias()

            # Crear un modelo para la lista
            model = QtGui.QStandardItemModel()

            # Añadir las categorías al modelo
            for categoria in categorias:
                item = QtGui.QStandardItem(categoria)
                model.appendRow(item)

            # Asignar el modelo a la lista
            self.ui.listView_categorias.setModel(model)
            self.ui.bt_SeleccionarCategoria.clicked.connect(self.seleccionada_categoria)
            self.ui.bt_AgregarCategoria.clicked.connect(self.mostrar_agregar_categoria)
            self.dialogo_categoria.exec_()

    ###############################################################
    #
    #           SECCION CTA. CTE.
    #
    ###############################################################

    def modulo_ctacte_cliente(self):
        self.stackedWidget.setCurrentIndex(10)
        self.lineEdit_fechaCobrarFactura_5.setText(datetime.now().strftime('%d/%m/%Y, %H:%M:%S'))

        clientes = ClienteDAO.seleccionar()
        self.tablaClientes_3.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            self.tablaClientes_3.setItem(i, 0, QtWidgets.QTableWidgetItem(str(cliente.codigo)))
            self.tablaClientes_3.setItem(i, 1, QtWidgets.QTableWidgetItem(cliente.nombre))
            self.tablaClientes_3.setItem(i, 2, QtWidgets.QTableWidgetItem(cliente.apellido))
            self.tablaClientes_3.setItem(i, 3, QtWidgets.QTableWidgetItem(cliente.dni))
            self.tablaClientes_3.setItem(i, 4, QtWidgets.QTableWidgetItem(cliente.empresa))
            self.tablaClientes_3.setItem(i, 5, QtWidgets.QTableWidgetItem(cliente.cuit))
            self.tablaClientes_3.setItem(i, 6, QtWidgets.QTableWidgetItem(cliente.telefono))
            self.tablaClientes_3.setItem(i, 7, QtWidgets.QTableWidgetItem(cliente.email))
            self.tablaClientes_3.setItem(i, 8, QtWidgets.QTableWidgetItem(cliente.direccion))
            self.tablaClientes_3.setItem(i, 9, QtWidgets.QTableWidgetItem(cliente.numero))
            self.tablaClientes_3.setItem(i, 10, QtWidgets.QTableWidgetItem(cliente.localidad))
            self.tablaClientes_3.setItem(i, 11, QtWidgets.QTableWidgetItem(cliente.provincia))
            self.tablaClientes_3.setItem(i, 12, QtWidgets.QTableWidgetItem(cliente.pais))
            self.tablaClientes_3.setItem(i, 13, QtWidgets.QTableWidgetItem(cliente.observaciones))
            self.tablaClientes_3.setItem(i, 14, QtWidgets.QTableWidgetItem(cliente.condiva))
            log.debug(cliente)

        last_row_cliente = self.tablaClientes_3.rowCount() - 1
        last_codigo_cliente = self.tablaClientes.item(last_row_cliente, 0)
        self.tablaClientes_3.resizeColumnsToContents()
        self.tablaClientes_3.resizeRowsToContents()

    def buscar_cliente_ctacte(self):
        campo1 = 'nombre'
        campo2 = 'apellido'
        campo3 = 'empresa'
        valor = str(self.lineEdit_BuscarClienteCtaCte.text())
        clientes = ClienteDAO.buscar_cliente(campo1, campo2, campo3, valor)
        self.tablaClientes_3.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            self.tablaClientes_3.setItem(i, 0, QtWidgets.QTableWidgetItem(str(cliente.codigo)))
            self.tablaClientes_3.setItem(i, 1, QtWidgets.QTableWidgetItem(cliente.nombre))
            self.tablaClientes_3.setItem(i, 2, QtWidgets.QTableWidgetItem(cliente.apellido))
            self.tablaClientes_3.setItem(i, 3, QtWidgets.QTableWidgetItem(cliente._dni))
            self.tablaClientes_3.setItem(i, 4, QtWidgets.QTableWidgetItem(cliente.empresa))
            self.tablaClientes_3.setItem(i, 5, QtWidgets.QTableWidgetItem(cliente._cuit))
            self.tablaClientes_3.setItem(i, 6, QtWidgets.QTableWidgetItem(cliente._telefono))
            self.tablaClientes_3.setItem(i, 7, QtWidgets.QTableWidgetItem(cliente._email))
            self.tablaClientes_3.setItem(i, 8, QtWidgets.QTableWidgetItem(cliente._direccion))
            self.tablaClientes_3.setItem(i, 9, QtWidgets.QTableWidgetItem(cliente._numero))
            self.tablaClientes_3.setItem(i, 10, QtWidgets.QTableWidgetItem(cliente._localidad))
            self.tablaClientes_3.setItem(i, 11, QtWidgets.QTableWidgetItem(cliente._provincia))
            self.tablaClientes_3.setItem(i, 12, QtWidgets.QTableWidgetItem(cliente._pais))
            self.tablaClientes_3.setItem(i, 13, QtWidgets.QTableWidgetItem(cliente._observaciones))
            self.tablaClientes_3.setItem(i, 13, QtWidgets.QTableWidgetItem(cliente._condiva))
            self.tablaClientes_3.resizeColumnsToContents()
            self.tablaClientes_3.resizeRowsToContents()
            log.debug(cliente)

    def seleccionar_factura_cliente_ctacte(self):
        # self.tablaClientes_3.clearContents()
        self.lineEdit_CobradoCtaCte.setText('')
        row = self.tablaClientes_3.currentRow()
        codcliente = int(self.tablaClientes_3.item(row, 0).text())
        nombre = self.tablaClientes_3.item(row, 2).text()
        volumen_compras = 0
        cant_compras = 0
        total_fact = 0
        fecha_ultCompra = ""

        facturas = FacturaDAO.seleccionar_factura_cliente(codcliente, nombre)
        self.tablaFacturasCliente_3.setRowCount(len(facturas))
        for i, factura in enumerate(facturas):
            self.tablaFacturasCliente_3.setItem(i, 0, QtWidgets.QTableWidgetItem(str(factura.serie)))
            self.tablaFacturasCliente_3.setItem(i, 1, QtWidgets.QTableWidgetItem(str(factura.codfactura)))
            self.tablaFacturasCliente_3.setItem(i, 2, QtWidgets.QTableWidgetItem(str(factura.tipo)))
            self.tablaFacturasCliente_3.setItem(i, 3, QtWidgets.QTableWidgetItem(str(factura.fecha)))
            self.tablaFacturasCliente_3.setItem(i, 4, QtWidgets.QTableWidgetItem(str(factura.codcliente)))
            self.tablaFacturasCliente_3.setItem(i, 5, QtWidgets.QTableWidgetItem(str(factura.cliente)))
            self.tablaFacturasCliente_3.setItem(i, 6, QtWidgets.QTableWidgetItem(str(factura.estado)))
            self.tablaFacturasCliente_3.setItem(i, 7, QtWidgets.QTableWidgetItem(str(factura.subtotal)))
            self.tablaFacturasCliente_3.setItem(i, 8, QtWidgets.QTableWidgetItem(str(factura.iva)))
            self.tablaFacturasCliente_3.setItem(i, 9, QtWidgets.QTableWidgetItem(str(factura.total)))
            self.tablaFacturasCliente_3.setItem(i, 10, QtWidgets.QTableWidgetItem(str(factura.formapago)))
            volumen_compras += round(float(factura.total), 2)
            cant_compras += 1
            self.tablaFacturasCliente_3.resizeColumnsToContents()
            self.tablaFacturasCliente_3.resizeRowsToContents()
            log.debug(factura)
        item = self.tablaFacturasCliente_3.item(0, 3)
        if item is not None:  # Check if the item is not None (i.e., the cell is not empty)
            fecha_ultCompra = item.text()
        else:
            fecha_ultCompra = ""  # or any default value
        self.lineEdit_VolumenCompras.setText("{:.2f}".format(volumen_compras))
        self.lineEdit_CantidadComprasCtaCte.setText(str(cant_compras))
        self.lineEdit_UltCompraCtaCte.setText(str(fecha_ultCompra))

        row = self.tablaClientes_3.currentRow()
        codcliente = self.tablaClientes_3.item(row, 0).text()
        nombre = self.tablaClientes_3.item(row, 1).text()

        suma_saldos_pendientes = 0
        suma_pagos = 0
        # Consulta a la tabla 'pendientes' para obtener los saldos pendientes del cliente seleccionado
        pendientes = PendientesDAO.buscar_pendiente_cliente(codcliente)

        # Suma los saldos pendientes
        for pendiente in pendientes:
            if pendiente.estado == 'PENDIENTE':
                suma_saldos_pendientes = sum(pendiente.saldo for pendiente in pendientes)
                self.lineEdit_SaldoPendienteCtaCte.setText("{:.2f}".format(suma_saldos_pendientes))


            else:

                self.lineEdit_SaldoPendienteCtaCte.setText('0')
            suma_pagos = sum(pendiente.pagos for pendiente in pendientes)
        item = self.tablaFacturasCliente_3.item(row, 6)
        print(item)
        # if item is not None:  # Check if the item is not None (i.e., the cell is not empty)
        #     if item == 'COBRADA':
        # suma_pagos = 0
        #         suma_pagos = self.tablaFacturasCliente_3.item(row, 9).text()
        #         self.lineEdit_CobradoCtaCte.setText("{:.2f}".format(float(suma_pagos)))
        # else:
        #
        #     self.lineEdit_CobradoCtaCte.setText("{:.2f}".format(suma_pagos))
        if suma_saldos_pendientes == 0:
            self.lineEdit_CobradoCtaCte.setText(str(float(volumen_compras)))
            self.lineEdit_SaldoPendienteCtaCte.setText('0')
            suma_pagos = volumen_compras
        else:
            self.lineEdit_CobradoCtaCte.setText(str(float(suma_pagos)))
        # resto_pagar= suma_saldos_pendientes - suma_pagos
        ##############################################################################################
        ##############################################################################################

        resto_pagar = volumen_compras - float(suma_pagos)

        self.lineEdit_ImporteNvoCobro_2.setText(str(resto_pagar))
        self.lineEdit_SaldoPendienteCtaCte.setText(str(resto_pagar))
        # Funciones.fx_cargarTablaX(detalles, self.tableWidget_detalleultimasFacturas_2, limpiaTabla=True)
        # self.tableWidget_detalleultimasFacturas_2.resizeColumnsToContents()
        # self.tableWidget_detalleultimasFacturas_2.resizeRowsToContents()
        log.debug(facturas)

    def seleccionar_pendiente_cliente_ctacte(self):
        row = self.tablaFacturasCliente_3.currentRow()
        serie = int(self.tablaFacturasCliente_3.item(row, 0).text())
        codfactura = int(self.tablaFacturasCliente_3.item(row, 1).text())
        codcliente = int(self.tablaFacturasCliente_3.item(row, 4).text())

        if self.tablaFacturasCliente_3.item(row, 6).text() != 'PENDIENTE':
            QMessageBox.information(self, "La Factura no se puede cobrar ",
                                    "La factura ya ha sido cancelada previamente, no se encuentra pendiente de pago", )
            return
        else:
            facturas = FacturaDAO.cobrar_factura_cliente(serie, codfactura, codcliente)
            # pendientes = PendientesDAO.buscar_pendiente_ctacte(self, serie, codfactura, codcliente)
            pendientes_dao = PendientesDAO()
            pendientes = pendientes_dao.buscar_pendiente_ctacte(serie, codfactura, codcliente)
            if facturas:  # Check if facturas is not empty

                saldo_ctacte = round(pendientes[0].saldo, 2)
                self.lineEdit_ImporteNvoCobro_2.setText("{:.2f}".format(saldo_ctacte))
                # self.lineEdit_ImporteNvoCobro_2.setText(str(facturas[0].total))
                self.lineEdit_ConceptoNvoCobro_2.setText(
                    'Cobro de Factura Nro. ' + str(facturas[0].serie) + "-" + str(facturas[0].codfactura))
            else:
                # Handle the case where facturas is empty
                # For example, you might want to clear the line edits or show an error message
                self.lineEdit_ImporteNvoCobro_2.clear()
                self.lineEdit_ConceptoNvoCobro_2.clear()

    def cobrar_factura_pendiente_ctacte(self):
        if not self.tablaFacturasCliente_3.selectedItems():
            QMessageBox.information(self, "Seleccionar Factura a Cobrar",
                                    "Tiene que seleccionar una Factura para poder continuar", )
            return
        if self.lineEdit_ImporteNvoCobro_2.text() == '' or self.lineEdit_ImporteNvoCobro_2.text() == '0' or self.lineEdit_ImporteNvoCobro_2.text() == '0.0':
            QMessageBox.information(self, "La Factura no se puede cobrar",
                                    "El cliente no tiene saldo pendiente por cobrar o ya ha sido cancelado")
            return

        importe = float(self.lineEdit_ImporteNvoCobro_2.text())
        estado = ''
        fechacancelada = self.lineEdit_fechaCobrarFactura_5.text()
        estado = 'CANCELADA'
        fechacancelada = self.lineEdit_fechaCobrarFactura_5.text()
        row = self.tablaFacturasCliente_3.currentRow()
        serie = int(self.tablaFacturasCliente_3.item(row, 0).text())
        codfactura = int(self.tablaFacturasCliente_3.item(row, 1).text())
        codcliente = int(self.tablaFacturasCliente_3.item(row, 4).text())
        query_modificar_factura = "UPDATE facturas SET estado = %s WHERE codfactura = %s"
        valor = (estado, codfactura)
        with CursorDelPool() as cursor:
            cursor.execute(query_modificar_factura, valor)
        QMessageBox.information(self, "Factura Cobrada", "La factura ha sido cobrada correctamente", )
        pendientes_dao = PendientesDAO()
        pendientes = pendientes_dao.buscar_pendiente_ctacte(serie, codfactura, codcliente)
        pagos = pendientes[0].pagos + importe
        saldo = 0
        query_cobro = "UPDATE pendientes SET estado = %s, importe = %s, pagos = %s, saldo = %s, fechacancelada = %s WHERE codfactura = %s"
        valores = (estado, importe, pagos, saldo, fechacancelada, codfactura)
        with CursorDelPool() as cursor:
            cursor.execute(query_cobro, valores)
            # self.stackedWidget.setCurrentIndex(1)
            # return
        QMessageBox.information(self, "Cuenta Corriente Actualizada", "Se ha actualizado la cuenta del cliente", )
        self.nuevo_cobro_ctacte()

    def nuevo_cobro_ctacte(self):
        fecha_cobro = self.lineEdit_fechaCobrarFactura_5.text()
        tipo = self.comboBox_TpoPagoNvoCobro_2.currentText()
        concepto = self.lineEdit_ConceptoNvoCobro_2.text()
        formapago = self.comboBox_FormaPagoNvoCobro_2.currentText()
        tarjeta = self.comboBox_TarjetaCobrarFactura_5.currentText()
        banco = self.comboBox_BancoCobrarFactura_5.currentText()
        total = self.lineEdit_ImporteNvoCobro_2.text()

        query_caja = "INSERT INTO caja (fecha, tipo, concepto, formapago, tarjeta, banco, total) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        valores = (fecha_cobro, tipo, concepto, formapago, tarjeta, banco, total)
        with CursorDelPool() as cursor:
            cursor.execute(query_caja, valores)
        QMessageBox.information(self, "Cobro Registrado", "El cobro ha sido registrado correctamente", )

        self.lineEdit_ConceptoNvoCobro_2.setText('')
        self.lineEdit_ImporteNvoCobro_2.setText('')
        self.lineEdit_ConceptoNvoCobro.setText('')

    def generar_recibo(self):
        pass
        # # Obtener los datos necesarios
        # nombre_cliente = self.lineEdit_clienteCobrarFactura.text()
        # cantidad_pagada = self.lineEdit_ImporteCobrarFactura.text()
        # fecha_pago = datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        # numero_factura = self.lineEdit_serieNvaFactura_2.text() + "-" + self.lineEdit_numeroNvaFactura_2.text()
        #
        # # Formatear los datos en un formato de recibo
        # recibo = f"""
        # -------------------------------------------------------------
        # Recibo de Pago
        # -------------------------------------------------------------
        # Fecha: {fecha_pago}
        # Nombre del Cliente: {nombre_cliente}
        # Número de Factura: {numero_factura}
        # Cantidad Pagada: $ {cantidad_pagada}
        # -----------------------------------------------------------
        # Gracias por su pago!
        # """
        #
        # # Crear un objeto de canvas y especificar el nombre del archivo PDF
        # # Format the date and time to be used in a filename
        # fecha_pago_filename = datetime.now().strftime('%d_%m_%Y_%H-%M-%S')
        #
        # # Use the formatted date and time in the filename
        # c = canvas.Canvas(f"recibo{numero_factura}_{fecha_pago_filename}.pdf")
        #
        # # Dibujar el texto en el PDF
        # c.drawString(100, 750, recibo)
        #
        # # Guardar el PDF
        # c.save()
        #
        # # Mostrar, imprimir o guardar el recibo
        # print(
        #     recibo)  # Esto es solo un ejemplo, puedes optar por mostrarlo en la interfaz de usuario o guardarlo en un archivo

    def importar_proveedores(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar Proveedores", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Importar los proveedores
            # ProveedorDAO.importar_desde_excel(ruta_archivo)
            #
            # # Mostrar un mensaje de éxito
            # QMessageBox.information(self, "Proveedores Importados", "Los proveedores han sido importados correctamente", )
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText("¿Desea subir nuevos proveedores o actualizar los existentes desde Excel?")
            msgBox.setWindowTitle("Importar proveedores desde Excel")
            msgBox.setStandardButtons(QMessageBox.Cancel)
            buttonUpload = msgBox.addButton('Subir nuevos', QMessageBox.ActionRole)
            buttonUpdate = msgBox.addButton('Actualizar existentes', QMessageBox.ActionRole)

            msgBox.exec_()

            if msgBox.clickedButton() == buttonUpload:
                # Obtener la ruta del archivo seleccionado
                ruta_archivo, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar proveedores", "",
                                                                        "Archivos XLSX (*.xlsx);;Todos los archivos (*)")
                # Verificar si el usuario seleccionó un archivo
                if ruta_archivo:
                    # Importar los articulos
                    ProveedorDAO.importar_desde_excel(ruta_archivo)
                    # Mostrar un mensaje de éxito
                    QMessageBox.information(self, "Proveedores Importados",
                                            "Los proveedores han sido importados correctamente", )
            elif msgBox.clickedButton() == buttonUpdate:
                # Aquí debe llamar al método de actualización de ProveedorDAO
                # Asegúrese de tener la ruta del archivo y los datos necesarios para la actualización
                ProveedorDAO.actualizar_desde_excel(ruta_archivo)
                # Mostrar un mensaje de éxito
                QMessageBox.information(self, "Proveedores Actualizados",
                                        "Los proveedores han sido actualizados correctamente", )

    def importar_clientes(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar Clientes", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Importar los proveedores
            # ClienteDAO.importar_desde_excel(ruta_archivo)
            #
            # # Mostrar un mensaje de éxito
            # QMessageBox.information(self, "Clientes Importados", "Los clientes han sido importados correctamente", )
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText("¿Desea subir nuevos clientes o actualizar los existentes desde Excel?")
            msgBox.setWindowTitle("Importar clientes desde Excel")
            msgBox.setStandardButtons(QMessageBox.Cancel)
            buttonUpload = msgBox.addButton('Subir nuevos', QMessageBox.ActionRole)
            buttonUpdate = msgBox.addButton('Actualizar existentes', QMessageBox.ActionRole)

            msgBox.exec_()

            if msgBox.clickedButton() == buttonUpload:
                # Obtener la ruta del archivo seleccionado
                ruta_archivo, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar Clientes", "",
                                                                        "Archivos XLSX (*.xlsx);;Todos los archivos (*)")
                # Verificar si el usuario seleccionó un archivo
                if ruta_archivo:
                    # Importar los articulos
                    ClienteDAO.importar_desde_excel(ruta_archivo)
                    # Mostrar un mensaje de éxito
                    QMessageBox.information(self, "Clientes Importados",
                                            "Los clientes han sido importados correctamente", )
            elif msgBox.clickedButton() == buttonUpdate:
                # Aquí debe llamar al método de actualización de ClienteDAO
                # Asegúrese de tener la ruta del archivo y los datos necesarios para la actualización
                ClienteDAO.actualizar_desde_excel(ruta_archivo)
                # Mostrar un mensaje de éxito
                QMessageBox.information(self, "Clientes Actualizados",
                                        "Los clientes han sido actualizados correctamente", )

    def importar_articulos(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar Articulos", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        # if ruta_archivo:
        #     # Importar los articulos
        #     ArticuloDAO.importar_desde_excel(ruta_archivo)
        #
        #     # Mostrar un mensaje de éxito
        #     QMessageBox.information(self, "Artículos Importados", "Los artículos han sido importados correctamente", )
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("¿Desea subir nuevos productos o actualizar los existentes desde Excel?")
        msgBox.setWindowTitle("Importar productos desde Excel")
        msgBox.setStandardButtons(QMessageBox.Cancel)
        buttonUpload = msgBox.addButton('Subir nuevos', QMessageBox.ActionRole)
        buttonUpdate = msgBox.addButton('Actualizar existentes', QMessageBox.ActionRole)

        msgBox.exec_()

        if msgBox.clickedButton() == buttonUpload:
            # Obtener la ruta del archivo seleccionado
            ruta_archivo, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar Articulos", "",
                                                                    "Archivos XLSX (*.xlsx);;Todos los archivos (*)")
            # Verificar si el usuario seleccionó un archivo
            if ruta_archivo:
                # Importar los articulos
                ArticuloDAO.importar_desde_excel(ruta_archivo)
                # Mostrar un mensaje de éxito
                QMessageBox.information(self, "Artículos Importados",
                                        "Los artículos han sido importados correctamente", )
        elif msgBox.clickedButton() == buttonUpdate:
            # Aquí debe llamar al método de actualización de ArticuloDAO
            # Asegúrese de tener la ruta del archivo y los datos necesarios para la actualización
            ArticuloDAO.actualizar_desde_excel(ruta_archivo)
            # Mostrar un mensaje de éxito
            QMessageBox.information(self, "Artículos Actualizados",
                                    "Los artículos han sido actualizados correctamente", )

    def descargar_articulos(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Descargar Articulos", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Descargar los articulos
            ArticuloDAO.exportar_articulos(ruta_archivo)

        # Mostrar un mensaje de éxito
        QMessageBox.information(self, "Artículos Descargados", "Los artículos han sido descargados correctamente", )

    def descargar_clientes(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Descargar Clientes", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Descargar los clientes
            ClienteDAO.exportar_clientes(ruta_archivo)

        # Mostrar un mensaje de éxito
        QMessageBox.information(self, "Clientes Descargados", "Los clientes han sido descargados correctamente", )

    def descargar_proveedores(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Descargar Proveedores", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Descargar los proveedores
            ProveedorDAO.exportar_proveedores(ruta_archivo)

        # Mostrar un mensaje de éxito
        QMessageBox.information(self, "Proveedores Descargados", "Los proveedores han sido descargados correctamente", )

    def descargar_ultimos_cobros(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Descargar Ultimos Cobros Realizados", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Descargar los últimos cobros
            CajaDAO.exportar_cobros(ruta_archivo)

        # Mostrar un mensaje de éxito
        QMessageBox.information(self, "Últimos Cobros Descargados",
                                "Los últimos cobros han sido descargados correctamente", )

    def descargar_ultimos_pagos(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Descargar Ultimos Pagos Realizados", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Descargar los últimos pagos
            CajaDAO.exportar_pagos(ruta_archivo)

        # Mostrar un mensaje de éxito
        QMessageBox.information(self, "Últimos Pagos Descargados",
                                "Los últimos pagos han sido descargados correctamente", )

    def descargar_pendientes(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Descargar Facturas Pendientes Pago", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Descargar facturas pendientes pago
            PendientesDAO.exportar_pendientes(ruta_archivo)

        # Mostrar un mensaje de éxito
        QMessageBox.information(self, "Facturas Pendientes",
                                "Los facturas pendientes han sido descargadas correctamente", )

    def descargar_facturas(self):
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Descargar Facturas", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Descargar facturas
            FacturaDAO.exportar_facturas(ruta_archivo)

        # Mostrar un mensaje de éxito
        QMessageBox.information(self, "Facturas Descargadas", "Las facturas han sido descargadas correctamente", )

    def descargar_facturas_pendientes_entrega(self, campo1):
        campo1 = 'ENVIO'
        # Obtener la ruta del archivo seleccionado
        ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Descargar Facturas Pendientes de Entrega", "",
                                                                "Archivos XLSX (*.xlsx);;Todos los archivos (*)")

        # Verificar si el usuario seleccionó un archivo
        if ruta_archivo:
            # Descargar facturas pendientes entrega
            FacturaDAO.exportar_facturas_entrega(campo1, ruta_archivo)

        # Mostrar un mensaje de éxito
        QMessageBox.information(self, "Facturas Pendientes Entrega Descargadas",
                                "Las facturas sin entregar han sido descargadas correctamente", )

    def cambiar_datos_empresa(self):
        self.ui_ventana_empresa.lineEdit_razon_social_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_nombre_fantasia_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_cuit_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_categoria_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_iibb_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_inicio_actividades_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_domicilio_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_localidad_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_provincia_empresa.setReadOnly(False)
        self.ui_ventana_empresa.lineEdit_pais_empresa.setReadOnly(False)

    def modificar_datos_empresa(self):
        global bArray
        razonsocial = self.ui_ventana_empresa.lineEdit_razon_social_empresa.text()
        nombrefantasia = self.ui_ventana_empresa.lineEdit_nombre_fantasia_empresa.text()
        cuit = self.ui_ventana_empresa.lineEdit_cuit_empresa.text()
        categoria = self.ui_ventana_empresa.lineEdit_categoria_empresa.text()
        iibb = int(self.ui_ventana_empresa.lineEdit_iibb_empresa.text())
        inicioactividades = self.ui_ventana_empresa.lineEdit_inicio_actividades_empresa.text()
        domicilio = self.ui_ventana_empresa.lineEdit_domicilio_empresa.text()
        localidad = self.ui_ventana_empresa.lineEdit_localidad_empresa.text()
        provincia = self.ui_ventana_empresa.lineEdit_provincia_empresa.text()
        pais = self.ui_ventana_empresa.lineEdit_pais_empresa.text()
        direccion_completa_empresa = " , ".join([domicilio, localidad, provincia, pais])
        sucursales = 1  # Add this line if you don't have a field for sucursales in your UI

        # empresa = Empresa(razonsocial, nombrefantasia, cuit, categoria, iibb, inicioactividades, domicilio, localidad,
        #                  provincia, pais, bArray)
        # empresas_insertadas = EmpresaDAO.actualizar(empresa)
        query_actualizar = 'UPDATE empresa SET nombrefantasia=%s, cuit=%s, categoria=%s, iibb=%s, inicioactividades=%s, domicilio=%s, localidad=%s, provincia=%s, pais=%s, sucursales=%s WHERE razonsocial = %s'
        valores = (
        nombrefantasia, cuit, categoria, iibb, inicioactividades, domicilio, localidad, provincia, pais, sucursales,
        razonsocial)  # Use logo_bytes instead of bArray
        with CursorDelPool() as cursor:
            cursor.execute(query_actualizar, valores)
        # log.debug(f'Empresa actualizada: {empresas_insertadas}')
        self.label_ingresar_msg2.setText('Empresa ingresada correctamente')
        QMessageBox.information(self, "Empresa Actualizada",
                                "Los datos de la empresa han sido actualizados correctamente", )

        self.Ui_ventana_Datos_Empresa.close()

    def eliminar_datos_empresa(self):
        empresa = self.ui_ventana_empresa.lineEdit_razon_social_empresa.text()
        EmpresaDAO.eliminar(empresa)
        QMessageBox.information(self, "Datos Eliminados",
                                "Los datos de la empresa han sido eliminados correctamente", )

    def subir_foto_empresa(self):
        # Obtener la ruta de la imagen seleccionada
        ruta_imagen, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Subir Foto Empresa", "",
                                                               "Archivos de Imagen (*.jpg *.png *.jpeg)")

        # Verificar si el usuario seleccionó una imagen
        if ruta_imagen:
            # Subir la imagen
            # EmpresaDAO.subir_foto(ruta_imagen)
            pixmapImagen = QPixmap(ruta_imagen).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui_ventana_empresa.label_11.setPixmap(pixmapImagen)

            # Obtener la ruta del directorio del negocio
            basedir = os.path.dirname(__file__)
            ruta_directorio_negocio = os.path.join(basedir, 'Interfaz/Icons')

            # Crear el directorio si no existe
            if not os.path.exists(ruta_directorio_negocio):
                os.makedirs(ruta_directorio_negocio)

            # Crear la ruta completa del nuevo archivo de imagen
            # Aquí es donde cambiamos el nombre del archivo a "logo.png"
            ruta_nueva_imagen = os.path.join(ruta_directorio_negocio, "logo.png")

            # Copiar la imagen al directorio del negocio
            shutil.copy(ruta_imagen, ruta_nueva_imagen)
            # Mostrar un mensaje de éxito
            QMessageBox.information(self, "Imagen Subida", "La imagen ha sido subida correctamente", )

    #############################################################################################
    #                 PRESUPUESTOS
    #############################################################################################

    def modulo_presupuestos_nuevo(self):
        self.stackedWidget.setCurrentIndex(12)
        self.lineEdit_BuscarArticuloNvaFactura1_3.setFocus()
        self.lineEdit_BuscarArticuloNvaFactura1_3.setCursorPosition(0)

        # Obtener la fecha y hora actual
        now = datetime.now()

        # Convertir la fecha y hora a una cadena de texto en español
        now_str = now.strftime('%d/%m/%Y, %H:%M:%S')

        # Establecer el texto del QLineEdit
        self.lineEdit_fechaNvaFactura_5.setText(now_str)
        self.lineEdit_fechaNvaFactura_5.setReadOnly(True)

        ############################################
        #       LLENAR LOS DATOS DE LA FACTURA CON LOS DATOS DE LA EMPRESA DE LA BD#####3
        #
        ###########################################
        empresa = EmpresaDAO.seleccionar()
        if empresa:
            empresa = empresa[0]
            self.label_297.setText(empresa.razonsocial)
            self.label_308.setText(empresa.nombrefantasia)
            self.lineEdit_cuitNvaFactura_3.setText(str(empresa.cuit))
            # self.label_91.setText(empresa.categoria)
            # self.lineEdit_IIBBNvaFactura.setText(str(empresa.iibb))
            self.lineEdit_inicioActNvaFactura_4.setText(empresa.inicioactividades)

        else:
            # Handle the case when there are no empresas
            print("Primero debe cargar los datos de su empresa en Módulo Empresa para poder continuar.")
            return
        domicilio = empresa.domicilio
        localidad = empresa.localidad
        provincia = empresa.provincia
        pais = empresa.pais
        direccion_completa_empresa = " , ".join([domicilio, localidad, provincia, pais])
        # self.lineEdit_localidadNvaFactura.setText(empresa.localidad)
        self.label_304.setText(direccion_completa_empresa)
        ############################################################################################
        # CARGAMOS EL LOGO DE LA EMPRESA EN LA NUEVA FACTURA
        # Crear un QPixmap con la ruta de la imagen
        # self.factura_logo.clear()
        # Crear un QPixmap con la ruta de la imagen
        logo_pixmap = QPixmap('_internal/Interfaz/Icons/logo.png')

        # Establecer el tamaño del QLabel
        self.factura_logo_2.setFixedSize(100, 100)

        # Escalar el QPixmap al tamaño deseado
        logo_pixmap = logo_pixmap.scaled(self.factura_logo_2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Establecer el QPixmap en la QLabel
        self.factura_logo_2.setPixmap(logo_pixmap)

        # Mover la QLabel a la posición deseada
        self.factura_logo_2.move(70, 45)

        ###############################################################################

        self.lineEdit_serieNvaFactura.setText("1".zfill(5))

        query_NroPresupuesto = "SELECT DISTINCT ON (codpresupuesto) * FROM presupuestos ORDER BY codpresupuesto DESC"

        with CursorDelPool() as cursor:
            cursor.execute(query_NroPresupuesto)
            registros = cursor.fetchall()
            presupuestos = []
            for registro in registros:
                presupuesto = Presupuesto(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5],
                                          registro[6], registro[7])
                presupuestos.append(presupuesto)
            if presupuestos:
                self.lineEdit_numeroNvaFactura_5.setText(str(presupuestos[0].codpresupuesto + 1).zfill(8))
            else:
                self.lineEdit_numeroNvaFactura_5.setText("1".zfill(8))  # or handle the error as you see fit
            return presupuestos

    def seleccionar_cliente_nuevo_presupuesto(self):
        self.dialogo_agregar_cliente_factura.setMaximumSize(1029, 540)  # Ancho máximo 800, altura máxima 600
        self.dialogo_agregar_cliente_factura.setMinimumSize(1029, 540)  # Ancho mínimo 400, altura mínima 300

        # Obtener los clientes de la base de datos
        clientes = ClienteDAO.seleccionar()

        self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 0, QtWidgets.QTableWidgetItem(
                str(cliente.codigo)))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 1, QtWidgets.QTableWidgetItem(
                cliente.nombre))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 2, QtWidgets.QTableWidgetItem(
                cliente.apellido))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 3, QtWidgets.QTableWidgetItem(
                cliente.dni))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 4, QtWidgets.QTableWidgetItem(
                cliente.empresa))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(
                cliente.cuit))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(
                cliente.telefono))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(
                cliente.email))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 8, QtWidgets.QTableWidgetItem(
                cliente.direccion))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 9, QtWidgets.QTableWidgetItem(
                cliente.numero))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 10, QtWidgets.QTableWidgetItem(
                cliente.localidad))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 11, QtWidgets.QTableWidgetItem(
                cliente.provincia))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 12, QtWidgets.QTableWidgetItem(
                cliente.pais))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 13, QtWidgets.QTableWidgetItem(
                cliente.observaciones))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 14, QtWidgets.QTableWidgetItem(
                cliente.condiva))

            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.resizeColumnsToContents()
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.resizeRowsToContents()
        # self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.doubleClicked.connect(self.agregar_cliente_click)

        self.lineEdit_BuscarArticuloNvaFactura1_3.setFocus()
        self.lineEdit_BuscarArticuloNvaFactura1_3.setCursorPosition(0)
        self.dialogo_agregar_cliente_factura.exec_()

    def buscar_cliente_nuevo_presupuesto(self):
        campo1 = 'nombre'
        campo2 = 'apellido'
        campo3 = 'empresa'
        valor1 = str(self.ui_agregar_cliente_Fact.lineEdit_BuscarItemArticuloNvaFactura.text())
        clientes = ClienteDAO.buscar_cliente(campo1, campo2, campo3, valor1)

        self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 0, QtWidgets.QTableWidgetItem(
                str(cliente.codigo)))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 1, QtWidgets.QTableWidgetItem(
                cliente.nombre))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 2, QtWidgets.QTableWidgetItem(
                cliente.apellido))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 3, QtWidgets.QTableWidgetItem(
                cliente.dni))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 4, QtWidgets.QTableWidgetItem(
                cliente.empresa))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(
                cliente.cuit))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(
                cliente.telefono))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(
                cliente.email))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 8, QtWidgets.QTableWidgetItem(
                cliente.direccion))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 9, QtWidgets.QTableWidgetItem(
                cliente.numero))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 10, QtWidgets.QTableWidgetItem(
                cliente.localidad))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 11, QtWidgets.QTableWidgetItem(
                cliente.provincia))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 12, QtWidgets.QTableWidgetItem(
                cliente.pais))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 13, QtWidgets.QTableWidgetItem(
                cliente.observaciones))
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.setItem(i, 14, QtWidgets.QTableWidgetItem(
                cliente.cond_iva))

            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.resizeColumnsToContents()
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.resizeRowsToContents()
            self.lineEdit_BuscarArticuloNvaFactura1.setFocus()
            self.lineEdit_BuscarArticuloNvaFactura1.setCursorPosition(0)

    def agregar_articulo_nuevo_presupuesto(self):

        articulos = ArticuloDAO.seleccionar()
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setRowCount(len(articulos))
        for i, articulo in enumerate(articulos):
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 0, QtWidgets.QTableWidgetItem(
                str(articulo.codigo)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 1, QtWidgets.QTableWidgetItem(
                articulo.nombre))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 2, QtWidgets.QTableWidgetItem(
                articulo._modelo))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 3, QtWidgets.QTableWidgetItem(
                articulo._marca))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 4, QtWidgets.QTableWidgetItem(
                articulo._categoria))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 5,
                                                                                       QtWidgets.QTableWidgetItem(
                                                                                           str(articulo._precio_costo)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 6,
                                                                                       QtWidgets.QTableWidgetItem(
                                                                                           str(articulo._precio_venta)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(
                str(articulo._iva)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 8, QtWidgets.QTableWidgetItem(
                str(articulo._stock)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 9, QtWidgets.QTableWidgetItem(
                str(articulo._margen_ganancia)))
            log.debug(articulo)
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.resizeColumnsToContents()
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.resizeRowsToContents()
        self.ui_ventana_agr_articulo.lineEdit_BuscarArticuloFacturaNueva.textChanged.connect(
            self.buscar_articulo_nueva_factura)
        self.dialogo_agregar_Art_Factura.exec_()

    def buscar_articulo_nuevo_presupuesto(self):
        campo1 = 'nombre'
        campo2 = 'codigo'
        campo3 = 'cod_barras'
        valor1 = self.ui_ventana_agr_articulo.lineEdit_BuscarArticuloFacturaNueva.text()
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.clearContents()
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setRowCount(0)
        articulos = ArticuloDAO.buscar_articulo_nombre(campo1, campo2, campo3, valor1)
        self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setRowCount(len(articulos))
        for i, articulo in enumerate(articulos):
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 0, QtWidgets.QTableWidgetItem(
                str(articulo.codigo)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 1, QtWidgets.QTableWidgetItem(
                articulo.nombre))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 2, QtWidgets.QTableWidgetItem(
                articulo._modelo))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 3, QtWidgets.QTableWidgetItem(
                articulo._marca))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 4, QtWidgets.QTableWidgetItem(
                articulo._categoria))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(articulo._sku))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(articulo._color))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(articulo._caracteristica))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 5, QtWidgets.QTableWidgetItem(
                str(articulo._precio_costo)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 6, QtWidgets.QTableWidgetItem(
                str(articulo._precio_venta)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 7, QtWidgets.QTableWidgetItem(
                str(articulo._iva)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 11, QtWidgets.QTableWidgetItem(articulo._proveedor))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 12, QtWidgets.QTableWidgetItem(str(articulo._tamaño)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 13, QtWidgets.QTableWidgetItem(str(articulo._ancho)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 14, QtWidgets.QTableWidgetItem(str(articulo._largo)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 15, QtWidgets.QTableWidgetItem(str(articulo._profundidad)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 16, QtWidgets.QTableWidgetItem(str(articulo._peso)))
            # self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 17, QtWidgets.QTableWidgetItem(str(articulo._peso_envalado)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 8, QtWidgets.QTableWidgetItem(
                str(articulo._stock)))
            self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura.setItem(i, 9, QtWidgets.QTableWidgetItem(
                str(articulo._margen_ganancia)))
            log.debug(articulo)
        return

    def agregar_articulo_nuevo_presupuesto2(self):
        tabla = self.ui_ventana_agr_articulo.tableWidget_SelecionarArticuloFactura
        lista = Funciones.fx_leer_seleccion_tabla(tabla)[0]
        print(lista)
        print("metodo llamado")
        precio_costo_str = tabla.item(tabla.currentRow(), 5).text().replace('$', '').replace(',', '')
        importe_iva = (float(precio_costo_str) * float(tabla.item(tabla.currentRow(), 7).text())) / 100
        precio_unitario = float(precio_costo_str) + importe_iva
        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura_3.rowCount()
        total = 0
        ################################################################################################
        # nueva_lista = []
        # for i in lista:
        #     nueva_lista.append([i[0], i[1], "1", i[5], i[7], importe_iva, precio_unitario, precio_unitario])
        #     #self.label_subtotal_factura.setText(str(round(precio_unitario, 2)))
        # print(nueva_lista)
        # Funciones.fx_cargarTablaX(nueva_lista, self.tableWidgetDetalleNvaFactura, limpiaTabla=False)
        # self.tableWidgetDetalleNvaFactura.resizeColumnsToContents()
        # self.tableWidgetDetalleNvaFactura.resizeRowsToContents()
        # self.verificarExistencias()
        # self.actualizar_subtotal_factura()
        ##################################################################################################
        # Obtén el código del artículo seleccionado
        codigo_articulo_seleccionado = lista[0][0]

        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura_3.rowCount()

        # Variable para verificar si el artículo ya está en la tabla
        articulo_ya_en_tabla = False

        # Itera sobre cada fila
        for row in range(num_rows):
            # Obtén el código del artículo en la fila actual (asumiendo que es la columna 0)
            codigo_articulo_en_tabla = self.tableWidgetDetalleNvaFactura_3.item(row, 0).text()

            # Si el código del artículo seleccionado coincide con el código del artículo en la fila actual
            if codigo_articulo_seleccionado == codigo_articulo_en_tabla:
                # Incrementa la cantidad del artículo en la fila actual (asumiendo que la cantidad es la columna 2)
                cantidad_actual = int(self.tableWidgetDetalleNvaFactura_3.item(row, 2).text())
                self.tableWidgetDetalleNvaFactura_3.setItem(row, 2,
                                                            QtWidgets.QTableWidgetItem(str(cantidad_actual + 1)))

                # Marca que el artículo ya está en la tabla
                articulo_ya_en_tabla = True
                break

        # Si el artículo no está en la tabla, agrega una nueva fila
        if not articulo_ya_en_tabla:
            nueva_lista = []
            for i in lista:
                nueva_lista.append([i[0], i[1], "1", i[5], i[7], importe_iva, precio_unitario, precio_unitario])
            Funciones.fx_cargarTablaX(nueva_lista, self.tableWidgetDetalleNvaFactura_3, limpiaTabla=False)

        self.tableWidgetDetalleNvaFactura_3.resizeColumnsToContents()
        self.tableWidgetDetalleNvaFactura_3.resizeRowsToContents()
        self.verificarExistencias()
        self.actualizar_subtotal_factura()

    def agregar_cliente_click_presupuesto(self):
        row = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.currentRow()
        # row = self.tableWidgetDetalleNvaFactura.currentRow()
        # item1 = self.tableWidgetAgregarClienteNvaFactura.item(row, 0)
        # if item1 is not None:

        ### CONCATENAR VALORES DE NOMBRE Y APELLIDO JUNTOS
        nombre = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 1).text()
        apellido = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 2).text()
        nombre_completo = " ".join([nombre, apellido])
        self.lineEdit_clienteNvoPresupuesto.setText(nombre_completo)
        ###########################################
        # self.lineEdit_clienteNvaFactura.setText(self.ui.tableWidgetAgregarClienteNvaFactura.item(0, 1).text())
        # self.lineEdit_domclienteNvaFactura.setText(self.ui.tableWidgetAgregarClienteNvaFactura.item(0, 8).text())

        # concatenar los valores de direccion, numero, localidad, provincia en un solo lineedit
        direccion = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 8).text()
        numero = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 9).text()
        localidad = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 10).text()
        provincia = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 11).text()
        pais = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 12).text()
        # Concatenar los valores con espacios entre ellos
        direccion_completa = " ".join([direccion, numero, localidad, provincia, pais])
        # cond_iva = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 11).text()

        self.lineEdit_domclienteNvoPresupuesto.setText(direccion_completa)
        ############################
        self.lineEdit_codclienteNvoPresupuesto.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 0).text())
        self.lineEdit_cuitclienteNvoPresupuesto.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 5).text())
        self.lineEdit_dniclienteNvoPresupuesto.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 3).text())
        self.lineEdit_telclienteNvoPresupuesto.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 6).text())
        self.lineEdit_emailclienteNvoPresupuesto.setText(
            self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 7).text())
        # self.lineEdit_IvaclienteNvaFactura.setText(self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 14).text())
        item_iva = self.ui_agregar_cliente_Fact.tableWidgetAgregarClienteNvaFactura.item(row, 14)
        if item_iva is not None:
            self.lineEdit_IvaclienteNvoPresupuesto.setText(item_iva.text())

        self.dialogo_agregar_cliente_factura.close()

        self.label_309.setText(provincia)

        self.lineEdit_clienteNvoPresupuesto.setReadOnly(True)
        self.lineEdit_domclienteNvoPresupuesto.setReadOnly(True)
        self.lineEdit_codclienteNvoPresupuesto.setReadOnly(True)
        self.lineEdit_cuitclienteNvoPresupuesto.setReadOnly(True)
        self.lineEdit_dniclienteNvoPresupuesto.setReadOnly(True)
        self.lineEdit_telclienteNvoPresupuesto.setReadOnly(True)
        self.lineEdit_emailclienteNvoPresupuesto.setReadOnly(True)
        self.lineEdit_IvaclienteNvoPresupuesto.setReadOnly(True)

        return
        # self.lineEdit_clienteNvaFactura.setText = self.Ui_ventana_agregar_cliente_factura.tableWidgetAgregarClienteNvaFactura.item(row, 0).text()

    def verificarExistencias_Presupuesto(self):
        tabla = self.tableWidgetDetalleNvaFactura_3
        lista = Funciones.fx_leer_seleccion_tabla(tabla)[0]
        for i in lista:
            codarticulo = i[0]
            cantidad = i[2]
            stock = ArticuloDAO.verificar_existencias(codarticulo)
            if cantidad > stock:
                QMessageBox.warning(self, "Stock Insuficiente",
                                    "El stock del artículo seleccionado es insuficiente", )
                return
            else:
                pass

    def actualizar_subtotal_presupuesto(self):
        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura_3.rowCount()

        # Inicializa el total
        sub_total_factura = 0.0
        sub_total_iva = 0.0
        total_factura = 0.0

        # Itera sobre cada fila
        for row in range(num_rows):
            # Obtén el valor de la columna subtotal (asumiendo que es la columna 7)
            item_factura = self.tableWidgetDetalleNvaFactura_3.item(row, 7)
            item_iva = self.tableWidgetDetalleNvaFactura_3.item(row, 5)

            if item_factura is not None:
                subtotal_factura_str = item_factura.text()
                sub_total_factura += float(subtotal_factura_str)

            if item_iva is not None:
                sub_total_iva_str = item_iva.text()
                sub_total_iva += float(sub_total_iva_str)

        # Actualiza label_subtotal_factura con el total
        self.label_subtotal_factura_3.setText(str(round(sub_total_factura - sub_total_iva, 2)))
        self.label_iva_factura_3.setText(str(round(sub_total_iva, 2)))
        self.label_total_Nva_factura_3.setText(str(float(round(sub_total_factura, 2))))

    def actualizar_subtotal_presu(self, row, column):
        # Verifica si la celda cambiada es de la columna "cantidad" (asumiendo que es la columna 2)
        if column == 2:
            # Obtiene el valor de la celda "cantidad"
            cantidad_item = self.tableWidgetDetalleNvaFactura_3.item(row, column)
            if cantidad_item is not None:
                cantidad = float(cantidad_item.text())
            else:
                return  # No item in the specified cell, so we return early

            ###########################################################
            codigoarticulo = self.tableWidgetDetalleNvaFactura_3.item(row, 0)
            cantidad_item = self.tableWidgetDetalleNvaFactura_3.item(row, 2)
            if cantidad_item is not None:
                cantidad = int(cantidad_item.text())
            else:
                return  # No item in the specified cell, so we return early

            stock = ArticuloDAO.verificar_existencias(codigoarticulo)
            if cantidad > stock:
                QMessageBox.warning(self, "Stock Insuficiente",
                                    "El stock del artículo seleccionado es insuficiente, ha seleccionado '{}' y el stock actual es '{}'".format(
                                        cantidad, stock))
                return
            ####################################################################

            # Obtiene el valor de la celda "precio unitario" (asumiendo que es la columna 6)
            precio_unitario_item = self.tableWidgetDetalleNvaFactura_3.item(row, 6)
            iva_item = self.tableWidgetDetalleNvaFactura_3.item(row, 5)
            if precio_unitario_item is not None:
                precio_unitario = float(precio_unitario_item.text())
            else:
                return  # No item in the specified cell, so we return early
            if iva_item is not None:
                iva = float(iva_item.text())
            else:
                return

            # Calcula el subtotal
            subtotal = cantidad * precio_unitario
            importe_iva_item = cantidad * iva

            # Actualiza la celda "subtotal" (asumiendo que es la columna 7)
            self.tableWidgetDetalleNvaFactura_3.setItem(row, 7, QtWidgets.QTableWidgetItem(str((round(subtotal, 2)))))
            self.tableWidgetDetalleNvaFactura_3.setItem(row, 5,
                                                        QtWidgets.QTableWidgetItem(str((round(importe_iva_item, 2)))))

            self.actualizar_subtotal_presupuesto()

    def guardar_presupuesto(self):
        # Obtener los datos de la factura
        codpresupuesto = str(self.lineEdit_numeroNvaFactura_5.text().zfill(8))
        codcliente = self.lineEdit_codclienteNvoPresupuesto.text()
        cliente = self.lineEdit_clienteNvoPresupuesto.text()
        fecha = self.lineEdit_fechaNvaFactura_5.text()
        subtotal = self.label_subtotal_factura_3.text()
        iva = self.label_iva_factura_3.text()
        total = self.label_total_Nva_factura_3.text()
        formapago = self.comboBox_FormaPagoFact_3.currentText()
        fecha_vto = self.dateEdit_fechavencimientoFactura_3.date().toString('dd/MM/yyyy')
        subtotal_presupuesto = self.label_subtotal_factura_3.text()

        # Crear un objeto Factura
        presupuesto = Presupuesto(codpresupuesto, fecha, codcliente, cliente, subtotal, iva, total, formapago,
                                  fecha_vto)

        # Insertar la factura en la base de datos
        presupuesto_insertado = PresupuestoDAO.insertar(presupuesto)
        log.debug(f'Facturas insertadas: {presupuesto_insertado}')
        ###########################################################################################
        presupuesto_json = presupuesto.__dict__

        # Guardar las facturas en un archivo JSON
        with open('negocio/presupuestos.json', 'w') as f:
            json.dump(presupuesto_json, f)
        ###########################################################################################

        # Obtener los detalles de la factura

        self.tableWidgetDetalleNvaFactura_3.rowCount()
        for row in range(self.tableWidgetDetalleNvaFactura_3.rowCount()):
            codarticulo = self.tableWidgetDetalleNvaFactura_3.item(row, 0).text()
            descripcion = self.tableWidgetDetalleNvaFactura_3.item(row, 1).text()
            cantidad = self.tableWidgetDetalleNvaFactura_3.item(row, 2).text()
            precio_unitario = self.tableWidgetDetalleNvaFactura_3.item(row, 3).text().replace('$', '').replace(',', '')
            importe_iva = self.tableWidgetDetalleNvaFactura_3.item(row, 5).text()
            subtotal = self.tableWidgetDetalleNvaFactura_3.item(row, 7).text()
            # precioventa = self.detallefactura.precioventa.replace('$', '').replace(',', '')
            # valores = (detallefactura.serie, detallefactura.codfactura, detallefactura.codarticulo, detallefactura.descripcion, detallefactura.cantidad, float(precioventa), detallefactura.importe, detallefactura.iva)
            detalle = detallePresupuesto(codpresupuesto, codarticulo, descripcion, cantidad, precio_unitario, subtotal,
                                         importe_iva)
            detallePresupuestoDAO.insertar(detalle)
            #################################
            # DESCONTAR STOCK DE LOS ARTICULOS
            #################################
            query_stock = "UPDATE articulos SET stock = stock - %s WHERE codigo = %s"
            valores = (cantidad, codarticulo)
            with CursorDelPool() as cursor:
                cursor.execute(query_stock, valores)

        log.debug(f'Detalles insertados: {detalle}')

        self.label_ingresar_msg2.setText('Presupuesto ingresado correctamente')
        QMessageBox.information(self, "Presupuesto Ingresado",
                                "El presupuesto ha sido ingresado correctamente", )


        empresa = EmpresaDAO.seleccionar()
        if empresa:
            empresa = empresa[0]
            razon_social = empresa.razonsocial
            fantasia_empresa = empresa.nombrefantasia
            cuit_empresa = empresa.cuit
            categoria_iva = empresa.categoria
            iibb_empresa = empresa.iibb
            inicio_actividades = empresa.inicioactividades

        else:
            # Handle the case when there are no empresas
            print("Primero debe cargar los datos de su empresa en Módulo Empresa para poder continuar.")
            return
        domicilio = empresa.domicilio
        localidad = empresa.localidad
        provincia = empresa.provincia
        pais = empresa.pais
        direccion_completa_empresa = " , ".join([domicilio, localidad, provincia, pais])
        # self.lineEdit_localidadNvaFactura.setText(empresa.localidad)
        self.label_72.setText(direccion_completa_empresa)
        cuit_cliente = self.lineEdit_cuitclienteNvoPresupuesto.text()
        condicion_iva = self.lineEdit_IvaclienteNvoPresupuesto.text()
        domicilio_cliente = self.lineEdit_domclienteNvoPresupuesto.text()
        condicion_vta = self.comboBox_FormaPagoFact_3.currentText()


        detalles_presupuesto = detallePresupuestoDAO.busca_detalle_lista(codpresupuesto)

        # # Obtén el directorio base donde se encuentra el archivo main.py
        # basedir = os.path.dirname(__file__)
        # ruta_directorio_presupuestos = os.path.join(basedir, 'Presupuestos')
        # Crear el directorio si no existe
        # if not os.path.exists(ruta_directorio_presupuestos):
        #     os.makedirs(ruta_directorio_presupuestos)
        # # Crea la ruta al archivo modelo_presupuesto.html en el directorio Presupuestos/
        # #template_path = os.path.join(basedir, 'Presupuestos', 'modelo_presupuesto.html')
        # ruta_plantilla_presupuesto = os.path.join(ruta_directorio_presupuestos, "modelo_presupuesto.html")


        # Carga la plantilla
        # env = Environment(loader=FileSystemLoader(ruta_directorio_presupuestos))
        # template = env.get_template(ruta_plantilla_presupuesto)
        basedir = os.path.dirname(__file__)

        subdirectorio = os.path.join(basedir, "Presupuestos")
        if not os.path.exists(subdirectorio):
            os.mkdir(subdirectorio)

        # Cargar la plantilla
        env = Environment(loader=FileSystemLoader(subdirectorio))
        template = env.get_template('modelo_presupuesto.html')

        # Llenar la plantilla con los datos de la factura
        presupuesto_html = template.render(nombrefantasia=fantasia_empresa, razonsocial=razon_social,
                                        codpresupuesto=codpresupuesto, fecha=fecha, cuit=cuit_empresa,
                                        iibb=iibb_empresa, inicioactividades=inicio_actividades,
                                        domicilio=direccion_completa_empresa, categoria=categoria_iva,
                                        cuit_cliente=cuit_cliente,
                                        cliente=cliente, condiva=condicion_iva, direccion=domicilio_cliente,
                                        formapago=condicion_vta, detalles_factura=detalles_presupuesto, subtotal=subtotal_presupuesto, iva=iva,
                                        total=total)  # Agrega más campos según sea necesario

        # Guardar el resultado en un nuevo archivo HTML
        with open(os.path.join(subdirectorio, 'presupuesto.html'), 'w', encoding='utf-8') as f:
            f.write(presupuesto_html)

        # Descargamos el HTML de ejemplo (ver mas arriba)
        # y lo guardamos como bill.html
        # html = open("./bill.html").read()
        html = open(os.path.join(subdirectorio, 'presupuesto.html')).read()

        # Nombre para el archivo (sin .pdf)
        name = "PDF de prueba"

        # Opciones para el archivo
        options = {
            "width": 8,  # Ancho de pagina en pulgadas. Usar 3.1 para ticket
            "marginLeft": 0.4,  # Margen izquierdo en pulgadas. Usar 0.1 para ticket
            "marginRight": 0.4,  # Margen derecho en pulgadas. Usar 0.1 para ticket
            "marginTop": 0.4,  # Margen superior en pulgadas. Usar 0.1 para ticket
            "marginBottom": 0.4  # Margen inferior en pulgadas. Usar 0.1 para ticket
        }

        # Configuración de opciones para el archivo PDF
        options = {
            'page-size': 'Letter',
            'margin-top': '10mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'no-outline': None
        }
        import pdfkit

        # Crear el nombre del archivo
        nombre_archivo = os.path.join(subdirectorio,f'presupuesto_{codpresupuesto}.pdf')

        # Crear el PDF
        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        pdfkit.from_file(os.path.join(subdirectorio,'presupuesto.html'), nombre_archivo, options=options, configuration=config)

        self.lineEdit_clienteNvoPresupuesto.clear()
        self.lineEdit_domclienteNvoPresupuesto.clear()
        self.lineEdit_codclienteNvoPresupuesto.clear()
        self.lineEdit_cuitclienteNvoPresupuesto.clear()
        self.lineEdit_dniclienteNvoPresupuesto.clear()
        self.lineEdit_telclienteNvoPresupuesto.clear()
        self.lineEdit_emailclienteNvoPresupuesto.clear()
        self.tableWidgetDetalleNvaFactura_3.clearContents()
        while self.tableWidgetDetalleNvaFactura_3.rowCount() > 0:
            self.tableWidgetDetalleNvaFactura_3.removeRow(0)

        # Cerrar la ventana
        self.stackedWidget.setCurrentIndex(0)
        return


    def cancelar_presupuesto(self):
        num_rows = self.tableWidgetDetalleNvaFactura_3.rowCount()
        for i in range(num_rows):
            self.tableWidgetDetalleNvaFactura_3.removeRow(0)
        self.lineEdit_clienteNvoPresupuesto.clear()
        self.lineEdit_domclienteNvoPresupuesto.clear()
        self.lineEdit_codclienteNvoPresupuesto.clear()
        self.lineEdit_cuitclienteNvoPresupuesto.clear()
        self.lineEdit_dniclienteNvoPresupuesto.clear()
        self.lineEdit_telclienteNvoPresupuesto.clear()
        self.lineEdit_emailclienteNvoPresupuesto.clear()
        self.lineEdit_IvaclienteNvoPresupuesto.clear()
        self.tableWidgetDetalleNvaFactura_3.clearContents()
        self.label_subtotal_factura_3.clear()
        self.label_iva_factura_3.clear()
        self.label_total_Nva_factura_3.clear()
        return

    def modulo_presupuestos(self):
        self.stackedWidget.setCurrentIndex(11)
        presupuestos = PresupuestoDAO.seleccionar()
        if presupuestos:
            self.tableWidgetPresupuestos.setRowCount(len(presupuestos))
            for i, presupuesto in enumerate(presupuestos):
                self.tableWidgetPresupuestos.setItem(i, 0, QtWidgets.QTableWidgetItem(str(presupuesto.codpresupuesto)))
                self.tableWidgetPresupuestos.setItem(i, 1,
                                                     QtWidgets.QTableWidgetItem(presupuesto.fecha.strftime('%Y-%m-%d')))
                self.tableWidgetPresupuestos.setItem(i, 2, QtWidgets.QTableWidgetItem(str(presupuesto.codcliente)))
                self.tableWidgetPresupuestos.setItem(i, 3, QtWidgets.QTableWidgetItem(presupuesto.cliente))
                self.tableWidgetPresupuestos.setItem(i, 4, QtWidgets.QTableWidgetItem(str(presupuesto.subtotal)))
                self.tableWidgetPresupuestos.setItem(i, 5, QtWidgets.QTableWidgetItem(str(presupuesto.iva)))
                self.tableWidgetPresupuestos.setItem(i, 6, QtWidgets.QTableWidgetItem(str(presupuesto.total)))
                if presupuesto.fecha_vto is not None:
                    self.tableWidgetPresupuestos.setItem(i, 7, QtWidgets.QTableWidgetItem(
                        presupuesto.fecha_vto.strftime('%Y-%m-%d')))
                else:
                    self.tableWidgetPresupuestos.setItem(i, 7, QtWidgets.QTableWidgetItem(''))
                self.tableWidgetPresupuestos.resizeColumnsToContents()
                self.tableWidgetPresupuestos.resizeRowsToContents()

    def seleccionar_presupuesto(self):
        row = self.tableWidgetPresupuestos.currentRow()
        campo = 'codpresupuesto'
        codpresupuesto = self.tableWidgetPresupuestos.item(row, 0).text()
        print(codpresupuesto)
        codcliente = self.tableWidgetPresupuestos.item(row, 2).text()
        cliente = self.tableWidgetPresupuestos.item(row, 3).text()
        presupuestos = PresupuestoDAO.buscar_presupuesto(campo, codpresupuesto)
        if presupuestos:
            # Extract the first Presupuesto object from the list
            presupuesto = presupuestos[0]
            self.lineEdit_numeroNvaFactura_6.setText(str(presupuesto.codpresupuesto).zfill(8))
            self.lineEdit_clienteNvoPresupuesto_2.setText(presupuesto.cliente)
            self.lineEdit_codclienteNvoPresupuesto_2.setText(str(presupuesto.codcliente))
            self.lineEdit_fechaNvaFactura_6.setText(presupuesto.fecha.strftime('%Y-%m-%d'))
            self.label_subtotal_factura_4.setText(str(presupuesto.subtotal))
            self.label_iva_factura_4.setText(str(presupuesto.iva))
            self.label_total_Nva_factura_4.setText(str(presupuesto.total))
            if presupuesto.fecha_vto is not None:
                self.dateEdit_fechavencimientoFactura_4.setDate(presupuesto.fecha_vto)
            else:
                self.dateEdit_fechavencimientoFactura_4.setDate(QDate.currentDate())

        codpresupuesto = self.tableWidgetPresupuestos.item(row, 0).text()

        detalles = detallePresupuestoDAO.busca_detalle(codpresupuesto)
        print(detalles)
        if detalles:
            self.tableWidgetDetalleNvaFactura_4.setRowCount(len(detalles))
            for i, detalle in enumerate(detalles):
                self.tableWidgetDetalleNvaFactura_4.setItem(i, 0, QtWidgets.QTableWidgetItem(codpresupuesto))
                self.tableWidgetDetalleNvaFactura_4.setItem(i, 1, QtWidgets.QTableWidgetItem(str(detalle.codarticulo)))
                self.tableWidgetDetalleNvaFactura_4.setItem(i, 2, QtWidgets.QTableWidgetItem(detalle.descripcion))
                self.tableWidgetDetalleNvaFactura_4.setItem(i, 3, QtWidgets.QTableWidgetItem(str(detalle.cantidad)))
                self.tableWidgetDetalleNvaFactura_4.setItem(i, 4,
                                                            QtWidgets.QTableWidgetItem(str(detalle.precio_unitario)))
                self.tableWidgetDetalleNvaFactura_4.setItem(i, 5, QtWidgets.QTableWidgetItem(str(detalle.subtotal)))
                self.tableWidgetDetalleNvaFactura_4.setItem(i, 6, QtWidgets.QTableWidgetItem(str(detalle.importe_iva)))

            self.tableWidgetDetalleNvaFactura_4.resizeColumnsToContents()

        cliente = ClienteDAO.busca_cliente(codcliente)
        if cliente:
            cliente = cliente[0]

            nombre_completo = " ".join([cliente.nombre, cliente.apellido])
            self.lineEdit_clienteNvoPresupuesto_2.setText(nombre_completo)
            direccion_completa = " ".join(
                [cliente.direccion, cliente.numero, cliente.localidad, cliente.provincia, cliente.pais])
            self.lineEdit_domclienteNvoPresupuesto_2.setText(direccion_completa)
            self.lineEdit_cuitclienteNvoPresupuesto_2.setText(cliente.cuit)
            self.lineEdit_dniclienteNvoPresupuesto_2.setText(cliente.dni)
            self.lineEdit_telclienteNvoPresupuesto_2.setText(cliente.telefono)
            self.lineEdit_emailclienteNvoPresupuesto_2.setText(cliente.email)
            self.lineEdit_IvaclienteNvoPresupuesto_2.setText(cliente.cond_iva)

    def eliminar_presupuesto(self):
        row = self.tableWidgetPresupuestos.currentRow()
        codpresupuesto = self.tableWidgetPresupuestos.item(row, 0).text()
        presupuesto = PresupuestoDAO.buscar_presupuesto('codpresupuesto', codpresupuesto)
        if presupuesto:
            presupuesto = presupuesto[0]
            detalles = detallePresupuestoDAO.busca_detalle(codpresupuesto)
            if detalles:
                for detalle in detalles:
                    if detalle.codpresupuesto is not None:
                        detallePresupuestoDAO.eliminar(codpresupuesto)
                    else:
                        print(f"Skipping detalle because codpresupuesto is None: {detalle}")
            reply = QMessageBox.question(self, 'Eliminar Presupuesto',
                                         "¿Estás seguro de que quieres eliminar el presupuesto?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                PresupuestoDAO.eliminar(codpresupuesto)
                self.tableWidgetPresupuestos.removeRow(row)
                self.tableWidgetDetalleNvaFactura_4.clearContents()
                while self.tableWidgetDetalleNvaFactura_4.rowCount() > 0:
                    self.tableWidgetDetalleNvaFactura_4.removeRow(0)
                    self.label_ingresar_msg2.setText('Presupuesto eliminado correctamente')
                QMessageBox.information(self, "Presupuesto Eliminado",
                                        "El presupuesto ha sido eliminado correctamente", )
                return

        self.lineEdit_clienteNvoPresupuesto.clear()
        self.lineEdit_domclienteNvoPresupuesto.clear()
        self.lineEdit_codclienteNvoPresupuesto.clear()
        self.lineEdit_cuitclienteNvoPresupuesto.clear()
        self.lineEdit_dniclienteNvoPresupuesto.clear()
        self.lineEdit_telclienteNvoPresupuesto.clear()
        self.lineEdit_emailclienteNvoPresupuesto.clear()
        self.label_subtotal_factura_4.setText('0.00')
        self.label_iva_factura_4.setText('0.00')
        self.label_total_Nva_factura_4.setText('0.00')

    def eliminar_articulo_detalle(self):
        # Obtén la fila seleccionada
        row = self.tableWidgetDetalleNvaFactura.currentRow()

        # Si no hay ninguna fila seleccionada, row será -1
        if row == -1:
            QMessageBox.information(self, "Eliminar artículo", "Por favor, selecciona un artículo para eliminar.")
            return

        # Muestra un cuadro de diálogo de confirmación
        reply = QMessageBox.question(self, 'Eliminar artículo',
                                     "¿Estás seguro de que quieres eliminar este artículo de la factura?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Elimina la fila de la tabla
            self.tableWidgetDetalleNvaFactura.removeRow(row)
            self.verificarExistencias()
            self.actualizar_subtotal_factura()

    def eliminar_articulo_detalle_presupuesto(self):
        # Obtén la fila seleccionada
        row = self.tableWidgetDetalleNvaFactura_3.currentRow()

        # Si no hay ninguna fila seleccionada, row será -1
        if row == -1:
            QMessageBox.information(self, "Eliminar artículo", "Por favor, selecciona un artículo para eliminar.")
            return

        # Muestra un cuadro de diálogo de confirmación
        reply = QMessageBox.question(self, 'Eliminar artículo',
                                     "¿Estás seguro de que quieres eliminar este artículo del presupuesto?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Elimina la fila de la tabla
            self.tableWidgetDetalleNvaFactura_3.removeRow(row)
            self.verificarExistencias_presupuesto()
            self.actualizar_subtotal_presupuesto()
            # self.actualizar_subtotal_presu()

    def verificarExistencias_presupuesto(self):
        tabla = self.tableWidgetDetalleNvaFactura_3
        lista = Funciones.fx_leer_seleccion_tabla(tabla)[0]
        for i in lista:
            codarticulo = i[0]
            cantidad = i[2]
            stock = ArticuloDAO.verificar_existencias(codarticulo)
            if cantidad > stock:
                QMessageBox.warning(self, "Stock Insuficiente",
                                    "El stock del artículo seleccionado es insuficiente", )
                return
            else:
                pass

    def actualizar_subtotal_presupuesto(self):
        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura_3.rowCount()

        # Inicializa el total
        sub_total_factura = 0.0
        sub_total_iva = 0.0
        total_factura = 0.0

        # Itera sobre cada fila
        for row in range(num_rows):
            # Obtén el valor de la columna subtotal (asumiendo que es la columna 7)
            item_factura = self.tableWidgetDetalleNvaFactura_3.item(row, 7)
            item_iva = self.tableWidgetDetalleNvaFactura_3.item(row, 5)

            if item_factura is not None:
                subtotal_factura_str = item_factura.text()
                sub_total_factura += float(subtotal_factura_str)

            if item_iva is not None:
                sub_total_iva_str = item_iva.text()
                sub_total_iva += float(sub_total_iva_str)

        # Actualiza label_subtotal_factura con el total
        self.label_subtotal_factura_3.setText(str(round(sub_total_factura - sub_total_iva, 2)))
        self.label_iva_factura_3.setText(str(round(sub_total_iva, 2)))
        self.label_total_Nva_factura_3.setText(str(float(round(sub_total_factura, 2))))

    def actualizar_subtotal_psto(self, row, column):
        # Verifica si la celda cambiada es de la columna "cantidad" (asumiendo que es la columna 2)
        if column == 2:
            # Obtiene el valor de la celda "cantidad"
            cantidad_item = self.tableWidgetDetalleNvaFactura_3.item(row, column)
            if cantidad_item is not None:
                cantidad = float(cantidad_item.text())
            else:
                return  # No item in the specified cell, so we return early

            ###########################################################
            codigoarticulo = self.tableWidgetDetalleNvaFactura_3.item(row, 0)
            cantidad_item = self.tableWidgetDetalleNvaFactura_3.item(row, 2)
            if cantidad_item is not None:
                cantidad = int(cantidad_item.text())
            else:
                return  # No item in the specified cell, so we return early

            stock = ArticuloDAO.verificar_existencias(codigoarticulo)
            if cantidad > stock:
                QMessageBox.warning(self, "Stock Insuficiente",
                                    "El stock del artículo seleccionado es insuficiente, ha seleccionado '{}' y el stock actual es '{}'".format(
                                        cantidad, stock))
                return
            ####################################################################

            # Obtiene el valor de la celda "precio unitario" (asumiendo que es la columna 6)
            precio_unitario_item = self.tableWidgetDetalleNvaFactura_3.item(row, 6)
            iva_item = self.tableWidgetDetalleNvaFactura_3.item(row, 5)
            if precio_unitario_item is not None:
                precio_unitario = float(precio_unitario_item.text())
            else:
                return  # No item in the specified cell, so we return early
            if iva_item is not None:
                iva = float(iva_item.text())
            else:
                return

            # Calcula el subtotal
            subtotal = cantidad * precio_unitario
            importe_iva_item = cantidad * iva

            # Actualiza la celda "subtotal" (asumiendo que es la columna 7)
            self.tableWidgetDetalleNvaFactura_3.setItem(row, 7, QtWidgets.QTableWidgetItem(str((round(subtotal, 2)))))
            self.tableWidgetDetalleNvaFactura_3.setItem(row, 5,
                                                        QtWidgets.QTableWidgetItem(str((round(importe_iva_item, 2)))))

            self.actualizar_subtotal_presupuesto()


    def facturar_presupuesto(self):

        while self.tableWidgetPresupuestos.currentRow() == -1:
            QMessageBox.information(self, "Facturar Presupuesto", "Por favor, selecciona un presupuesto para facturar.")
            return

        reply = QMessageBox.question(self, 'Facturar Presupuesto',
                                     '¿Está seguro de que desea facturar el presupuesto actual? Si selecciona "Sí", el presupuesto se marcará como facturado y no podrá modificarlo más tarde. ¿Desea continuar?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return
        else:
            pass

        self.nueva_factura()




        self.lineEdit_codclienteNvaFactura.setText(self.lineEdit_codclienteNvoPresupuesto_2.text())
        self.lineEdit_clienteNvaFactura.setText(self.lineEdit_clienteNvoPresupuesto_2.text())
        self.lineEdit_fechaNvaFactura.setText(self.lineEdit_fechaNvaFactura_6.text())
        self.label_subtotal_factura.setText(self.label_subtotal_factura_4.text())
        self.label_iva_factura.setText(self.label_iva_factura_4.text())
        self.label_total_Nva_factura.setText(self.label_total_Nva_factura_4.text())
        self.comboBox_FormaPagoFact.setCurrentText(self.comboBox_FormaPagoFact_4.currentText())
        self.dateEdit_fechavencimientoFactura.setDate(QDate.fromString(self.dateEdit_fechavencimientoFactura_4.date().toString('dd/MM/yyyy'), 'dd/MM/yyyy'))
        self.lineEdit_domclienteNvaFactura.setText(self.lineEdit_domclienteNvoPresupuesto_2.text())
        self.lineEdit_cuitclienteNvaFactura.setText(self.lineEdit_cuitclienteNvoPresupuesto_2.text())
        self.lineEdit_dniclienteNvaFactura_2.setText(self.lineEdit_dniclienteNvoPresupuesto_2.text())
        self.lineEdit_telclienteNvaFactura.setText(self.lineEdit_telclienteNvoPresupuesto_2.text())
        self.lineEdit_emailclienteNvaFactura.setText(self.lineEdit_emailclienteNvoPresupuesto_2.text())
        self.lineEdit_IvaclienteNvaFactura.setText(self.lineEdit_IvaclienteNvoPresupuesto_2.text())


        # Obtener los detalles de la factura

        # Crear una lista vacía para almacenar los datos de la tabla
        datos_tabla = []

        # Obtén el número de filas en la tabla
        num_rows = self.tableWidgetDetalleNvaFactura_4.rowCount()

        # Itera sobre cada fila
        for row in range(num_rows):
            # Obtén los datos de cada celda en la fila
            codarticulo = self.tableWidgetDetalleNvaFactura_4.item(row, 1).text()
            descripcion = self.tableWidgetDetalleNvaFactura_4.item(row, 2).text()
            cantidad = self.tableWidgetDetalleNvaFactura_4.item(row, 3).text()
            precio_unitario = self.tableWidgetDetalleNvaFactura_4.item(row, 4).text().replace('$', '').replace(',', '')
            importe_iva = self.tableWidgetDetalleNvaFactura_4.item(row, 6).text()
            subtotal = self.tableWidgetDetalleNvaFactura_4.item(row, 5).text()
            alicuota_iva = round(float(subtotal) / float(importe_iva), 1)
            importe_prod = float(cantidad) * float(precio_unitario)

            # Agrega los datos de la fila a la lista
            datos_tabla.append([codarticulo, descripcion, cantidad, precio_unitario, importe_iva, subtotal, alicuota_iva,importe_prod])

        # Ahora, puedes usar la lista datos_tabla para llenar la tabla tableWidgetDetalleNvaFactura
        self.tableWidgetDetalleNvaFactura.setRowCount(len(datos_tabla))
        for row, data in enumerate(datos_tabla):
            self.tableWidgetDetalleNvaFactura.setItem(row, 0, QtWidgets.QTableWidgetItem(data[0]))
            self.tableWidgetDetalleNvaFactura.setItem(row, 1, QtWidgets.QTableWidgetItem(data[1]))
            self.tableWidgetDetalleNvaFactura.setItem(row, 2, QtWidgets.QTableWidgetItem(data[2]))
            self.tableWidgetDetalleNvaFactura.setItem(row, 3, QtWidgets.QTableWidgetItem(data[3]))
            self.tableWidgetDetalleNvaFactura.setItem(row, 5, QtWidgets.QTableWidgetItem(data[4]))
            self.tableWidgetDetalleNvaFactura.setItem(row, 4, QtWidgets.QTableWidgetItem(str(data[6])))
            self.tableWidgetDetalleNvaFactura.setItem(row, 6, QtWidgets.QTableWidgetItem(str(data[7])))
            self.tableWidgetDetalleNvaFactura.setItem(row, 7, QtWidgets.QTableWidgetItem(data[5]))

        self.tableWidgetDetalleNvaFactura.resizeColumnsToContents()
        self.tableWidgetDetalleNvaFactura.resizeRowsToContents()

        row = self.tableWidgetPresupuestos.currentRow()
        codpresupuesto = self.tableWidgetPresupuestos.item(row, 0).text()
        presupuesto = PresupuestoDAO.eliminar(codpresupuesto)
        detalle_presupuesto = detallePresupuestoDAO.eliminar(codpresupuesto)

        self.stackedWidget.setCurrentIndex(7)








    ############################################################################################
    #
    #                    FACTURA ELECTRONICA
    #
    ############################################################################################

    def generar_factura_afip(self, serie, codfactura, fecha, codcliente, cliente, estado, subtotal, iva, total,
                             formapago, alicuota_iva):

        # afip = Afip({"CUIT": 20409378472})
        afip = Afip({
            "access_token": "e3CBc6TtcOYTPYLBPdke6bilMiqrjIE5xc9PNsxxryHU9NtomipEZD32LC9XznWI",
            "CUIT": 20409378472  # Replace with your CUIT
        })

        # Numero de punto de venta
        punto_de_venta = 1

        # Tipo de comprobante
        tipo_de_comprobante = 6  # 6 = Factura B

        last_voucher = afip.ElectronicBilling.getLastVoucher(punto_de_venta, tipo_de_comprobante)
        # The next voucher number to be authorized
        next_voucher = last_voucher + 1

        # Devolver respuesta completa del web service
        return_full_response = False

        # calcular alicuota IVA
        if alicuota_iva == 21.0:
            id_iva = 5
            porcentaje_iva = 0.21
        else:
            alicuota_iva == 10.5
            id_iva = 4
            porcentaje_iva = 0.105

        # Info del comprobante
        data = {
            "CantReg": 1,  # Ensure this is between 1 and 9998
            "PtoVta": serie,  # Punto de venta
            "CbteTipo": 6,  # Tipo de comprobante (ver tipos disponibles)
            "Concepto": 1,  # Concepto del Comprobante: (1)Productos, (2)Servicios, (3)Productos y Servicios
            "DocTipo": 96,  # Tipo de documento del comprador (99 consumidor final, ver tipos disponibles)
            "DocNro": 30024794,  # Número de documento del comprador (0 consumidor final)
            "CbteDesde": next_voucher,
            # Número de comprobante o numero del primer comprobante en caso de ser mas de uno
            "CbteHasta": next_voucher,
            # Número de comprobante o numero del último comprobante en caso de ser mas de uno
            "CbteFch": 20240621,  # (Opcional) Fecha del comprobante (yyyymmdd) o fecha actual si es nulo
            "ImpTotal": round(float(subtotal), 2) + round(float(subtotal) * porcentaje_iva, 2),
            # Importe total del comprobante
            "ImpTotConc": 0,  # Importe neto no gravado
            "ImpNeto": round(float(subtotal), 2),  # Importe neto gravado
            "ImpOpEx": 0,  # Importe exento de IVA
            "ImpIVA": round(float(subtotal) * porcentaje_iva, 2),  # Importe total de IVA
            "ImpTrib": 0,  # Importe total de tributos
            "MonId": "PES",
            # Tipo de moneda usada en el comprobante (ver tipos disponibles)("PES" para pesos argentinos)
            "MonCotiz": 1,  # Cotización de la moneda usada (1 para pesos argentinos)
            "Iva": [  # (Opcional) Alícuotas asociadas al comprobante
                {
                    "Id": id_iva,  # Id del tipo de IVA (5 para 21%)(ver tipos disponibles)
                    "BaseImp": round(float(subtotal), 2),  # Taxable base
                    "Importe": round(float(subtotal) * porcentaje_iva, 2)  # Importe
                }
            ]
        }

        res = afip.ElectronicBilling.createVoucher(data, return_full_response)
        print(res)
        # voucher_number = res["voucher_number"]

        res["CAE"]  # CAE asignado el comprobante
        res["CAEFchVto"]  # Fecha de vencimiento del CAE (yyyy-mm-dd)

        res = afip.ElectronicBilling.createNextVoucher(data)

        res["CAE"]  # CAE asignado el comprobante
        res["CAEFchVto"]  # Fecha de vencimiento del CAE (yyyy-mm-dd)
        # res["voucher_number"]  # Número asignado al comprobante
        # res["voucher_number"]  # Número asignado al comprobante

        # Numero de comprobante
        numero_de_comprobante = next_voucher

        # Numero de punto de venta
        punto_de_venta = 1

        # Tipo de comprobante
        tipo_de_comprobante = 6  # 6 = Factura B

        voucher_info = afip.ElectronicBilling.getVoucherInfo(numero_de_comprobante, punto_de_venta, tipo_de_comprobante)

        print("Esta es la información del comprobante:")
        print(voucher_info)

        # Descargamos el HTML de ejemplo (ver mas arriba)
        # y lo guardamos como bill.html
        html = open("./bill.html").read()

        # Nombre para el archivo (sin .pdf)
        name = "PDF de prueba"

        # Opciones para el archivo
        options = {
            "width": 8,  # Ancho de pagina en pulgadas. Usar 3.1 para ticket
            "marginLeft": 0.4,  # Margen izquierdo en pulgadas. Usar 0.1 para ticket
            "marginRight": 0.4,  # Margen derecho en pulgadas. Usar 0.1 para ticket
            "marginTop": 0.4,  # Margen superior en pulgadas. Usar 0.1 para ticket
            "marginBottom": 0.4  # Margen inferior en pulgadas. Usar 0.1 para ticket
        }

        # Creamos el PDF
        res = afip.ElectronicBilling.createPDF({
            "html": html,
            "file_name": name,
            "options": options
        })

        # Mostramos la url del archivo creado
        print(res["file"])

    def facturaA(self, tipo, fantasia_empresa, razon_social, serie, codfactura, fecha, cuit_empresa, iibb_empresa,
                 inicio_actividades, domicilio_empresa, categoria_iva, cuit_cliente, codcliente, cliente, condicion_iva,
                 domicilio_cliente, condicion_vta, estado, subtotal, iva, total, formapago, alicuota_iva,
                 detalles_factura):

        # afip = Afip({"CUIT": 20409378472})
        afip = Afip({
            "access_token": "e3CBc6TtcOYTPYLBPdke6bilMiqrjIE5xc9PNsxxryHU9NtomipEZD32LC9XznWI",
            "CUIT": 20409378472  # Replace with your CUIT
        })

        # Numero del punto de venta
        punto_de_venta = serie

        # Tipo de factura
        tipo_de_factura = 1  # 1 = Factura A

        # Número de la ultima Factura A
        last_voucher = afip.ElectronicBilling.getLastVoucher(punto_de_venta, tipo_de_factura)

        # Concepto de la factura
        #
        # Opciones:
        #
        # 1 = Productos
        # 2 = Servicios
        # 3 = Productos y Servicios
        concepto = 1

        # Tipo de documento del comprador
        #
        # Opciones:
        #
        # 80 = CUIT
        # 86 = CUIL
        # 96 = DNI
        # 99 = Consumidor Final
        tipo_de_documento = 80

        # Numero de documento del comprador (0 para consumidor final)
        numero_de_documento = 20300247947

        # Numero de factura
        numero_de_factura = last_voucher + 1

        # Fecha de la factura en formato aaaammdd (hasta 10 dias antes y 10 dias despues)
        fecha = int(datetime.today().strftime("%Y%m%d"))

        # Importe sujeto al IVA (sin incluir IVA)
        # importe_gravado = 100
        importe_gravado = float(subtotal)

        # Importe exento al IVA
        importe_exento_iva = 0

        # Importe de IVA
        # importe_iva = 21
        importe_iva = float(alicuota_iva)

        # Los siguientes campos solo son obligatorios para los conceptos 2 y 3
        if concepto == 2 or concepto == 3:
            # Fecha de inicio de servicio en formato aaaammdd
            fecha_servicio_desde = int(datetime.today().strftime("%Y%m%d"))

            # Fecha de fin de servicio en formato aaaammdd
            fecha_servicio_hasta = int(datetime.today().strftime("%Y%m%d"))

            # Fecha de vencimiento del pago en formato aaaammdd
            fecha_vencimiento_pago = int(datetime.today().strftime("%Y%m%d"))
        else:
            fecha_servicio_desde = None
            fecha_servicio_hasta = None
            fecha_vencimiento_pago = None

        # calcular alicuota IVA
        if alicuota_iva == 21.0:
            id_iva = 5
            porcentaje_iva = 0.21
        else:
            alicuota_iva == 10.5
            id_iva = 4
            porcentaje_iva = 0.105

        data = {
            "CantReg": 1,  # Cantidad de facturas a registrar
            "PtoVta": punto_de_venta,
            "CbteTipo": tipo_de_factura,
            "Concepto": concepto,
            "DocTipo": tipo_de_documento,
            "DocNro": numero_de_documento,
            "CbteDesde": numero_de_factura,
            "CbteHasta": numero_de_factura,
            "CbteFch": fecha,
            "FchServDesde": fecha_servicio_desde,
            "FchServHasta": fecha_servicio_hasta,
            "FchVtoPago": fecha_vencimiento_pago,
            "ImpTotal": round(round(float(subtotal), 2) + round(float(subtotal) * porcentaje_iva, 2), 2),
            "ImpTotConc": 0,  # Importe neto no gravado
            "ImpNeto": round(float(subtotal), 2),
            "ImpOpEx": importe_exento_iva,
            "ImpIVA": round(float(subtotal) * porcentaje_iva, 2),  # Importe total de IVA,
            "ImpTrib": 0,  # Importe total de tributos
            "MonId": "PES",  # Tipo de moneda usada en la factura ("PES" = pesos argentinos)
            "MonCotiz": 1,  # Cotización de la moneda usada (1 para pesos argentinos)
            "Iva": [  # Alícuotas asociadas al factura
                {
                    "Id": id_iva,  # Id del tipo de IVA (5 = 21%)
                    "BaseImp": round(float(subtotal), 2),  # Taxable base
                    "Importe": round(float(subtotal) * porcentaje_iva, 2)  # Importe
                }
            ]
        }

        # Creamos la Factura
        res = afip.ElectronicBilling.createVoucher(data)

        # Mostramos por pantalla los datos de la nueva Factura
        print({
            "cae": res["CAE"],  # CAE asignado a la Factura
            "vencimiento": res["CAEFchVto"]  # Fecha de vencimiento del CAE
        })

        voucher_info = afip.ElectronicBilling.getVoucherInfo(numero_de_factura, punto_de_venta, tipo_de_factura)

        print("Esta es la información del comprobante:")
        print(voucher_info)

        # Crear el diccionario con los datos requeridos
        qr_data = {
            "ver": 1,
            "fecha": fecha,  # Asegúrate de que esta variable esté en el formato correcto
            "cuit": cuit_empresa,  # Asegúrate de que esta variable esté en el formato correcto
            "ptoVta": serie,  # Asegúrate de que esta variable esté en el formato correcto
            "tipoCmp": tipo_de_factura,  # Asegúrate de que esta variable esté en el formato correcto
            "nroCmp": codfactura,  # Asegúrate de que esta variable esté en el formato correcto
            "importe": total,  # Asegúrate de que esta variable esté en el formato correcto
            "moneda": "PES",  # Asegúrate de que esta variable esté en el formato correcto
            "ctz": 1,  # Asegúrate de que esta variable esté en el formato correcto
            "tipoDocRec": 80,  # Asegúrate de que esta variable esté en el formato correcto
            "nroDocRec": numero_de_documento,  # Asegúrate de que esta variable esté en el formato correcto
            "tipoCodAut": "E",  # Asegúrate de que esta variable esté en el formato correcto
            "codAut": res["CAE"]  # Asegúrate de que esta variable esté en el formato correcto
        }

        # Convertir el diccionario a un string JSON
        qr_json = json.dumps(qr_data)

        # Codificar el string JSON en base64
        qr_base64 = base64.b64encode(qr_json.encode()).decode()
        qr_generado = f'https://www.afip.gob.ar/fe/qr/?p={qr_base64}'

        print(qr_base64)
        import segno
        qrcode = segno.make(qr_generado)
        qrcode.save('qr.png')
        # Añadir la ruta de la imagen del código QR a los datos de la factura
        qr_code_image = 'qr.png'

        cae = res["CAE"]
        venc_cae = res["CAEFchVto"]
        # Cargar la plantilla
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('./Facturas/bill.html')

        # Llenar la plantilla con los datos de la factura
        factura_html = template.render(tipo_factura=tipo, nombrefantasia=fantasia_empresa, razonsocial=razon_social,
                                       serie=serie, codfactura=codfactura, fecha=fecha, cuit=cuit_empresa,
                                       iibb=iibb_empresa, inicioactividades=inicio_actividades,
                                       domicilio=domicilio_empresa, categoria=categoria_iva, cuit_cliente=cuit_cliente,
                                       cliente=cliente, condiva=condicion_iva, direccion=domicilio_cliente,
                                       formapago=condicion_vta, cae=cae, vto_cae=venc_cae,
                                       detalles_factura=detalles_factura, subtotal=subtotal, iva=iva,
                                       total=total)  # Agrega más campos según sea necesario

        # Guardar el resultado en un nuevo archivo HTML
        with open('./Facturas/factura.html', 'w', encoding='utf-8') as f:
            f.write(factura_html)

        # Descargamos el HTML de ejemplo (ver mas arriba)
        # y lo guardamos como bill.html
        # html = open("./bill.html").read()
        html = open("./Facturas/factura.html").read()

        # Nombre para el archivo (sin .pdf)
        name = "PDF de prueba"

        # Opciones para el archivo
        options = {
            "width": 8,  # Ancho de pagina en pulgadas. Usar 3.1 para ticket
            "marginLeft": 0.4,  # Margen izquierdo en pulgadas. Usar 0.1 para ticket
            "marginRight": 0.4,  # Margen derecho en pulgadas. Usar 0.1 para ticket
            "marginTop": 0.4,  # Margen superior en pulgadas. Usar 0.1 para ticket
            "marginBottom": 0.4  # Margen inferior en pulgadas. Usar 0.1 para ticket
        }

        # # Creamos el PDF
        # res = afip.ElectronicBilling.createPDF({
        #     "html": html,
        #     "file_name": name,
        #     "options": options
        # })

        # Mostramos la url del archivo creado
        #print(res["file"])

        # Configuración de opciones para el archivo PDF
        options = {
            'page-size': 'Letter',
            'margin-top': '10mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'no-outline': None
        }
        import pdfkit

        # Crear el nombre del archivo
        nombre_archivo = f'./Facturas/factura_{codfactura}_{fecha}.pdf'

        # Crear el PDF
        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        pdfkit.from_file('./Facturas/factura.html', nombre_archivo, options=options, configuration=config)


    def facturaB(self, tipo, fantasia_empresa, razon_social, serie, codfactura, fecha, cuit_empresa, iibb_empresa,
                 inicio_actividades, domicilio_empresa, categoria_iva, cuit_cliente, codcliente, cliente, condicion_iva,
                 domicilio_cliente, condicion_vta, estado, subtotal, iva, total, formapago, alicuota_iva,
                 detalles_factura):

        # afip = Afip({"CUIT": 20409378472})
        afip = Afip({
            "access_token": "e3CBc6TtcOYTPYLBPdke6bilMiqrjIE5xc9PNsxxryHU9NtomipEZD32LC9XznWI",
            "CUIT": 20409378472  # Replace with your CUIT
        })

        # Numero del punto de venta
        punto_de_venta = 1

        # Tipo de factura
        tipo_de_factura = 6  # 6 = Factura B

        # Número de la ultima Factura B
        last_voucher = afip.ElectronicBilling.getLastVoucher(punto_de_venta, tipo_de_factura)

        # Concepto de la factura
        #
        # Opciones:
        #
        # 1 = Productos
        # 2 = Servicios
        # 3 = Productos y Servicios
        concepto = 1

        # Tipo de documento del comprador
        #
        # Opciones:
        #
        # 80 = CUIT
        # 86 = CUIL
        # 96 = DNI
        # 99 = Consumidor Final
        tipo_de_documento = 80

        # Numero de documento del comprador (0 para consumidor final)
        numero_de_documento = 20300247947

        # Numero de factura
        numero_de_factura = last_voucher + 1

        # Fecha de la factura en formato aaaammdd (hasta 10 dias antes y 10 dias despues)
        fecha = int(datetime.today().strftime("%Y%m%d"))

        # Importe sujeto al IVA (sin incluir IVA)
        # importe_gravado = 100
        importe_gravado = float(subtotal)

        # Importe exento al IVA
        importe_exento_iva = 0

        # Importe de IVA
        # importe_iva = 21
        importe_iva = float(alicuota_iva)

        # Los siguientes campos solo son obligatorios para los conceptos 2 y 3
        if concepto == 2 or concepto == 3:
            # Fecha de inicio de servicio en formato aaaammdd
            fecha_servicio_desde = int(datetime.today().strftime("%Y%m%d"))

            # Fecha de fin de servicio en formato aaaammdd
            fecha_servicio_hasta = int(datetime.today().strftime("%Y%m%d"))

            # Fecha de vencimiento del pago en formato aaaammdd
            fecha_vencimiento_pago = int(datetime.today().strftime("%Y%m%d"))
        else:
            fecha_servicio_desde = None
            fecha_servicio_hasta = None
            fecha_vencimiento_pago = None

        # calcular alicuota IVA
        if alicuota_iva == 21.0:
            id_iva = 5
            porcentaje_iva = 0.21
        else:
            alicuota_iva == 10.5
            id_iva = 4
            porcentaje_iva = 0.105

        data = {
            "CantReg": 1,  # Cantidad de facturas a registrar
            "PtoVta": punto_de_venta,
            "CbteTipo": tipo_de_factura,
            "Concepto": concepto,
            "DocTipo": tipo_de_documento,
            "DocNro": numero_de_documento,
            "CbteDesde": numero_de_factura,
            "CbteHasta": numero_de_factura,
            "CbteFch": fecha,
            "FchServDesde": fecha_servicio_desde,
            "FchServHasta": fecha_servicio_hasta,
            "FchVtoPago": fecha_vencimiento_pago,
            "ImpTotal": round(round(float(subtotal), 2) + round(float(subtotal) * porcentaje_iva, 2), 2),
            "ImpTotConc": 0,  # Importe neto no gravado
            "ImpNeto": round(float(subtotal), 2),
            "ImpOpEx": importe_exento_iva,
            "ImpIVA": round(float(subtotal) * porcentaje_iva, 2),  # Importe total de IVA,
            "ImpTrib": 0,  # Importe total de tributos
            "MonId": "PES",  # Tipo de moneda usada en la factura ("PES" = pesos argentinos)
            "MonCotiz": 1,  # Cotización de la moneda usada (1 para pesos argentinos)
            "Iva": [  # Alícuotas asociadas al factura
                {
                    "Id": id_iva,  # Id del tipo de IVA (5 = 21%)
                    "BaseImp": round(float(subtotal), 2),  # Taxable base
                    "Importe": round(float(subtotal) * porcentaje_iva, 2)  # Importe
                }
            ]
        }

        # Creamos la Factura
        res = afip.ElectronicBilling.createVoucher(data)

        # Mostramos por pantalla los datos de la nueva Factura
        print({
            "cae": res["CAE"],  # CAE asignado a la Factura
            "vencimiento": res["CAEFchVto"]  # Fecha de vencimiento del CAE
        })

        voucher_info = afip.ElectronicBilling.getVoucherInfo(numero_de_factura, punto_de_venta, tipo_de_factura)

        print("Esta es la información del comprobante:")
        print(voucher_info)

        cae = res["CAE"]
        venc_cae = res["CAEFchVto"]
        # Cargar la plantilla
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('./Facturas/bill.html')

        # Llenar la plantilla con los datos de la factura
        factura_html = template.render(tipo_factura=tipo, nombrefantasia=fantasia_empresa, razonsocial=razon_social,
                                       serie=serie, codfactura=codfactura, fecha=fecha, cuit=cuit_empresa,
                                       iibb=iibb_empresa, inicioactividades=inicio_actividades,
                                       domicilio=domicilio_empresa, categoria=categoria_iva, cuit_cliente=cuit_cliente,
                                       cliente=cliente, condiva=condicion_iva, direccion=domicilio_cliente,
                                       formapago=condicion_vta, cae=cae, vto_cae=venc_cae,
                                       detalles_factura=detalles_factura, subtotal=subtotal, iva=iva,
                                       total=total)  # Agrega más campos según sea necesario

        # Guardar el resultado en un nuevo archivo HTML
        with open('./Facturas/factura.html', 'w', encoding='utf-8') as f:
            f.write(factura_html)

        # Descargamos el HTML de ejemplo (ver mas arriba)
        # y lo guardamos como bill.html
        # html = open("./bill.html").read()
        html = open("./Facturas/factura.html").read()

        # Nombre para el archivo (sin .pdf)
        name = "PDF de prueba"

        # Opciones para el archivo
        options = {
            "width": 8,  # Ancho de pagina en pulgadas. Usar 3.1 para ticket
            "marginLeft": 0.4,  # Margen izquierdo en pulgadas. Usar 0.1 para ticket
            "marginRight": 0.4,  # Margen derecho en pulgadas. Usar 0.1 para ticket
            "marginTop": 0.4,  # Margen superior en pulgadas. Usar 0.1 para ticket
            "marginBottom": 0.4  # Margen inferior en pulgadas. Usar 0.1 para ticket
        }

        # # Creamos el PDF
        # res = afip.ElectronicBilling.createPDF({
        #     "html": html,
        #     "file_name": name,
        #     "options": options
        # })

        # Mostramos la url del archivo creado
        # print(res["file"])

        # Configuración de opciones para el archivo PDF
        options = {
            'page-size': 'Letter',
            'margin-top': '10mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'no-outline': None
        }
        import pdfkit

        # Crear el nombre del archivo
        nombre_archivo = f'./Facturas/factura_{codfactura}_{fecha}.pdf'

        # Crear el PDF
        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        pdfkit.from_file('./Facturas/factura.html', nombre_archivo, options=options, configuration=config)

    def facturaC(self, tipo, fantasia_empresa, razon_social, serie, codfactura, fecha, cuit_empresa, iibb_empresa,
                 inicio_actividades, domicilio_empresa, categoria_iva, cuit_cliente, codcliente, cliente, condicion_iva,
                 domicilio_cliente, condicion_vta, estado, subtotal, iva, total, formapago, alicuota_iva,
                 detalles_factura):

        # afip = Afip({"CUIT": 20409378472})
        afip = Afip({
            "access_token": "e3CBc6TtcOYTPYLBPdke6bilMiqrjIE5xc9PNsxxryHU9NtomipEZD32LC9XznWI",
            "CUIT": 20409378472  # Replace with your CUIT
        })

        # Numero del punto de venta
        punto_de_venta = 1

        # Tipo de factura
        tipo_de_factura = 11  # 11 = Factura C

        # Número de la ultima Factura B
        last_voucher = afip.ElectronicBilling.getLastVoucher(punto_de_venta, tipo_de_factura)

        # Concepto de la factura
        #
        # Opciones:
        #
        # 1 = Productos
        # 2 = Servicios
        # 3 = Productos y Servicios
        concepto = 1

        # Tipo de documento del comprador
        #
        # Opciones:
        #
        # 80 = CUIT
        # 86 = CUIL
        # 96 = DNI
        # 99 = Consumidor Final
        tipo_de_documento = 99

        # Numero de documento del comprador (0 para consumidor final)
        numero_de_documento = 0

        # Numero de factura
        numero_de_factura = last_voucher + 1

        # Fecha de la factura en formato aaaammdd (hasta 10 dias antes y 10 dias despues)
        fecha = int(datetime.today().strftime("%Y%m%d"))

        # Importe sujeto al IVA (sin incluir IVA)
        # importe_gravado = 100
        importe_gravado = float(subtotal)

        # Importe exento al IVA
        importe_exento_iva = 0

        # Importe de IVA
        # importe_iva = 21
        importe_iva = float(alicuota_iva)

        # Los siguientes campos solo son obligatorios para los conceptos 2 y 3
        if concepto == 2 or concepto == 3:
            # Fecha de inicio de servicio en formato aaaammdd
            fecha_servicio_desde = int(datetime.today().strftime("%Y%m%d"))

            # Fecha de fin de servicio en formato aaaammdd
            fecha_servicio_hasta = int(datetime.today().strftime("%Y%m%d"))

            # Fecha de vencimiento del pago en formato aaaammdd
            fecha_vencimiento_pago = int(datetime.today().strftime("%Y%m%d"))
        else:
            fecha_servicio_desde = None
            fecha_servicio_hasta = None
            fecha_vencimiento_pago = None

        # calcular alicuota IVA
        if alicuota_iva == 21.0:
            id_iva = 5
            porcentaje_iva = 0.21
        else:
            alicuota_iva == 10.5
            id_iva = 4
            porcentaje_iva = 0.105

        data = {
            "CantReg": 1,  # Cantidad de facturas a registrar
            "PtoVta": punto_de_venta,
            "CbteTipo": tipo_de_factura,
            "Concepto": concepto,
            "DocTipo": tipo_de_documento,
            "DocNro": numero_de_documento,
            "CbteDesde": numero_de_factura,
            "CbteHasta": numero_de_factura,
            "CbteFch": fecha,
            "FchServDesde": fecha_servicio_desde,
            "FchServHasta": fecha_servicio_hasta,
            "FchVtoPago": fecha_vencimiento_pago,
            "ImpTotal": round(float(total), 2),
            "ImpTotConc": 0,  # Importe neto no gravado
            "ImpNeto": round(float(total), 2),
            "ImpOpEx": 0,
            "ImpIVA": 0,
            "ImpTrib": 0,  # Importe total de tributos
            "MonId": "PES",  # Tipo de moneda usada en la factura ("PES" = pesos argentinos)
            "MonCotiz": 1  # Cotización de la moneda usada (1 para pesos argentinos)
        }

        # Creamos la Factura
        res = afip.ElectronicBilling.createVoucher(data)

        # Mostramos por pantalla los datos de la nueva Factura
        print({
            "cae": res["CAE"],  # CAE asignado a la Factura
            "vencimiento": res["CAEFchVto"]  # Fecha de vencimiento del CAE
        })

        voucher_info = afip.ElectronicBilling.getVoucherInfo(numero_de_factura, punto_de_venta, tipo_de_factura)

        print("Esta es la información del comprobante:")
        print(voucher_info)

        cae = res["CAE"]
        venc_cae = res["CAEFchVto"]
        # Cargar la plantilla
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('./Facturas/bill.html')

        # Llenar la plantilla con los datos de la factura
        factura_html = template.render(tipo_factura=tipo, nombrefantasia=fantasia_empresa, razonsocial=razon_social,
                                       serie=serie, codfactura=codfactura, fecha=fecha, cuit=cuit_empresa,
                                       iibb=iibb_empresa, inicioactividades=inicio_actividades,
                                       domicilio=domicilio_empresa, categoria=categoria_iva, cuit_cliente=cuit_cliente,
                                       cliente=cliente, condiva=condicion_iva, direccion=domicilio_cliente,
                                       formapago=condicion_vta, cae=cae, vto_cae=venc_cae,
                                       detalles_factura=detalles_factura, subtotal=subtotal, iva=iva,
                                       total=total)  # Agrega más campos según sea necesario

        # Guardar el resultado en un nuevo archivo HTML
        with open('./Facturas/factura.html', 'w', encoding='utf-8') as f:
            f.write(factura_html)

        # Descargamos el HTML de ejemplo (ver mas arriba)
        # y lo guardamos como bill.html
        # html = open("./bill.html").read()
        html = open("./Facturas/factura.html").read()

        # Nombre para el archivo (sin .pdf)
        name = "PDF de prueba"

        # Opciones para el archivo
        options = {
            "width": 8,  # Ancho de pagina en pulgadas. Usar 3.1 para ticket
            "marginLeft": 0.4,  # Margen izquierdo en pulgadas. Usar 0.1 para ticket
            "marginRight": 0.4,  # Margen derecho en pulgadas. Usar 0.1 para ticket
            "marginTop": 0.4,  # Margen superior en pulgadas. Usar 0.1 para ticket
            "marginBottom": 0.4  # Margen inferior en pulgadas. Usar 0.1 para ticket
        }

        # # Creamos el PDF
        # res = afip.ElectronicBilling.createPDF({
        #     "html": html,
        #     "file_name": name,
        #     "options": options
        # })

        # Mostramos la url del archivo creado
        # print(res["file"])

        # Configuración de opciones para el archivo PDF
        options = {
            'page-size': 'Letter',
            'margin-top': '10mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'no-outline': None
        }
        import pdfkit

        # Crear el nombre del archivo
        nombre_archivo = f'./Facturas/factura_{codfactura}_{fecha}.pdf'

        # Crear el PDF
        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        pdfkit.from_file('./Facturas/factura.html', nombre_archivo, options=options, configuration=config)


    def cliente_afip(self):

        afip = Afip({
            "access_token": "e3CBc6TtcOYTPYLBPdke6bilMiqrjIE5xc9PNsxxryHU9NtomipEZD32LC9XznWI",
            "CUIT": 20409378472  # Replace with your CUIT
        })

        # CUIT del contribuyente
    ####Padrón de constancia de inscripción
        # tax_id = self.lineEdit_cuitNvoCliente.text()
        # taxpayer_details = afip.RegisterInscriptionProof.getTaxpayerDetails(tax_id)
        # print(taxpayer_details)
        # CUIT del contribuyente
    ###########################################################################################3
    ####Padrón alcance 10
        tax_id = self.lineEdit_cuitNvoCliente.text()

        taxpayer_details = afip.RegisterScopeTen.getTaxpayerDetails(tax_id)
        print(taxpayer_details)

        # Obtener la razón social
        razon_social = taxpayer_details['persona']['razonSocial']
        self.lineEdit_empresaNvoCliente.setText(razon_social)
        if taxpayer_details['persona']['tipoClave'] == 'CUIT':
            self.lineEdit_nombreNvoCliente.setText(razon_social)
            self.lineEdit_lineEdit_dniNvoCliente.setText(str(0))
        # Obtener el CUIT
        cuit = taxpayer_details['persona']['idPersona']

        # Obtener la condición del IVA
        condicion_iva = taxpayer_details['persona']['descripcionActividadPrincipal']

        print(f"Razón Social: {razon_social}")
        print(f"CUIT: {cuit}")
        print(f"Condición IVA: {condicion_iva}")

        # Obtener la lista de domicilios
        domicilios = taxpayer_details['persona']['domicilio']

        # Iterar sobre la lista de domicilios
        for domicilio in domicilios:
            # Verificar si el tipo de domicilio es 'FISCAL'
            if domicilio['tipoDomicilio'] == 'LEGAL/REAL':
                # Imprimir la dirección
                print(domicilio['direccion'])
                self.lineEdit_direccionNvoCliente.setText(domicilio['direccion'])
                self.lineEdit_localidadNvoCliente.setText(domicilio['localidad'])
                self.lineEdit_provinciaNvoCliente.setText(domicilio['descripcionProvincia'])
                self.lineEdit_paisNvoCliente.setText('ARGENTINA')
        return




    ########################################################################################3##
        # CUIT del contribuyente
    ####Padrón alcance 13
        # tax_id = self.lineEdit_cuitNvoCliente.text()
        #
        # taxpayer_details = afip.RegisterScopeThirteen.getTaxpayerDetails(tax_id)
        # print(taxpayer_details)


    def proveedor_afip(self):

        afip = Afip({
            "access_token": "e3CBc6TtcOYTPYLBPdke6bilMiqrjIE5xc9PNsxxryHU9NtomipEZD32LC9XznWI",
            "CUIT": 20409378472  # Replace with your CUIT
        })

        # CUIT del contribuyente
    ####Padrón de constancia de inscripción
        # tax_id = self.lineEdit_cuitNvoCliente.text()
        # taxpayer_details = afip.RegisterInscriptionProof.getTaxpayerDetails(tax_id)
        # print(taxpayer_details)
        # CUIT del contribuyente
    ###########################################################################################3
    ####Padrón alcance 10
        tax_id = self.lineEdit_cuitNvoProveedor.text()

        taxpayer_details = afip.RegisterScopeTen.getTaxpayerDetails(tax_id)
        print(taxpayer_details)

        # Obtener la razón social
        razon_social = taxpayer_details['persona']['razonSocial']
        self.lineEdit_razonsocialNvoProveedor.setText(razon_social)

        # Obtener el CUIT
        cuit = taxpayer_details['persona']['idPersona']

        # Obtener la condición del IVA
        condicion_iva = taxpayer_details['persona']['descripcionActividadPrincipal']

        # Obtener la lista de domicilios
        domicilios = taxpayer_details['persona']['domicilio']

        # Iterar sobre la lista de domicilios
        for domicilio in domicilios:
            # Verificar si el tipo de domicilio es 'FISCAL'
            if domicilio['tipoDomicilio'] == 'LEGAL/REAL':
                # Imprimir la dirección
                print(domicilio['direccion'])
                self.lineEdit_domicilioNvoProveedor.setText(domicilio['direccion'])
                self.lineEdit_ciudadNvoProveedor.setText(domicilio['localidad'])
                self.lineEdit_provinciaNvoProveedor.setText(domicilio['descripcionProvincia'])
                self.lineEdit_paisNvoProveedor.setText('ARGENTINA')
        return


  #################################################################################################################
  #
  #                                    DESPACHOS
  #
  #################################################################################################################
    def modulo_despachos(self):
        self.stackedWidget.setCurrentIndex(13)
        self.lineEdit_fechaNvaFactura_7.setText(str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        despachos = DespachoDAO.seleccionar()
        self.tableWidget_ultimasFacturas_3.setRowCount(len(despachos))
        for i, despacho in enumerate(despachos):
            self.tableWidget_ultimasFacturas_3.setItem(i, 0, QtWidgets.QTableWidgetItem(str(despacho.coddespacho)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 1, QtWidgets.QTableWidgetItem(str(despacho.fecha)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 2, QtWidgets.QTableWidgetItem(str(despacho.serie)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 3, QtWidgets.QTableWidgetItem(str(despacho.codfactura)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 4, QtWidgets.QTableWidgetItem(str(despacho.codcliente)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 5, QtWidgets.QTableWidgetItem(str(despacho.cliente)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 6, QtWidgets.QTableWidgetItem(str(despacho.estado)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 7, QtWidgets.QTableWidgetItem(str(despacho.tipo)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 8, QtWidgets.QTableWidgetItem(str(despacho.transporte)))
            self.tableWidget_ultimasFacturas_3.setItem(i, 9, QtWidgets.QTableWidgetItem(str(despacho.guia)))


        self.tableWidget_ultimasFacturas_3.resizeColumnsToContents()
        self.tableWidget_ultimasFacturas_3.resizeRowsToContents()

    def seleccionar_factura_despacho(self):

        # Crear un QPixmap con la ruta de la imagen
        logo_pixmap = QPixmap(':/icons/Icons/no-disponible.png')

        # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
        logo_pixmap = logo_pixmap.scaled(self.label_dni_frente.size(), Qt.KeepAspectRatio)

        # Establecer el QPixmap en la QLabel
        self.label_dni_frente.setPixmap(logo_pixmap)

        # Crear un QPixmap con la ruta de la imagen
        logo_pixmap1 = QPixmap(':/icons/Icons/no-disponible.png')

        # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
        logo_pixmap1 = logo_pixmap1.scaled(self.label_dni_dorso.size(), Qt.KeepAspectRatio)

        # Establecer el QPixmap en la QLabel
        self.label_dni_dorso.setPixmap(logo_pixmap1)

        row = self.tableWidget_ultimasFacturas_3.currentRow()
        codfactura = int(self.tableWidget_ultimasFacturas_3.item(row, 3).text())
        self.lineEdit_numeroNvaFactura_7.setText(str(codfactura).zfill(8))
        self.lineEdit_serieNvaFactura_7.setText(str(self.tableWidget_ultimasFacturas_3.item(row, 2).text()).zfill(5))
        detalles = detalleFacturaDAO.busca_detalle(codfactura)
        self.tableWidget_detalleultimasFacturas_4.setRowCount(len(detalles))
        for i, detalle in enumerate(detalles):
            self.tableWidget_detalleultimasFacturas_4.setItem(i, 0, QtWidgets.QTableWidgetItem(str(detalle.codarticulo)))
            self.tableWidget_detalleultimasFacturas_4.setItem(i, 1, QtWidgets.QTableWidgetItem(detalle.descripcion))
            self.tableWidget_detalleultimasFacturas_4.setItem(i, 2, QtWidgets.QTableWidgetItem(str(detalle.cantidad)))
            self.tableWidget_detalleultimasFacturas_4.setItem(i, 3, QtWidgets.QTableWidgetItem(str(detalle.precioventa)))
            #self.tableWidget_detalleultimasFacturas_4.setItem(i, 4, QtWidgets.QTableWidgetItem(str(round((detalle.iva/detalle.importe) *100, 2))))
            self.tableWidget_detalleultimasFacturas_4.setItem(i, 4, QtWidgets.QTableWidgetItem(str(detalle.importe)))
            self.tableWidget_detalleultimasFacturas_4.setItem(i, 5, QtWidgets.QTableWidgetItem(str(detalle.iva)))
            self.tableWidget_detalleultimasFacturas_4.setItem(i, 6, QtWidgets.QTableWidgetItem(str(detalle.importe)))
            self.tableWidget_detalleultimasFacturas_4.resizeColumnsToContents()
            self.tableWidget_detalleultimasFacturas_4.resizeRowsToContents()
            log.debug(detalle)

        row = self.tableWidget_ultimasFacturas_3.currentRow()
        codcliente = self.tableWidget_ultimasFacturas_3.item(row, 4).text()
        self.lineEdit_codclienteNvoPresupuesto_3.setText(codcliente)
        self.lineEdit_clienteNvoPresupuesto_3.setText(self.tableWidget_ultimasFacturas_3.item(row, 5).text())
        #codcliente = self.lineEdit_codclienteNvoPresupuesto_3.text
        cliente = ClienteDAO.busca_cliente(codcliente)[0]
        direccion = cliente.direccion
        numero = cliente.numero
        localidad = cliente.localidad
        provincia = cliente.provincia
        pais = cliente.pais
        direccion_completa_cliente = " , ".join([direccion, numero, localidad, provincia, pais])

        self.lineEdit_domclienteNvoPresupuesto_3.setText(direccion_completa_cliente)
        self.lineEdit_cuitclienteNvoPresupuesto_3.setText(cliente.cuit)
        self.lineEdit_dniclienteNvoPresupuesto_3.setText(cliente.dni)
        self.lineEdit_telclienteNvoPresupuesto_3.setText(cliente.telefono)

        if self.tableWidget_ultimasFacturas_3.item(row,6).text() == 'ENTREGADA':
            self.lineEdit_fechaCompra.setText(self.tableWidget_ultimasFacturas_3.item(row,1).text())
            self.comboBox_EstadoDespacho.setCurrentText('ENTREGADA')
            self.comboBox_EstadoDespacho_2.setCurrentText(self.tableWidget_ultimasFacturas_3.item(row,7).text())
            self.lineEdit_fechaentregada_2.setText(self.tableWidget_ultimasFacturas_3.item(row,8).text())
            self.lineEdit_fechaentregada_3.setText(self.tableWidget_ultimasFacturas_3.item(row,9).text())
            self.lineEdit_fechaCompra.setReadOnly(True)
            self.comboBox_EstadoDespacho.setDisabled(True)
            self.comboBox_EstadoDespacho_2.setDisabled(True)
            self.lineEdit_fechaentregada_2.setReadOnly(True)
            self.lineEdit_fechaentregada_3.setReadOnly(True)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap = QPixmap(f'Despacho/FacturaN-{codfactura}_frente.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap = logo_pixmap.scaled(self.label_dni_frente.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.label_dni_frente.setPixmap(logo_pixmap)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap1 = QPixmap(f'Despacho/FacturaN-{codfactura}_dorso.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap1 = logo_pixmap1.scaled(self.label_dni_dorso.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.label_dni_dorso.setPixmap(logo_pixmap1)


        elif self.tableWidget_ultimasFacturas_3.item(row,6).text() == 'PENDIENTE':
            self.comboBox_EstadoDespacho.setEnabled(True)
            self.comboBox_EstadoDespacho_2.setEnabled(True)
            self.lineEdit_fechaentregada_2.setReadOnly(False)
            self.lineEdit_fechaentregada_3.setReadOnly(False)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap = QPixmap(':/icons/Icons/no-disponible.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap = logo_pixmap.scaled(self.label_dni_frente.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.label_dni_frente.setPixmap(logo_pixmap)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap1 = QPixmap(':/icons/Icons/no-disponible.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap1 = logo_pixmap1.scaled(self.label_dni_dorso.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.label_dni_dorso.setPixmap(logo_pixmap1)

        elif self.tableWidget_ultimasFacturas_3.item(row,6).text() == 'PARCIAL':
            self.comboBox_EstadoDespacho.setEnabled(True)
            self.comboBox_EstadoDespacho_2.setEnabled(True)
            self.lineEdit_fechaentregada_2.setReadOnly(False)
            self.lineEdit_fechaentregada_3.setReadOnly(False)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap = QPixmap(f'Despacho/FacturaN-{codfactura}_frente.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap = logo_pixmap.scaled(self.label_dni_frente.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.label_dni_frente.setPixmap(logo_pixmap)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap1 = QPixmap(f'Despacho/FacturaN-{codfactura}_dorso.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap1 = logo_pixmap1.scaled(self.label_dni_dorso.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.label_dni_dorso.setPixmap(logo_pixmap1)

        else:
            self.comboBox_EstadoDespacho.setEnabled(True)
            self.comboBox_EstadoDespacho_2.setEnabled(True)
            self.lineEdit_fechaentregada_2.setReadOnly(False)
            self.lineEdit_fechaentregada_3.setReadOnly(False)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap = QPixmap(f'Despacho/FacturaN-{codfactura}_frente.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap = logo_pixmap.scaled(self.label_dni_frente.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.label_dni_frente.setPixmap(logo_pixmap)

            # Crear un QPixmap con la ruta de la imagen
            logo_pixmap1 = QPixmap(f'Despacho/FacturaN-{codfactura}_dorso.png')

            # Asegúrate de que la imagen se ajuste al tamaño de la QLabel redimensionándola
            logo_pixmap1 = logo_pixmap1.scaled(self.label_dni_dorso.size(), Qt.KeepAspectRatio)

            # Establecer el QPixmap en la QLabel
            self.label_dni_dorso.setPixmap(logo_pixmap1)

    def despachar_factura(self):
        row = self.tableWidget_ultimasFacturas_3.currentRow()
        mod_despacho_ant = self.tableWidget_ultimasFacturas_3.item(row, 0).text()
        query_act = "UPDATE despacho SET estado = 'ENTREGADA' WHERE coddespacho = %s"
        with CursorDelPool() as cursor:
            cursor.execute(query_act, (mod_despacho_ant,))

        if row == -1:  # No se ha seleccionado ninguna fila
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Debe seleccionar una factura primero")
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            query_NroDespacho = "SELECT DISTINCT ON (coddespacho) * FROM despacho ORDER BY coddespacho DESC"

            with CursorDelPool() as cursor:
                cursor.execute(query_NroDespacho)
                registros = cursor.fetchall()
                despachos = []
                for registro in registros:
                    despacho = Despacho(registro[0], registro[1], registro[2], registro[3], registro[4],
                                              registro[5],
                                              registro[6], registro[7], registro[8], registro[9], registro[10])
                    despachos.append(despacho)
                if despachos:
                    codigo = despachos[0].coddespacho + 1
                else:
                    codigo = 1


            fecha = self.lineEdit_fechaNvaFactura_7.text()
            serie = self.lineEdit_serieNvaFactura_7.text()
            codfactura = int(self.tableWidget_ultimasFacturas_3.item(row, 3).text())
            codcliente = self.lineEdit_codclienteNvoPresupuesto_3.text()
            cliente = self.lineEdit_clienteNvoPresupuesto_3.text()
            estado = self.comboBox_EstadoDespacho.currentText()
            tipo = self.comboBox_EstadoDespacho_2.currentText()
            transporte = self.lineEdit_fechaentregada_2.text()
            guia = self.lineEdit_fechaentregada_3.text()
            observaciones = self.textEdit_observacionesDespacho.toPlainText()

            # Create a Despacho object
            despacho = Despacho(codigo, fecha, serie, codfactura, codcliente, cliente, estado, tipo, transporte,
                                guia, observaciones)

            # Pass the Despacho object to the insertar method
            DespachoDAO.insertar(despacho)

            QMessageBox.information(self, "Despacho Ingresado",
                                    "El despacho ha sido ingresado correctamente", )

            row = self.tableWidget_ultimasFacturas_3.currentRow()
            codcliente = self.tableWidget_ultimasFacturas_3.item(row, 4).text()
            self.lineEdit_codclienteNvoPresupuesto_3.setText(codcliente)
            self.lineEdit_clienteNvoPresupuesto_3.setText(self.tableWidget_ultimasFacturas_3.item(row, 5).text())
            # codcliente = self.lineEdit_codclienteNvoPresupuesto_3.text
            cliente = ClienteDAO.busca_cliente(codcliente)[0]
            nombre = cliente.nombre
            apellido = cliente.apellido
            nombre_completo = " ".join([nombre, apellido])
            direccion = cliente.direccion
            numero = cliente.numero
            localidad = cliente.localidad
            provincia = cliente.provincia
            pais = cliente.pais
            direccion_completa_cliente = " , ".join([direccion, numero, localidad, provincia, pais])
            cuit_cliente = self.lineEdit_cuitclienteNvoPresupuesto_3.text()
            condicion_iva = cliente.condiva

            empresa = EmpresaDAO.seleccionar()
            fantasia_empresa = empresa[0].nombrefantasia
            razon_social = empresa[0].razonsocial
            cuit_empresa = empresa[0].cuit
            iibb_empresa = empresa[0].iibb
            inicio_actividades = empresa[0].inicioactividades
            domicilio_empresa = empresa[0].domicilio
            categoria_iva = empresa[0].categoria

            detalles_factura = detalleFacturaDAO.busca_detalle_lista(codfactura)



    #################################################################################################
            #   GENERAR PDF REMITO
    #################################################################################################
            basedir = os.path.dirname(__file__)

            subdirectorio = os.path.join(basedir, "Despacho")
            if not os.path.exists(subdirectorio):
                os.mkdir(subdirectorio)

            # Cargar la plantilla
            env = Environment(loader=FileSystemLoader(subdirectorio))

            template = env.get_template('despacho.html')

            # Llenar la plantilla con los datos de la factura
            remito_html = template.render(tipo_factura=tipo, nombrefantasia=fantasia_empresa, razonsocial=razon_social,
                                           serie=serie, codfactura=codfactura, fecha=fecha, cuit=cuit_empresa,
                                           iibb=iibb_empresa, inicioactividades=inicio_actividades,
                                           domicilio=domicilio_empresa, categoria=categoria_iva,
                                           cuit_cliente=cuit_cliente,
                                           cliente=nombre_completo, condiva=condicion_iva, direccion=direccion_completa_cliente,
                                           detalles_factura=detalles_factura)  # Agrega más campos según sea necesario
            html = ''
            # Guardar el resultado en un nuevo archivo HTML
            with open(os.path.join(subdirectorio,'remito.html'), 'w', encoding='utf-8') as f:
                f.write(remito_html)
                f.close()
                #html = f.read()

            # Descargamos el HTML de ejemplo (ver mas arriba)
            # y lo guardamos como bill.html
            # html = open("./bill.html").read()
            html = open(os.path.join(subdirectorio,'remito.html')).read()

            # Nombre para el archivo (sin .pdf)
            name = "PDF de prueba"

            # Opciones para el archivo
            options = {
                "width": 8,  # Ancho de pagina en pulgadas. Usar 3.1 para ticket
                "marginLeft": 0.4,  # Margen izquierdo en pulgadas. Usar 0.1 para ticket
                "marginRight": 0.4,  # Margen derecho en pulgadas. Usar 0.1 para ticket
                "marginTop": 0.4,  # Margen superior en pulgadas. Usar 0.1 para ticket
                "marginBottom": 0.4  # Margen inferior en pulgadas. Usar 0.1 para ticket
            }

            # # Creamos el PDF
            # res = afip.ElectronicBilling.createPDF({
            #     "html": html,
            #     "file_name": name,
            #     "options": options
            # })

            # Mostramos la url del archivo creado
            # print(res["file"])

            # Configuración de opciones para el archivo PDF
            options = {
                'page-size': 'Letter',
                'margin-top': '10mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm',
                'encoding': "UTF-8",
                'no-outline': None
            }
            import pdfkit

            # Crear el nombre del archivo
            nombre_archivo = os.path.join(subdirectorio,f'remito_{codfactura}.pdf')

            # Crear el PDF
            config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
            pdfkit.from_file(os.path.join(subdirectorio,'remito.html'), nombre_archivo, options=options, configuration=config)


            self.modulo_despachos()


    def ver_despacho(self):
        row = self.tableWidget_ultimasFacturas_3.currentRow()
        codfactura = self.tableWidget_ultimasFacturas_3.item(row, 3).text()
        basedir = os.path.dirname(__file__)
        subdirectorio = os.path.join(basedir, "Despacho")
        nombre_archivo = os.path.join(subdirectorio, f'remito_{codfactura}.pdf')
        os.startfile(nombre_archivo)

    def presupuesto_pdf(self):
        row = self.tableWidgetPresupuestos.currentRow()
        codpresupuesto = self.tableWidgetPresupuestos.item(row, 0).text().zfill(8)
        basedir = os.path.dirname(__file__)
        subdirectorio = os.path.join(basedir, "Presupuestos")
        nombre_archivo = os.path.join(subdirectorio, f'presupuesto_{codpresupuesto}.pdf')
        os.startfile(nombre_archivo)

    def factura_pdf(self):
        row = self.tableWidget_ultimasFacturas.currentRow()
        codfactura = self.tableWidget_ultimasFacturas.item(row, 1).text().zfill(8)
        # Obtienes la fecha desde la interfaz de usuario
        fecha_str = self.tableWidget_ultimasFacturas.item(row, 3).text()

        # Conviertes el string a un objeto datetime
        fecha_datetime = datetime.strptime(fecha_str, "%Y-%m-%d")

        # Formateas el objeto datetime a yyyymmdd
        fecha_formateada = fecha_datetime.strftime("%Y%m%d")

        basedir = os.path.dirname(__file__)
        subdirectorio = os.path.join(basedir, "Facturas")
        nombre_archivo = os.path.join(subdirectorio, f'factura_{codfactura}_{fecha_formateada}.pdf')
        os.startfile(nombre_archivo)


    def escanear_documentos(self):
        row = self.tableWidget_ultimasFacturas_3.currentRow()
        codfactura = self.tableWidget_ultimasFacturas_3.item(row, 3).text()
        dni_captura = DNI_captura(codfactura)
        dni_captura.capture()


    def crear_grafico_ventas(self, tipo):

        ventas = FacturaDAO.graficoventas()
        df_ventas = pd.DataFrame(ventas)
        df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])  # Convert 'fecha' to datetime
        df_ventas['total'] = pd.to_numeric(df_ventas['total'], errors='coerce')  # Ensure 'total' is numeric

        if tipo == "DIARIO":
            df_agrupado = df_ventas.groupby(df_ventas['fecha'].dt.date)['total'].sum()
        elif tipo == "SEMANAL":
            df_agrupado = df_ventas.groupby(df_ventas['fecha'].dt.to_period('W'))['total'].sum()
        elif tipo == "MENSUAL":
            df_agrupado = df_ventas.groupby(df_ventas['fecha'].dt.to_period('M'))['total'].sum()
        elif tipo == "ANUAL":
            df_agrupado = df_ventas.groupby(df_ventas['fecha'].dt.to_period('Y'))['total'].sum()

        # Convert PeriodIndex to DateTimeIndex if necessary
        if isinstance(df_agrupado.index, pd.PeriodIndex):
            df_agrupado.index = df_agrupado.index.to_timestamp()

        # Convert the index to string to avoid plotting issues
        df_agrupado.index = df_agrupado.index.astype(str)

        plt.figure(figsize=(10, 6))
        plt.plot(df_agrupado.index, df_agrupado, marker='o')  # Plot using df_agrupado directly if it's a Series
        plt.title(f'Ventas {tipo}')
        plt.xlabel('Fecha')
        plt.ylabel('Ventas')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # # Mostrar el gráfico
        # plt.show()

        # Guardar el gráfico como una imagen temporal
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        plt.savefig(temp_file.name)
        plt.close()

        # Cargar la imagen en el QLabel
        self.label_vtastotales.setPixmap(QPixmap(temp_file.name))

    def grafico_ventas_por_categoria(self):
        # Consulta SQL corregida
        consulta_sql = """
        SELECT a.categoria, SUM(df.importe) AS total_ventas
        FROM detallefactura df
        JOIN articulos a ON df.codarticulo = a.codigo
        GROUP BY a.categoria
        """

        # Ejecutar consulta y cargar los datos en un DataFrame
        with CursorDelPool() as cursor:
            cursor.execute(consulta_sql)
            registros = cursor.fetchall()
            df = pd.DataFrame(registros, columns=['categoria', 'total_ventas'])

        # Asegurarse de que los montos sean numéricos
        df['total_ventas'] = pd.to_numeric(df['total_ventas'])

        # Dimensiones deseadas del QLabel en píxeles
        label_width_px = 721
        label_height_px = 311

        # Convertir las dimensiones a pulgadas para matplotlib (DPI=100 por defecto)
        dpi = 100
        fig_width_in = label_width_px / dpi
        fig_height_in = label_height_px / dpi

        plt.figure(figsize=(fig_width_in, fig_height_in))
        df.plot.pie(y='total_ventas', labels=df['categoria'], autopct='%1.1f%%', startangle=140)
        plt.title('Ventas Totales por Categoría de Artículo')
        plt.ylabel('')  # Eliminar la etiqueta del eje y

        temp_file_path1 = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
        plt.savefig(temp_file_path1)
        plt.close()

        pixmap = QPixmap(temp_file_path1)
        self.label_vtasxcategoria.setPixmap(pixmap)
        self.label_vtasxcategoria.setFixedSize(label_width_px, label_height_px)
        self.label_vtasxcategoria.show()
        self.label_vtasxcategoria.update()

    def graficoFechas_change(self):
        tipo = self.graficoFechas.currentText()
        self.crear_grafico_ventas(tipo)





if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
