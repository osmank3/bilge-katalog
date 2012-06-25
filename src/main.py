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

class BilgeItem(object):
    def ready():
        return False

class Bilge(object):
    def __init__(self, database=None):
        self.db = BilgeItem()
        self.exp = BilgeItem()
        self.disp = BilgeItem()
        if database and database.ready():
            self.db = database
    
    def setDatabase(self, database):
        if database and database.ready():
            self.db = database
        else:
            self.db = BilgeItem()
            self.exp = BilgeItem()
            self.disp = BilgeItem()
            
    def setCatalog(self, catalog):
        if catalog:
            self.cat = catalog
            self.cat.ready = lambda: True
        else:
            self.cat = BilgeItem()
            self.disp = BilgeItem()
    
    def setExplorer(self, explorer):
        if explorer and explorer.ready():
            self.exp = explorer
        else:
            self.exp = BilgeItem()
            self.disp = BilgeItem()
    
    def setDisplay(self, display):
        if display and display.ready():
            self.disp = display
        else:
            self.disp = BilgeItem()

def startApp():
    #get database object
    db = getDatabase()
    bilge = Bilge(database=db)
    
    if bilge.db.ready():
        #catalog functions
        cat = catalog
        bilge.setCatalog(cat)
        #exploring database
        exp = catalog.Explorer(bilge)
        bilge.setExplorer(exp)
        
        if bilge.exp.ready() and bilge.cat.ready():
            #creating gui
            app = window.QtGui.QApplication(sys.argv)
            win = window.MainWindow(bilge)
            bilge.setDisplay(win)
            
            #create api
            db_api = api.db_api(db)
            qt_api = api.qt_api(win)
            plug_api = api.plug_api(db_api, qt_api)
            
            getPlugins(plug_api)
            
            win.show()
            app.exec_()#sys.exit(app.exec_())
        else:
            print("Explorer error")
            return 2
    else:
        print("Database error")
        return 2
    
def getDatabase():
    confApp = None
    maxturn = 5
    turn = 0
    
    while turn < maxturn:
        turn += 1
        
        exception = None
        
        config = database.ConfigForDb()
        if config.readConfig() == False:
            if not confApp:
                confApp = dialogs.QtGui.QApplication(sys.argv)
                dialog = dialogs.forms()
                
            exception = "config"
            dialog.setForConfig(config)
        else:
            try:
                db = database.mountDb(config)
            except Exception, e:
                if not confApp:
                    confApp = dialogs.QtGui.QApplication(sys.argv)
                    dialog = dialogs.forms()
                    
                if e[0] == 2002:
                    exception = "server"
                    dialog.setForMysqlServer(config)
                elif e[0] in [1044,1045,1049]:
                    exception = "create"
                    dialog.setForMysqlCreate(config, database)
                else:
                    exception = e
                    db = None
        
        if exception:
            if exception not in ["server","config","create"]:
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
