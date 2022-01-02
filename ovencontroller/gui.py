"""Oven Controller Qt5 GUI"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from gui_views import *


DEFAULT_FONT = QtGui.QFont("Open Sans", pointSize=16)


def main(exit, argv):
	"""Main loop"""

	app = QtWidgets.QApplication(argv)
	app.setFont(DEFAULT_FONT)

	v_startup = StartupView()
	v_startup.show()

	ret = app.exec_()

	if exit is None:
		sys.exit(ret)


if __name__ == "__main__":
	# run gui by itself
	main(None, sys.argv)
