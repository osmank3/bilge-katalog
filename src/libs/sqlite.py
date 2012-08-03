#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sqlite3
from .sampledb import SampleDB

class database(SampleDB):
    def __init__(self):
        SampleDB.__init__(self)
        self.escText = "'"
        
    def mount(self, config):
        """function for connecting database with configuration"""
        creating = False
        if not os.path.isfile(config.sqliteDbAddress):
            creating = True
        try:
            self.db = sqlite3.connect(  config.sqliteDbAddress,
                                        detect_types=sqlite3.PARSE_DECLTYPES   )
            self.cur = self.db.cursor()
            self.mounted = True
            
            if creating:
                self.createTable("items", {
                                    "no":{"type":"INTEGER", "auto":True, "primary":True},
                                    "upno":{"type":"INTEGER"},
                                    "name":{"type":"TEXT"},
                                    "dateadd":{"type":"TIMESTAMP","default":"CURRENT_TIMESTAMP"},
                                    "size":{"type":"INTEGER",},
                                    "form":{"type":"TEXT"}
                                    }
                                )
                self.createTable("config", {
                                    "key":{"type":"TEXT", "primary":True},
                                    "value":{"type":"TEXT"}
                                    }
                                )
                self.db.commit()
                
        except Exception as e:
            raise Exception(e)
    
    def getkeys(self, table):
        """function for taking column names from database"""
        if not self.mounted:
            return
        
        query = "PRAGMA TABLE_INFO(%s)"% table
        self.cur.execute(query)
        keys = []
        for i in self.cur.fetchall():
            keys.append(i[1])
        
        return keys
    
    def createTable(self, table, keys):
        """
        function for creating table on database
        
        table : ""
        keys : {"key":{ "type":"TYPE","null":False,"auto":False,
                        "primary":False,"default":"DEFAULT"     }, ...}
        """
        if not self.mounted:
            return
        
        query = "CREATE TABLE %s ("% table
            
        for i in keys.keys():
            info = keys[i]
            keytype = info["type"]
            query += "%s %s "% (i, keytype)
            
            if "primary" in info.keys() and info["primary"] == True:
                query += "PRIMARY KEY "
            
            if "auto" in info.keys() and info["auto"] == True:
                query += "AUTOINCREMENT "
                
            if "default" in info.keys():
                query += "DEFAULT %s "% info["default"]
            
            query += ", "
        
        query = query[:-2] + ")"
        
        self.cur.execute(query)
        self.db.commit()
