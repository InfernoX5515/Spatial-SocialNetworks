from PyQt5 import QtGui, QtCore, QtWidgets

def statusBar(self):
    self.statusBar = QtWidgets.QStatusBar()
    self.loadingTime = QtWidgets.QLabel("Load Time")
    self.statusBar.addPermanentWidget(self.loadingTime)
    self.setStatusBar(self.statusBar)