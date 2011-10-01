#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui_window import Ui_MainWindow

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.setToolBars()
    
    def setToolBars(self):
        """Adding toolbars actions"""
        self.ExpBar.addAction(self.actBack)
        self.ExpBar.addAction(self.actNext)
        self.ExpBar.addAction(self.actUp)
        self.ExpBar.addAction(self.actRefresh)
        
        self.EditBar.addAction(self.actCut)
        self.EditBar.addAction(self.actCopy)
        self.EditBar.addAction(self.actPaste)
        self.EditBar.addAction(self.actDel)
        
        self.searchLine = QtGui.QLineEdit()
        self.searchButton = QtGui.QPushButton()
        self.searchButton.setObjectName("searchButton")
        self.SearchBar.addWidget(self.searchLine)
        self.SearchBar.addWidget(self.searchButton)


#testing lines start in here
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())