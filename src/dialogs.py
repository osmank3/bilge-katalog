#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui_dialogs import Ui_Dialog

class forms(QtGui.QDialog, Ui_Dialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        #signals
        self.connect(self.mcp_nextButton, QtCore.SIGNAL("clicked()"), self.mcp_next)
        self.connect(self.msp_tryButton, QtCore.SIGNAL("clicked()"), self.msp_try)
        self.connect(self.ap_backButton, QtCore.SIGNAL("clicked()"), self.ap_back)
        self.connect(self.ap_createButton, QtCore.SIGNAL("clicked()"), self.ap_create)
        self.connect(self.cp_nextButton, QtCore.SIGNAL("clicked()"), self.cp_next)
        self.connect(self.sp_addressButton, QtCore.SIGNAL("clicked()"), self.sp_address)
        self.connect(self.sp_backButton, QtCore.SIGNAL("clicked()"), self.sp_back)
        self.connect(self.sp_applyButton, QtCore.SIGNAL("clicked()"), self.sp_apply)
        self.connect(self.mp_defaultButton, QtCore.SIGNAL("clicked()"), self.mp_default)
        self.connect(self.mp_tryButton, QtCore.SIGNAL("clicked()"), self.mp_try)
        self.connect(self.mp_backButton, QtCore.SIGNAL("clicked()"), self.mp_back)
        self.connect(self.mp_applyButton, QtCore.SIGNAL("clicked()"), self.mp_apply)
    
    #signal's functions
    def mcp_next(self):
        if self.mcp_changeRadio.isChecked():
            pass#stackwidget ilgili sayfayı gösterecek
        elif self.mcp_authRadio.isChecked():
            self.stackWidget.setCurrentWidget(self.authPage)
        elif self.mcp_yourselfRadio.isChecked():
            pass#stackwidget ilgili sayfayı gösterecek
            
    def msp_try(self):
        pass#mysql server'e bağlanılıp bağlanılmadığını kontrol edecek
        
    def ap_back(self):
        self.stackWidget.setCurrentWidget(self.mysqlCreatePage)
        
    def ap_create(self):
        pass#mysql'e yetkili ile bağlanıp yeni kullanıcı oluşturacak
        
    def cp_next(self):
        if self.cp_sqliteRadio.isChecked():
            self.sp_addressLine.setText(os.path.join(os.environ["HOME"],".bilge-katalog","sqlitedb"))
            self.stackedWidget.setCurrentWidget(self.sqlitePage)
        elif self.cp_mysqlRadio.isChecked():
            self.stackedWidget.setCurrentWidget(self.mysqlPage)
            
    def sp_address(self):
        address = QtGui.QFileDialog.getSaveFileName(self, directory = "sqlitedb")
        if not address.isEmpty():
            self.sp_addressLine.setText(address)
        
    def sp_back(self):
        self.stackedWidget.setCurrentWidget(self.confPage)
        
    def sp_apply(self):
        address = os.path.join(os.environ["HOME"],".bilge-katalog","sqlitedb")
        if not self.sp_defaultCheck.isChecked() and self.sp_addressLine.text():
            address = self.sp_addressLine.text()
        setattr(self.confObj,"dbType","sqlite")
        setattr(self.confObj,"sqliteDbAddress",address)
        self.close()
    
    def mp_default(self):
        self.mp_serverLine.setText("localhost")
        self.mp_unameLine.setText("bilge")
        self.mp_upassLine.setText("123456")
        self.mp_dbLine.setText("bilgedb")
        
    def mp_try(self):
        pass#mysql veritabanının bağlanılıp bağlanılmadığını kontrol edecek
    
    def mp_back(self):
        if self.mp_tryButton.isVisible():
            self.stackedWidget.setCurrentWidget(self.mysqlServerPage)
        else:
            self.stackedWidget.setCurrentWidget(self.confPage)
        
    def mp_apply(self):
        if self.mp_serverLine.text() and self.mp_unameLine.text() and self.mp_upassLine.text() and self.mp_dbLine.text():
            setattr(self.confObj,"dbType","mysql")
            setattr(self.confObj,"mysqlServer",self.mp_serverLine.text())
            setattr(self.confObj,"mysqlUserName",self.mp_unameLine.text())
            setattr(self.confObj,"mysqlUserPass",self.mp_upassLine.text())
            setattr(self.confObj,"mysqlDbName",self.mp_dbLine.text())
            self.close()
        
    #signal's functions end
    
    def setForConfig(self, conf):
        self.confObj = conf
        self.stackedWidget.setCurrentWidget(self.confPage)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = forms()
    if "config" in sys.argv:
        class config():
            dbType = None
            sqliteDbAddress = None
            mysqlServer = None
            mysqlUserName = None
            mysqlUserPass = None
            mysqlDbName = None
        window.setForConfig(config())
    window.show()
    sys.exit(app.exec_())
