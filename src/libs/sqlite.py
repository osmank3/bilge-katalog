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
                self.cur.execute("""CREATE TABLE items (\
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                    up_id INTEGER,\
                                    name TEXT,\
                                    dateadd TIMESTAMP,\
                                    size INTEGER,\
                                    form TEXT)""")
                self.cur.execute("""CREATE TABLE config (\
                                    key TEXT PRIMARY KEY,\
                                    value TEXT)""")
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