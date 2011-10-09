#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

import libs.database as database
import libs.catalog as catalog
import window
import api

def startApp():
    config = database.ConfigForDb()
    if config.readConfig() == False:
        return #burada bir ayar penceresi açılsın ve ayar yaptırsın
    
    try:
        db = database.mountDb(config)
    except Exception, e:
        return #burada da hata ile ilgili bir diyalog penceresi iş görür
    
    #creating gui
    app = window.QtGui.QApplication(sys.argv)
    win = window.MainWindow()
    
    #create api
    db_api = api.db_api(db)
    qt_api = api.qt_api(win)
    plug_api = api.plug_api(db_api, qt_api)
    
    getPlugins(plug_api)
    
    win.show()
    sys.exit(app.exec_())

def getPlugins(api):
    pass

if __name__ == "__main__":
    startApp()