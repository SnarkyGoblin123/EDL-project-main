from PyQt6 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget
from pyqtgraph import mkPen
import time
import intel_jtag_uart
import matplotlib.pyplot as plt
import numpy as np

# Determines values for time axis
ADC_CLOCK_FREQ = 1500000.0
ADC_TIME_PERIOD = 1000000/ADC_CLOCK_FREQ # In microseconds

time_array = [0]
current_time = 0
for i in range(40):
	current_time += 16*ADC_TIME_PERIOD
	time_array.append(current_time)

try:
	ju = intel_jtag_uart.intel_jtag_uart()

except Exception as e:
	print(e)
	#exit(0)

class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		#Main window init
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(800, 600)
		MainWindow.setMouseTracking(True)
		self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
		self.centralwidget.setObjectName("centralwidget")

		# Graph Widget
		self.graph = PlotWidget(parent=self.centralwidget)
		self.graph.setGeometry(QtCore.QRect(50, 230, 491, 261))
		self.graph.setObjectName("graph")
		self.graph.setBackground("w")
		self.graph.setLabel("left", "Voltage (V)")
		self.graph.setLabel("bottom", "Time (us)")

		self.graph.addLegend()
		self.lineStyle = mkPen(color=(255,0,0))
		self.line1 = self.graph.plot(range(10), range(1,11), name = "Vbias", pen = self.lineStyle)
		self.lineStyle = mkPen(color=(0,0,255))
		self.line2 = self.graph.plot(range(2,11), range(1,10), name = "Vsource",pen = self.lineStyle)
		
		# "Send pulse" buttom
		self.Exec = QtWidgets.QPushButton(parent=self.centralwidget)
		self.Exec.setGeometry(QtCore.QRect(80, 170, 141, 31))
		self.Exec.setObjectName("Exec")
		self.Exec.clicked.connect(self.send_pulse)
		
		# Labels
		self.PV_label = QtWidgets.QLabel(parent=self.centralwidget)
		self.PV_label.setGeometry(QtCore.QRect(30, 10, 121, 41))
		self.PV_label.setObjectName("PV_label")
		self.label_V = QtWidgets.QLabel(parent=self.centralwidget)
		self.label_V.setGeometry(QtCore.QRect(358, 20, 41, 20))
		self.label_V.setObjectName("label_V")
		
		# Slider
		self.V_Slider = QtWidgets.QSlider(parent=self.centralwidget)
		self.V_Slider.setGeometry(QtCore.QRect(140, 20, 131, 21))
		self.V_Slider.setMaximum(1900)
		self.V_Slider.setMinimum(-3500)
		self.V_Slider.setSingleStep(10)
		self.V_Slider.setPageStep(500)
		self.V_Slider.setProperty("value", 0)
		self.V_Slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
		self.V_Slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBothSides)
		self.V_Slider.setTickInterval(500)
		self.V_Slider.setObjectName("V_Slider")
		self.V_Slider.valueChanged.connect(self.SlideUpdate)
		
		# Text field for Voltage value
		self.Volt_Display = QtWidgets.QLineEdit(parent=self.centralwidget)
		self.Volt_Display.setGeometry(QtCore.QRect(300, 20, 41, 21))
		self.Volt_Display.setObjectName("Volt_Display")
		self.Volt_Display.editingFinished.connect(self.TextUpdate)
		
		# Resistance display table
		self.CrossbarTable = QtWidgets.QTableWidget(parent=self.centralwidget)
		self.CrossbarTable.setGeometry(QtCore.QRect(280, 50, 320, 120))
		self.CrossbarTable.setMouseTracking(True)
		self.CrossbarTable.setAcceptDrops(False)
		self.CrossbarTable.setObjectName("CrossbarTable")
		self.CrossbarTable.setColumnCount(3)
		self.CrossbarTable.setRowCount(3)
		self.CrossbarTable.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)

		# Word line selection
		self.WL_group = QtWidgets.QButtonGroup(MainWindow)
		self.WL_group.setObjectName("WL_group")
		self.WL_1 = QtWidgets.QRadioButton(parent=self.centralwidget)
		self.WL_1.setGeometry(QtCore.QRect(30, 70, 50, 20))
		self.WL_1.setObjectName("WL_1")
		self.WL_group.addButton(self.WL_1)
		self.WL_group.setId(self.WL_1,1)
		self.WL_2 = QtWidgets.QRadioButton(parent=self.centralwidget)
		self.WL_2.setGeometry(QtCore.QRect(30, 100, 50, 20))
		self.WL_2.setObjectName("WL_2")
		self.WL_group.addButton(self.WL_2)
		self.WL_group.setId(self.WL_2,2)
		self.WL_3 = QtWidgets.QRadioButton(parent=self.centralwidget)
		self.WL_3.setGeometry(QtCore.QRect(30, 130, 50, 20))
		self.WL_3.setObjectName("WL_3")
		self.WL_group.addButton(self.WL_3)
		self.WL_group.setId(self.WL_3,3)
		
		# Bit line selection
		self.BL_group = QtWidgets.QButtonGroup(MainWindow)
		self.BL_group.setObjectName("BL_group")
		self.BL_3 = QtWidgets.QRadioButton(parent=self.centralwidget)
		self.BL_3.setGeometry(QtCore.QRect(100, 130, 50, 20))
		self.BL_3.setObjectName("BL_3")
		self.BL_group.addButton(self.BL_3)
		self.BL_group.setId(self.BL_3,3)
		self.BL_2 = QtWidgets.QRadioButton(parent=self.centralwidget)
		self.BL_2.setGeometry(QtCore.QRect(100, 100, 50, 20))
		self.BL_2.setObjectName("BL_2")
		self.BL_group.addButton(self.BL_2)
		self.BL_group.setId(self.BL_2,2)
		self.BL_1 = QtWidgets.QRadioButton(parent=self.centralwidget)
		self.BL_1.setGeometry(QtCore.QRect(100, 70, 50, 20))
		self.BL_1.setObjectName("BL_1")
		self.BL_group.addButton(self.BL_1)
		self.BL_group.setId(self.BL_1,1)

		# Resistor Selection
		self.Rgroup = QtWidgets.QButtonGroup(MainWindow)
		self.Rsense = QtWidgets.QGroupBox(parent=self.centralwidget)
		self.Rsense.setGeometry(QtCore.QRect(170, 50, 90, 111))
		self.Rsense.setObjectName("Rsense")
		self.RS_1 = QtWidgets.QRadioButton(parent=self.Rsense)
		self.RS_1.setGeometry(QtCore.QRect(10, 20, 89, 20))
		self.RS_1.setObjectName("RS_1")
		self.RS_2 = QtWidgets.QRadioButton(parent=self.Rsense)
		self.RS_2.setGeometry(QtCore.QRect(10, 50, 89, 20))
		self.RS_2.setObjectName("RS_2")
		self.RS_3 = QtWidgets.QRadioButton(parent=self.Rsense)
		self.RS_3.setGeometry(QtCore.QRect(10, 80, 89, 20))
		self.RS_3.setObjectName("RS_3")
		self.Rgroup.addButton(self.RS_3)
		self.Rgroup.setId(self.RS_3,3)
		self.Rgroup.addButton(self.RS_2)
		self.Rgroup.setId(self.RS_2,2)
		self.Rgroup.addButton(self.RS_1)
		self.Rgroup.setId(self.RS_1,1)

		# Boxes
		self.WordGroup = QtWidgets.QGroupBox(parent=self.centralwidget)
		self.WordGroup.setGeometry(QtCore.QRect(10, 50, 75, 111))
		self.WordGroup.setObjectName("WordGroup")
		self.BitGroup = QtWidgets.QGroupBox(parent=self.centralwidget)
		self.BitGroup.setGeometry(QtCore.QRect(80, 50, 75, 111))
		self.BitGroup.setObjectName("BitGroup")

		# Finishing touches
		self.Table_desc = QtWidgets.QLabel(parent=self.centralwidget)
		self.Table_desc.setGeometry(QtCore.QRect(300, 170, 291, 20))
		self.Table_desc.setObjectName("Table_desc")
		self.BitGroup.raise_()
		self.WordGroup.raise_()
		self.Exec.raise_()
		self.PV_label.raise_()
		self.V_Slider.raise_()
		self.Volt_Display.raise_()
		self.CrossbarTable.raise_()
		self.WL_1.raise_()
		self.WL_2.raise_()
		self.WL_3.raise_()
		self.BL_3.raise_()
		self.BL_2.raise_()
		self.BL_1.raise_()
		self.Rsense.raise_()
		self.Table_desc.raise_()
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
		self.Exec.setText(_translate("MainWindow", "Send pulse"))
		self.PV_label.setText(_translate("MainWindow", "Pulse Voltage"))
		self.WL_1.setText(_translate("MainWindow", "1"))
		self.WL_2.setText(_translate("MainWindow", "2"))
		self.WL_3.setText(_translate("MainWindow", "3"))
		self.BL_3.setText(_translate("MainWindow", "3"))
		self.BL_2.setText(_translate("MainWindow", "2"))
		self.BL_1.setText(_translate("MainWindow", "1"))
		self.Rsense.setTitle(_translate("MainWindow", "Rsense"))
		self.RS_2.setText(_translate("MainWindow", "10k"))
		self.RS_3.setText(_translate("MainWindow", "Write"))
		self.RS_1.setText(_translate("MainWindow", "30k"))
		self.WordGroup.setTitle(_translate("MainWindow", "Word Line"))
		self.BitGroup.setTitle(_translate("MainWindow", "Bit line"))
		self.Table_desc.setText(_translate("MainWindow", "Calculated Crossbar Resistance Values, in Kilo Ohms"))
		self.Volt_Display.setText("0")
		self.label_V.setText(_translate("MainWindow", "Volts"))

	def SlideUpdate(self, val):
		self.Volt_Display.setText(str(val/1000.0))

	def TextUpdate(self):
		try:
			val = int(float(self.Volt_Display.text())*1000)
			if (val >= -5000 and val <= 5000):
				self.V_Slider.setProperty("value", val)
			else:
				self.Volt_Display.setText(str(self.V_Slider.value()/1000.0))
		except:
			self.Volt_Display.setText(str(self.V_Slider.value()/1000.0))

	# Function which activates when control signals to the FPGA.
	# THIS is the function that actually interacts with jtag UART
	def send_pulse(self):

		BL_no = self.BL_group.checkedId()
		WL_no = self.WL_group.checkedId()
		R_no = self.Rgroup.checkedId()

		# Send sequence
		DAC_num = int(((1<<12)-1)*(float(self.Volt_Display.text())+16)/25)
		byte_1 = ((1<<R_no)<<4) + (1<<WL_no)
		ju.write(byte_1.to_bytes(1, byteorder = 'big'))
		byte_2 =((15-(1<<BL_no))<<4) + (DAC_num>>8)
		ju.write(byte_2.to_bytes(1, byteorder = 'big'))
		byte_3 = DAC_num%(1<<8)
		ju.write(byte_3.to_bytes(1, byteorder = 'big'))
		print (str(byte_1)+  " "+ str(byte_2)+ " " + str(byte_3))

		# Read sequence
		time.sleep(0.1)
		byte_parity = False
		while (ju.bytes_available() ==0):
			continue
		list = ju.read()

		new_list_1 = []
		new_list_2 = []
		byte_parity = False

		# Remove dummy zero if present
		if(len(list)%2 == 1):
			list = list[1:]

		x = int(len(list)/2)
		# Create arrays for plotting
		for i in range(x):
			new_val = 2*(((list[2*i]<<8) + list[2*i + 1])*3.3/((1<<12)-1)) - 5
			if(byte_parity):
				new_list_2.append(new_val)
			else:
				new_list_1.append(new_val)
			byte_parity = not byte_parity

		new_list_1 = new_list_1[1:] #First values are garbage
		new_list_2 = new_list_2[1:]

		self.line1.setData(time_array[:len(new_list_2)], new_list_2)
		self.line2.setData(time_array[:len(new_list_1)], new_list_1)

		Rsense = 10 if (R_no == 2) else 30 # Kilo Ohm values
		# If read, update table with calculated resistance
		if (R_no != 3):
			R_array = []
			for i in range(len(new_list_1)):
				R_array.append(Rsense/(new_list_1[i]/new_list_2[i] - 1))
			
			Resistance_val = np.mean(R_array)
			self.CrossbarTable.setItem(BL_no-1, WL_no-1, QtWidgets.QTableWidgetItem(str(Resistance_val)))
			print(Resistance_val)

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	app.exec()
	ju.close()
	sys.exit()
