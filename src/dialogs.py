#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
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
        self.connect(self.msp_closeButton, QtCore.SIGNAL("clicked()"), self.msp_close)
        self.connect(self.msp_tryButton, QtCore.SIGNAL("clicked()"), self.msp_try)
        self.connect(self.ap_backButton, QtCore.SIGNAL("clicked()"), self.ap_back)
        self.connect(self.ap_createButton, QtCore.SIGNAL("clicked()"), self.ap_create)
        self.connect(self.cp_backButton, QtCore.SIGNAL("clicked()"), self.cp_back)
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
            self.cp_backButton.setVisible(True)
            self.stackedWidget.setCurrentWidget(self.confPage)
            
        elif self.mcp_authRadio.isChecked():
            self.stackedWidget.setCurrentWidget(self.authPage)
            
        elif self.mcp_yourselfRadio.isChecked():
            #set buttons visibility
            self.mp_tryButton.setVisible(True)
            self.mp_defaultButton.setVisible(False)
            self.mp_applyButton.setVisible(False)
            
            #set lines text and writability
            self.mp_serverLine.setText(self.confObj.mysqlServer)
            self.mp_serverLine.setReadOnly(True)
            self.mp_unameLine.setText(self.confObj.mysqlUserName)
            self.mp_unameLine.setReadOnly(True)
            self.mp_upassLine.setText(self.confObj.mysqlUserPass)
            self.mp_upassLine.setReadOnly(True)
            self.mp_dbLine.setText(self.confObj.mysqlDbName)
            self.mp_dbLine.setReadOnly(True)
            
            self.stackedWidget.setCurrentWidget(self.mysqlPage)
            
    def msp_close(self):
        sys.exit()
    
    def msp_try(self):
        self.close()
        
    def ap_back(self):
        self.stackedWidget.setCurrentWidget(self.mysqlCreatePage)
        
    def ap_create(self):
        config = self.database.ConfigForDb()
        setattr(config,"dbType",self.confObj.dbType)
        setattr(config,"mysqlServer",self.confObj.mysqlServer)
        setattr(config,"mysqlUserName",str(self.ap_unameLine.text()))
        setattr(config,"mysqlUserPass",str(self.ap_upassLine.text()))
        setattr(config,"mysqlDbName","")
        try:
            db = self.database.mountDb(config)
            try:
                trydb = self.database.mountDb(self.confObj)
            except Exception as e:
                if e[0] == 1045:
                    db.createUser(self.confObj)    
            db.createDatabase(self.confObj)
            db.prepareTable()
            
            self.close()
        except Exception as e:
            print(e)
        
    def cp_back(self):
        self.stackedWidget.setCurrentWidget(self.mysqlCreatePage)
        
    def cp_next(self):
        if self.cp_sqliteRadio.isChecked():
            self.sp_addressLine.setText(os.path.join(os.environ["HOME"],".bilge-katalog","sqlitedb"))
            self.stackedWidget.setCurrentWidget(self.sqlitePage)
            
        elif self.cp_mysqlRadio.isChecked():
            #set buttons visibility
            self.mp_tryButton.setVisible(False)
            self.mp_defaultButton.setVisible(True)
            self.mp_applyButton.setVisible(True)
            
            #set lines writability
            self.mp_serverLine.setReadOnly(False)
            self.mp_unameLine.setReadOnly(False)
            self.mp_upassLine.setReadOnly(False)
            self.mp_dbLine.setReadOnly(False)
            
            self.mp_default()
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
        self.close()
    
    def mp_back(self):
        if self.mp_tryButton.isVisible():
            self.stackedWidget.setCurrentWidget(self.mysqlCreatePage)
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
    
    def setForException(self, exception):
        self.ep_text.setPlainText(str(exception))
        self.stackedWidget.setCurrentWidget(self.exceptPage)

    def setForMysqlCreate(self, conf, database):
        self.confObj = conf
        self.database = database
        self.stackedWidget.setCurrentWidget(self.mysqlCreatePage)
    
    def setForConfig(self, conf):
        self.confObj = conf
        self.stackedWidget.setCurrentWidget(self.confPage)
        
    def setForMysqlServer(self, conf):
        self.confObj = conf
        self.stackedWidget.setCurrentWidget(self.mysqlServerPage)


#testing lines start in here
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = forms()
    class config():
        dbType = None
        sqliteDbAddress = None
        mysqlServer = ""
        mysqlUserName = ""
        mysqlUserPass = ""
        mysqlDbName = ""
    if "config" in sys.argv:
        window.setForConfig(config())
    elif "create" in sys.argv:
        import libs.database as database
        window.setForMysqlCreate(config(), database)
    elif "server" in sys.argv:
        window.setForMysqlServer(config())
    else:
        window.setForException(" ".join(sys.argv[1:]))
    window.show()
    sys.exit(app.exec_())
