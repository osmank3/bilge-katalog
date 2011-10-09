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
        """
        function for taking data from database
        
        pluginName : ""
        table : ""
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        order : []
        
        returned : [{"key":"value", ...}, ...]
        """
        pass
        
    def insert(self, pluginName, table, row):
        """
        function for inserting row to database
        
        pluginName : ""
        table : ""
        row : {"key":"value", ...}
        """
        pass
    
    def update(self, pluginName, table, row, where):
        """
        function for updating the row where on the database
        
        pluginName : ""
        table : ""
        row : {"key":"value", ...}
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        """
        pass
        
    def delete(self, pluginName, table, where):
        """
        function for deleting anything from database
        
        pluginName : ""
        table : ""
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        """
        pass
    
    def createTable(self, pluginName, table, keys):
        """
        function for creating table on database
        
        pluginName : ""
        table : ""
        keys : {"key":{ "type":"TYPE","null":False,"auto":False,
                        "primary":False,"default":"DEFAULT"     }, ...}
        """
        pass

class plug_api(object):
    def __init__(self, db, ui):
        self.db = db
        self.ui = ui