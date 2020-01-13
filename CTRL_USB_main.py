
import time
import sys
from PyQt5 import QtWidgets
from control_usb import Ui_Preferences  # импорт нашего сгенерированного файла
from myFunct_1 import myFunctions
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,
    QAction, QFileDialog, QApplication)
from PyQt5.QtGui import QIcon
from checkPorts import CheckPorts




class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.setWindowIcon(QIcon('logoUSB.png'))
        self.check = CheckPorts()
        self.check_p = None
        self.myF = myFunctions()
        self.ser_result = self.myF.serial_ports()
        self.len_o = 0
        self.ser = None
        self.textLogin = ['']
        self.textPassword = ['']
        self.Qstr = ''
        self.out = ''
        self.port = ''
        self.wait = 0
        self.connected = False
        self.start_switch = False
        self.device_number = 0
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.setWindowTitle("CONTROL USB")
        self.palette = QtGui.QPalette()
        self.i = 0
        self.dataArray = list()
        self.ui.Pot_1.valueChanged.connect(self.POT_Ctrl_0)
        self.ui.Pot_2.valueChanged.connect(self.POT_Ctrl_1)
        self.ui.Pot_3.valueChanged.connect(self.POT_Ctrl_2)
        self.ui.Pot_4.valueChanged.connect(self.POT_Ctrl_3)
        self.ui.Pot_5.valueChanged.connect(self.POT_Ctrl_4)
        self.ui.Super_Sonic_Left.valueChanged.connect(self.S_S_Sensor_Left)
        self.ui.Super_Sonic_Right.valueChanged.connect(self.SS_S_Sensor_Right)
        self.ui.SuperSonic_L_Button.toggled.connect(self.SS_But_Left)
        self.ui.SuperSonic_R_Button.toggled.connect(self.SS_But_Right)
        self.ui.Potentiometrs.toggled.connect(self.Pot_But)
        self.ui.MIDI_Channel_Slider.valueChanged.connect(self.MIDI_Channel_Slider)
        self.ui.Latency_Slider.valueChanged.connect(self.Latency_Slider)
        self.ui.Distance_min_Slider.valueChanged.connect(self.Distance_min)
        self.ui.Distance_max_Slider.valueChanged.connect(self.Distance_max)
        self.ui.Smooth_Slider.valueChanged.connect(self.Smoothing)
        self.ui.LED_Prog_Slider.valueChanged.connect(self.LED_Programm_Slider)
        self.ui.LED_Speed_Slider.valueChanged.connect(self.LED_Speed_Slider)
        self.ui.LED_Bright_Slider.valueChanged.connect(self.LED_Brightness_Slider)
        self.ui.Refresh.clicked.connect(self.Refresh)
        self.ui.Refresh.setToolTip('Load and Refresh all Parameters from Device')
        self.ui.Load_Preset.clicked.connect(self.showDialogRead)
        self.ui.Load_Preset.setToolTip('Load Preset from Disk')
        self.ui.Save_Preset.clicked.connect(self.showDialogWrite)
        self.ui.Save_Preset.setToolTip('Save Preset to Disk')
        self.ui.Quit.clicked.connect(self.Quit)
        self.ui.Quit.setToolTip('Exit')
        self.ui.Save.clicked.connect(self.Save_Param)
        self.ui.Save.setToolTip('Save Parameters to Device')
        self.data_Complicate = list()
        self.ui.COM_Ports.setText('')
        self.ui.Connecting.setVisible(True)
        QTimer.singleShot(10, self.device)





    def showDialogRead(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file', '')[0]
        try:
            f = open(fname, 'r')

            with f:
                d = f.read()
                data = d.split('\n')
                self.dataArray = data
            QTimer.singleShot(10, self.Save_Param)
            QTimer.singleShot(10, self.Refresh)
        except:
            pass



    def showDialogWrite(self):

        fname = QFileDialog.getSaveFileName(self, 'Save file', '')[0]
        del_ = fname.split('.')
        try:
            f = open(del_[0] + '.usb', 'w')
            for index in range(len(self.dataArray)):
                f.write(self.dataArray[index] + '\n')

            f.close()
        except:
            pass



    def serialConnect(self):
        self.len_o = len(self.ser_result) - 1
        self.ser = self.myF.serial_begin(self.ser_result, self.device_number)
        self.ser.isOpen()
        QTimer.singleShot(100, self.Start)

    def device(self):
        if self.connected is False:
            check = self.check_Ports()
            for i in range(len(self.ser_result)):
                if self.ser_result[i] == check:
                    self.device_number = i
                    self.serialConnect()
                    self.connected = True
                    self.ui.Connecting.setVisible(True)
                    QTimer.singleShot(1000, self.device)
                    break
                elif self.ser_result[i] != check:
                    self.ui.COM_Ports.setText('    NO DEVICE')
        try:
            self.ser.flush()
            QTimer.singleShot(1000, self.device)
        except:
            self.connected = False
            self.start_switch = False
            QTimer.singleShot(1000, self.device)
            self.ser_result = self.myF.serial_ports()
            self.ui.Connecting.setHidden(True)

    def Start(self):
        self.wait += 1

        if self.start_switch is False:
            try:
                self.ser.write('__CHECK_DEV__'.encode('utf_8') + b'\n')
                self.ser.flush()
            except OSError:
                QTimer.singleShot(1000, self.Start)

            try:
                while self.ser.inWaiting() > 0:
                    self.out += self.ser.read(1).decode()
                    out = self.out.split('\r\n')
                    if out[0] == 'WiFi Connected!':
                            out[0] = ''
                    for i in range(len(out)-1):
                        if out[i] == 'CONTROL_USB':
                            print('out[i] =>')
                            print(out[i])
                            self.start_switch = True
                            self.ui.COM_Ports.setText('CONTROL USB')
                            self.ui.Connecting.setVisible(True)
                            self.ui.Connecting.setText('   Loading...')
                            QTimer.singleShot(1200, self.Refresh)
                            self.layout().update()
                            self.switch_interval = True
                            self.out = ''
                            break
                        elif self.out != 'CONTROL_USB':
                             self.ui.Connecting.setHidden(True)
                             self.start_switch = False
                        elif self.start_switch:
                            break

                        if self.out != 'CONTROL_USB' and self.wait == 10:
                            print(self.wait)
                            self.check.switchChange()
                            self.connected = False
                            self.start_switch = False
                            self.ser.close()
                            self.device()
                            self.wait = 0
                            self.ui.Connecting.setHidden(True)
                            break
                else:
                    QTimer.singleShot(1000, self.Start)

            except:
                pass




    @pyqtSlot()



    def Save_Param(self):
        a = 0.1
        temp = [x.encode('utf-8') + b'\n' for x in self.dataArray]
        try:
            self.ser.write(' '.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write('__POT_Ctrl_0__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[0])
            time.sleep(a)
            self.ser.write('__POT_Ctrl_1__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[1])
            time.sleep(a)
            self.ser.write('__POT_Ctrl_2__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[2])
            time.sleep(a)
            self.ser.write('__POT_Ctrl_3__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[3])
            time.sleep(0.5 + a)
            self.ser.write('__POT_Ctrl_4__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[4])
            time.sleep(a)
            self.ser.write('__SS_Ctrl_L__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[5])
            time.sleep(a)
            self.ser.write('__SS_Ctrl_R__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[6])
            time.sleep(a)
            self.ser.write('__SS_B_L__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[7])
            time.sleep(a)
            self.ser.write('__SS_B_R__'.encode('utf_8') + b'\n')
            time.sleep(0.5+a)
            self.ser.write(temp[8])
            time.sleep(a)
            self.ser.write('__Pot_B__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[9])
            time.sleep(a)
            self.ser.write('__MIDI_Chan__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[10])
            time.sleep(a)
            self.ser.write('__Latency__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[11])
            time.sleep(0.5 + a)
            self.ser.write('__Dist_min__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[12])
            time.sleep(a)
            self.ser.write('__Dist_max__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[13])
            time.sleep(a)
            self.ser.write('__Smooth__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[14])
            time.sleep(a + 0.5)
            self.ser.write('__L_P__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[15])
            time.sleep(a)
            self.ser.write('__L_S__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[16])
            time.sleep(a)
            self.ser.write('__L_B__'.encode('utf_8') + b'\n')
            time.sleep(a)
            self.ser.write(temp[17])
            time.sleep(a)
            self.ser.write('__Save__'.encode('utf_8') + b'\n')
        except:
            pass

    def POT_Ctrl_0(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[0] = self.Qstr
            self.ser.write('__POT_Ctrl_0__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def POT_Ctrl_1(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[1] = self.Qstr
            self.ser.write('__POT_Ctrl_1__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def POT_Ctrl_2(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[2] = self.Qstr
            self.ser.write('__POT_Ctrl_2__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def POT_Ctrl_3(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[3] = self.Qstr
            self.ser.write('__POT_Ctrl_3__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def POT_Ctrl_4(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[4] = self.Qstr
            self.ser.write('__POT_Ctrl_4__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') +  b'\n')
            time.sleep(0.05)
        except:
            pass

    def S_S_Sensor_Left(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[5] = self.Qstr
            self.ser.write('__SS_Ctrl_L__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def SS_S_Sensor_Right(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[6] = self.Qstr
            self.ser.write('__SS_Ctrl_R__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def SS_But_Left(self, QString):
        try:
            self.Qstr = self.bool2str(QString)
            self.dataArray[7] = self.Qstr
            self.ser.write('__SS_B_L__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def SS_But_Right(self, QString):
        try:
            self.Qstr = self.bool2str(QString)
            self.dataArray[8] = self.Qstr
            self.ser.write('__SS_B_R__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def Pot_But(self, QString):
        try:
            self.Qstr = self.bool2str(QString)
            self.dataArray[9] = self.Qstr
            self.ser.write('__Pot_B__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def MIDI_Channel_Slider(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[10] = self.Qstr
            self.ser.write('__MIDI_Chan__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def Latency_Slider(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[11] = self.Qstr
            self.ser.write('__Latency__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def Distance_min(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[12] = self.Qstr
            self.ser.write('__Dist_min__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def Distance_max(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[13] = self.Qstr
            self.ser.write('__Dist_max__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def Smoothing(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[14] = self.Qstr
            self.ser.write('__Smooth__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def LED_Programm_Slider(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[15] = self.Qstr
            self.ser.write('__L_P__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def LED_Speed_Slider(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[16] = self.Qstr
            self.ser.write('__L_S__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass

    def LED_Brightness_Slider(self, QString):
        try:
            self.Qstr = str(QString)
            self.dataArray[17] = self.Qstr
            self.ser.write('__L_B__'.encode('utf_8') + b'\n')
            time.sleep(0.01)
            self.ser.write(self.Qstr.encode('utf_8') + b'\n')
            time.sleep(0.05)
        except:
            pass


    def Refresh(self):
        try:
            self.ser.write('__Refresh__'.encode('utf_8') + b'\n')
            self.Param_Loading(self.Recive_Dump())
            self.Update()
        except:
            QTimer.singleShot(1000, self.Refresh)



    def Update(self):
        #self.ui.COM_Ports.setText('CONTROL USB')
        self.layout().update()



    def Recive_Dump(self):
        out = ''
        self.ser.flush()
        time.sleep(0.15)
        self.ser.write('__SEND_D__'.encode('utf_8') + b'\n')
        time.sleep(1.2)
        while self.ser.inWaiting() > 0:
            out += self.ser.read(1).decode()
        return out


    def Param_Loading(self, outDump):
        res1 = outDump.split('\r\n')
        self.dataArray.clear()
        self.dataArray = res1
        self.ui.Pot_1.setValue(int(res1[0]))
        self.ui.Pot_2.setValue(int(res1[1]))
        self.ui.Pot_3.setValue(int(res1[2]))
        self.ui.Pot_4.setValue(int(res1[3]))
        self.ui.Pot_5.setValue(int(res1[4]))
        self.ui.Super_Sonic_Left.setValue(int(res1[5]))
        self.ui.Super_Sonic_Right.setValue(int(res1[6]))
        self.ui.SuperSonic_L_Button.setChecked(self.str2bool(res1[7]))
        self.ui.SuperSonic_R_Button.setChecked(self.str2bool(res1[8]))
        self.ui.Potentiometrs.setChecked(self.str2bool(res1[9]))
        self.ui.MIDI_Channel_Slider.setValue(int(res1[10]))
        self.ui.Latency_Slider.setValue(int(res1[11]))
        self.ui.Distance_min_Slider.setValue(int(res1[12]))
        self.ui.Distance_max_Slider.setValue(int(res1[13]))
        self.ui.Smooth_Slider.setValue(int(res1[14]))
        self.ui.LED_Prog_Slider.setValue(int(res1[15]))
        self.ui.LED_Speed_Slider.setValue(int(res1[16]))
        self.ui.LED_Bright_Slider.setValue(int(res1[17]))
        self.ui.Connecting.setVisible(False)
        print('res1 =>')
        print(res1)


    def check_Ports(self):
        check_p = self.check.checkPorts()
        return check_p

    def str2bool(self, v):
        return v.lower() in ("yes", "true", "t", "1")

    def bool2str(self, v):
        if v:
            return '1'
        else:
            return '0'

    def Quit(self):
        try:
            self.ser.close()
        except:
            pass
        sys.exit()

















# configure the serial connections (the parameters differs on the device you are cont
# connecting to)

#app1 = QtGui.QGuiApplication.instance()
#app1.setStyleSheet('QLabel{color: #fff;} QPushButton{background-color: #000; color: #fff}')
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()
    sys.exit(app.exec())

