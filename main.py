from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice, QPoint, Qt
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtGui import QResizeEvent
import numpy as np
import pyqtgraph as pg
import sys
import logging
import pyfirmata

# Configuración del registro de errores
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)


class MyApp(QMainWindow):
        def __init__(self):
                super(MyApp, self).__init__()
                uic.loadUi('HMI_Brazo.ui', self)
                
                self.bt_normal.hide()
                self.click_posicion = QPoint()
                self.bt_minimizar.clicked.connect(lambda : self.showMinimized())
                self.bt_normal.clicked.connect(self.control_bt_normal)
                self.bt_maximizar.clicked.connect(self.control_bt_maximizar)
                self.bt_cerrar.clicked.connect(lambda : self.close())
                
                # Eliminar barra de titulo y opacidad
                
                self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
                self.setWindowOpacity(1)
                self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                
                # SiceGrid
                
                self.gripSize = 10
                self.grip = QtWidgets.QSizeGrip(self)
                self.grip.resize(self.gripSize, self.gripSize)
                
                # Mover ventana
                
                self.frame_superior.mouseMoveEvent = self.mover_ventana
                
                # Control connect
                self.serial = QSerialPort()
                self.bt_update.clicked.connect(self.read_ports)
                self.bt_connect.clicked.connect(self.serial_connect)
                self.bt_disconnect.clicked.connect(self.serial_disconnect)     
                
                
                # Variables y componentes adicionales
                
                self.trackBarServo1.valueChanged.connect(lambda: self.update_servo(1, self.trackBarServo1.value()))
                self.trackBarServo2.valueChanged.connect(lambda: self.update_servo(2, self.trackBarServo2.value()))
                self.trackBarServo3.valueChanged.connect(lambda: self.update_servo(3, self.trackBarServo3.value()))
                self.trackBarServo4.valueChanged.connect(lambda: self.update_servo(4, self.trackBarServo4.value()))
                self.trackBarServo5.valueChanged.connect(lambda: self.update_servo(5, self.trackBarServo5.value()))
                
                self.buttonAvanzar.clicked.connect(lambda: self.send_command("$Bizq"))
                self.buttonRetroceder.clicked.connect(lambda: self.send_command("$Bder"))
                self.buttonParar.clicked.connect(lambda: self.send_command("$Bstop"))
                
                self.disable_components()       
               
                # Inicializar conexión pyFirmata
        
                        
                
                
        #######################################################
        
        
        def read_ports(self):
                try:
                        self.baudrates = ['1200', '2400', '4800', '9600', '19200', '38400', '115200']
                        portList = [port.portName() for port in QSerialPortInfo().availablePorts()]
                        
                        self.cb_list_ports.clear()
                        self.cb_list_baudrates.clear()
                        self.cb_list_ports.addItems(portList)
                        self.cb_list_baudrates.addItems(self.baudrates)
                        self.cb_list_baudrates.setCurrentText("9600")
                except Exception as error:
                        logging.error(f"Error reading ports: {str(error)}")
                        QMessageBox.warning(self, "Error", "Error al leer los puertos. Verifique la conexión del hardware.")
                        
                
        def serial_connect(self):
                try:
                        self.port = self.cb_list_ports.currentText()
                        self.baud = self.cb_list_baudrates.currentText()
                        
                        if not self.port or not self.baud:
                                raise ValueError("Seleccione un puerto y una tasa de baudios válidos.")
                                
                        self.serial.setBaudRate(int(self.baud))
                        self.serial.setPortName(self.port)
                        self.serial.open(QIODevice.ReadWrite)
                        self.serial.readyRead.connect(self.serial_read_data)
                        
                        self.progressBarConection.setValue(100)
                        self.bt_connect.setText("Desconectar")
                        self.bt_update.setEnabled(False)
                        self.enable_components()
                except Exception as error:
                        logging.error(f"Error connecting to serial port: {str(error)}")
                        QMessageBox.warning(self, "Error", "Error al conectar con el puerto serie. Verifique la conexión del hardware.")
                        
                
        def serial_disconnect(self):
                try:
                        self.disable_components()
                        self.progressBarConection.setValue(0)
                        self.bt_connect.setText("Conectar")
                        self.bt_update.setEnabled(True)
                        self.send_command("$S0")  # Detener servos y banda de manera segura
                        self.serial.close()
                except Exception as error:
                        logging.error(f"Error disconnecting from serial port: {str(error)}")
                        QMessageBox.warning(self, "Error", "Error al desconectar del puerto serie.")
        
        def enable_components(self):
                self.trackBarServo1.setEnabled(True)
                self.trackBarServo2.setEnabled(True)
                self.trackBarServo3.setEnabled(True)
                self.trackBarServo4.setEnabled(True)
                self.trackBarServo5.setEnabled(True)
                
                self.buttonAvanzar.setEnabled(True)
                self.buttonRetroceder.setEnabled(True)
                self.buttonParar.setEnabled(True)
                
        def disable_components(self):
                self.trackBarServo1.setValue(0)
                self.trackBarServo1.setEnabled(False)
                
                self.trackBarServo2.setValue(0)
                self.trackBarServo2.setEnabled(False)
                
                self.trackBarServo3.setValue(0)
                self.trackBarServo3.setEnabled(False)
                
                self.trackBarServo4.setValue(0)
                self.trackBarServo4.setEnabled(False)
                
                self.trackBarServo5.setValue(0)
                self.trackBarServo5.setEnabled(False)
                
                self.buttonAvanzar.setEnabled(False)
                self.buttonRetroceder.setEnabled(False)
                self.buttonParar.setEnabled(False)
                
                self.labelInfo1.setText("0°")
                self.labelInfo2.setText("0°")
                self.labelInfo3.setText("0°")
                self.labelInfo4.setText("0°")
                self.labelInfo5.setText("0°")
                
        def update_servo(self, servo_num, value):
                try:
                        label = getattr(self, f"labelInfo{servo_num}")
                        label.setText(f"{value}°")
                        self.send_command(f"$S{servo_num}{value}")
                        logging.debug(f"Servo {servo_num} set to {value} degrees.")
                except Exception as error:
                        logging.error(f"Error updating servo {servo_num}: {str(error)}")
                        QMessageBox.warning(self, "Error", str(error))
                        
        def send_command(self, command):
                try:
                        if self.serial.isOpen():
                                self.serial.write(command.encode())
                                logging.debug(f"Sent command: {command}")
                        else:
                                logging.warning("Serial port is not open.")
                except Exception as error:
                        logging.error(f"Error sending command '{command}': {str(error)}")
                        QMessageBox.warning(self, "Error", str(error))
            
            
        def serial_read_data(self):
                try:
                        if self.serial.canReadLine():
                                data = self.serial.readLine().data().decode().strip()
                                print(data)  # Do something with the data
                except Exception as error:
                        logging.error(f"Error reading serial data: {str(error)}")             
               
        def control_bt_normal(self):
                self.showNormal()
                self.bt_normal.hide()
                self.bt_maximizar.show()
                
        def control_bt_maximizar(self):
                self.showMaximized()
                self.bt_maximizar.hide()
                self.bt_normal.show()
                
        ######### SizeGrid
        
        ######### Mover Ventana
        
        def mousePressEvent(self, event):
                self.click_posicion = event.globalPos()
                
        def mover_ventana(self, event):
                if self.isMaximized() == False:
                        if event.buttons() == QtCore.Qt.LeftButton:
                                self.move(self.pos() + event.globalPos() - self.click_posicion) 
                                self.click_posicion = event.globalPos()
                                event.accept()
                        if event.globalPos().y() <=5 or event.globalPos().x() <=5:
                                self.showMaximized()
                                self.bt_maximizar.hide()
                                self.bt_normal.show()
                        else:
                                self.showNormal()
                                self.bt_normal.hide()
                                self.bt_maximizar.show()
                
if __name__ == '__main__':
        app = QApplication(sys.argv)
        my_app = MyApp()
        my_app.show()
        sys.exit(app.exec_())
                
                
