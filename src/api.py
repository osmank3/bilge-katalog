#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

class qt_api(object):
    def __init__(self, window):
        self.__window = window
    
    def addMenu(self, ogeler):
        """"""
        pass
        
    def showDialog(self, ogeler):
        """"""
        pass
        
class db_api(object):
    def __init__(self, database):
        self.__db = database
        
    def get(self, pluginName, table, where=None, order=None):
        """"""
        pass
        
    def insert(self, pluginName, table, row):
        """"""
        pass
    
    def update(self, pluginName, table, row, where):
        """"""
        pass
        
    def delete(self, pluginName, table, where):
        """"""
        pass

class plug_api(object):
    def __init__(self, db, ui):
        self.db = db
        self.ui = ui