#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui_firststart import Ui_ConfigForm

class configForm(QtGui.QDialog, Ui_ConfigForm):
    def __init__(self, config):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        self.config = config
        
        self.addressLine.setText(os.path.join(os.environ["HOME"],".bilge-katalog","sqlitedb"))
        
        #signals
        self.connect(self.nextButton, QtCore.SIGNAL("clicked()"), self.tryNext)
        self.connect(self.backButton, QtCore.SIGNAL("clicked()"), self.tryBack)
        self.connect(self.defaultButton, QtCore.SIGNAL("clicked()"), self.mysqlDefault)
    
    def tryNext(self):
        if self.stackedWidget.currentWidget() == self.p0:
            if self.sqliteRadio.isChecked():
                self.stackedWidget.setCurrentWidget(self.ps)
            elif self.mysqlRadio.isChecked():
                self.stackedWidget.setCurrentWidget(self.pm)
        elif self.stackedWidget.currentWidget() == self.ps:
            address = os.path.join(os.environ["HOME"],".bilge-katalog","sqlitedb")
            if not self.defaultCheck.isChecked() and self.addressLine.text():
                address = self.addressLine.text()
            setattr(self.config,"dbType","sqlite")
            setattr(self.config,"sqliteDbAddress",address)
            self.close()
        elif self.stackedWidget.currentWidget() == self.pm:
            if self.serverLine.text() and self.unameLine.text() and self.upassLine.text() and self.dbLine.text():
                setattr(self.config,"dbType","mysql")
                setattr(self.config,"mysqlServer",self.serverLine.text())
                setattr(self.config,"mysqlUserName",self.unameLine.text())
                setattr(self.config,"mysqlUserPass",self.upassLine.text())
                setattr(self.config,"mysqlDbName",self.dbLine.text())
                self.close()
    
    def tryBack(self):
        self.stackedWidget.setCurrentWidget(self.p0)
    
    def mysqlDefault(self):
        self.serverLine.setText("localhost")
        self.unameLine.setText("bilge")
        self.upassLine.setText("123456")
        self.dbLine.setText("bilgedb")

if __name__ == "__main__":
    class config():
        dbType = None
        sqliteDbAddress = None
        mysqlServer = None
        mysqlUserName = None
        mysqlUserPass = None
        mysqlDbName = None
    app = QtGui.QApplication(sys.argv)
    window = configForm(config())
    window.show()
    sys.exit(app.exec_())