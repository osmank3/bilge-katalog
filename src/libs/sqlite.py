#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sqlite3
from database import SampleDB

class database(SampleDB):
    def __init__(self):
        SampleDB.__init__(self)
        
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
                                    "dateadd":{"type":"TIMESTAMP",},
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
                
        except Exception, e:
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
            
            if info.has_key("auto") and info["auto"] == True:
                query += "AUTOINCREMENT "
            
            if info.has_key("primary") and info["primary"] == True:
                query += "PRIMARY KEY "
                
            if info.has_key("default"):
                query += "DEFAULT %s "% info["default"]
            
            query += ", "
        
        query += ")"
        
        self.cur.execute(query)