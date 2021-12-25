"""Oven Controller Qt5 GUI Views"""

from PyQt5 import QtCore, QtGui, QtWidgets


class StartupView(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Oven Controller")

		# root layout
		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.setContentsMargins(10, 10, 10, 10)
		self.layout.setSpacing(10)

		# widget grid
		self.grid = QtWidgets.QGridLayout()
		self.grid.setHorizontalSpacing(10)
		self.grid.setVerticalSpacing(0)

		# thermocouple 1 labels
		self.label_tc1 = QtWidgets.QLabel("TC1 MCP9601:", self)
		self.label_tc1.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.label_tc1, 0, 0, 1, 1)

		self.field_tc1 = QtWidgets.QLabel(self)
		self.field_tc1.setText("OK")
		self.field_tc1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.field_tc1, 0, 1, 1, 1)

		# thermocouple 2 labels
		self.label_tc2 = QtWidgets.QLabel("TC2 MCP9601:", self)
		self.grid.addWidget(self.label_tc2, 1, 0, 1, 1)

		self.field_tc2 = QtWidgets.QLabel(self)
		self.field_tc2.setText("OK")
		self.field_tc2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.field_tc2, 1, 1, 1, 1)

		# eeprom labels
		self.label_eeprom = QtWidgets.QLabel("EEPROM:", self)
		self.grid.addWidget(self.label_eeprom, 2, 0, 1, 1)

		self.field_eeprom = QtWidgets.QLabel(self)
		self.field_eeprom.setText("OK")
		self.field_eeprom.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.field_eeprom, 2, 1, 1, 1)

		self.layout.addLayout(self.grid)

		# test buzzer button
		self.btn_buzzer = QtWidgets.QPushButton("Test Buzzer", self)
		self.layout.addWidget(self.btn_buzzer)

		# spacer
		self.spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.layout.addItem(self.spacer)

		# continue button
		self.btn_continue = QtWidgets.QPushButton("Continue", self)
		self.layout.addWidget(self.btn_continue)
