#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
from hsaudiotag import auto

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

class Main(object):
    def __init__(self, api):
        self.name = "MusicInfo"
        self.api = api
        self.tableName = "music_info"
        self.tableColumn = { 
                            "no": {"type":"INT", "primary":True},
                            "title" : {"type":"TEXT", "null":True},
                            "artist" : {"type":"TEXT", "null":True},
                            "album" : {"type":"TEXT", "null":True},
                            "duration" : {"type":"INT", "null":True},
                            "year" : {"type":"TEXT", "null":True},
                            "genre" : {"type":"TEXT", "null":True}
                           }
    
    def install(self, upgradeFrom=None):
        self.api.db.createTable(self.name, self.tableName, self.tableColumn)
    
    def uninstall(self):
        self.api.db.deleteTable(self.name, self.tableName)
    
    def run(self, command, params):
        if command == "getFileInfo":
            self.getInfo(params["no"], params["address"])
        elif command == "search":
            return self.search(params)
        elif command == "showFileInfo":
            return self.showInfo(params)
        elif command == "delete":
            self.delete(params)
    
    def getInfo(self, no, address):
        info = auto.File(address)
        if info.valid:
            keys = {}
            for i in self.tableColumn.keys():
                try:
                    value = getattr(info, i)
                    keys[i] = value
                except AttributeError:
                    pass
            keys["no"] = no
            if len(keys.keys()) > 1:
                self.api.db.insert(self.name, self.tableName, keys)
    
    def showInfo(self, no):
        where = [{"no":no}]
        infos = self.api.db.get(self.name, self.tableName, where=where)
        if len(infos) == 1:
            return infos[0]
    
    def delete(self, no):
        where = [{"no":no}]
        infos = self.api.db.delete(self.name, self.tableName, where=where)
    
    def search(self, text):
        where = [{"title":["like", text]}, "OR",
                 {"artist":["like", text]}, "OR",
                 {"album":["like", text]}, "OR",
                 {"genre":["like", text]}
                ]
        founded = self.api.db.get(self.name, self.tableName, where=where, order=["no"])
        noList = []
        for i in founded:
            if i["no"] not in noList:
                noList.append(i["no"])
        return noList
