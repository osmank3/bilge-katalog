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
        self.cat = BilgeItem()
        self.exp = BilgeItem()
        self.disp = BilgeItem()
        if database and database.ready():
            self.db = database
    
    def setDatabase(self, database):
        if database and database.ready():
            self.db = database
        else:
            self.db = BilgeItem()
            self.cat = BilgeItem()
            self.exp = BilgeItem()
            self.disp = BilgeItem()
            
    def setCatalog(self, catalog):
        if catalog:
            self.cat = catalog
            self.cat.ready = lambda: True
        else:
            self.cat = BilgeItem()
            self.exp = BilgeItem()
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
    app = window.QtGui.QApplication(sys.argv)
    #get database object
    db = getDatabase(app)
    bilge = Bilge(database=db)
    
    if bilge.db.ready():
        #catalog functions
        cat = catalog
        bilge.setCatalog(cat)
        if bilge.cat.ready():
            #exploring database
            exp = bilge.cat.Explorer(bilge)
            bilge.setExplorer(exp)
            
            if bilge.exp.ready() and bilge.cat.ready():
                #creating gui
                win = window.MainWindow(bilge)
                bilge.setDisplay(win)
                
                #create api
                db_api = api.db_api(bilge)
                disp_api = api.disp_api(bilge)
                plug_api = api.plug_api(db_api, disp_api)
                
                getPlugins(plug_api)
                
                win.show()
                app.exec_()#sys.exit(app.exec_())
            else:
                print("Explorer error")
                return 2
        else:
            print("Catalog module error")
            return 2
    else:
        print("Database error")
        return 2
    
def getDatabase(app=None):
    if not app:
        app = dialogs.QtGui.QApplication(sys.argv)
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
            app.exec_()
            
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
