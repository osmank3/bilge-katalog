#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

import libs.database as database
import libs.catalog as catalog
import window
import dialogs
import api

def startApp():
    #get database object
    db = getDatabase()
    
    #exploring database
    exp = catalog.Explore(db)
    
    #creating gui
    app = window.QtGui.QApplication(sys.argv)
    win = window.MainWindow(exp)
    
    #create api
    db_api = api.db_api(db)
    qt_api = api.qt_api(win)
    plug_api = api.plug_api(db_api, qt_api)
    
    getPlugins(plug_api)
    
    win.show()
    app.exec_()#sys.exit(app.exec_())
    
def getDatabase():
    confApp = dialogs.QtGui.QApplication(sys.argv)
    dialog = dialogs.forms()
    
    maxturn = 5
    turn = 0
    
    while turn < maxturn:
        turn += 1
        
        exception = None
        
        config = database.ConfigForDb()
        if config.readConfig() == False:
            exception = "config"
            dialog.setForConfig(config)
        else:
            try:
                db = database.mountDb(config)
            except Exception, e:
                if e[0] == 2002:
                    exception = "server"
                    dialog.setForMysqlServer(config)
                if e[0] in [1044,1045,1049]:
                    exception = "create"
                    dialog.setForMysqlCreate(config, database)
                else:
                    exception = e
                    db = None
        
        if exception:
            if exception not in ["config","create"]:
                dialog.setForException(exception)
                turn = maxturn
                
            dialog.show()
            confApp.exec_()
            
            if exception in ["config","create"]:
                config.writeConfig()
        
        else:
            return db
            
        if turn == maxturn:
            sys.exit()

def getPlugins(api):
    pass

if __name__ == "__main__":
    startApp()