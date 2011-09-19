#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sqlite3

def mount(config):
    """function for connecting database with configuration"""
    creating = False
    if not os.path.isfile(config.sqliteDbAddress):
        creating = True
    try:
        db = sqlite3.connect(  config.sqliteDbAddress,
                               detect_types=sqlite3.PARSE_DECLTYPES    )
        
        if creating:
            cur = db.cursor()
            cur.execute(""" CREATE TABLE items (\
                            id INTEGER PRIMARY KEY AUTOINCREMENT,\
                            up_id INTEGER,\
                            name TEXT,\
                            dateadd TIMESTAMP,\
                            size INTEGER,\
                            form TEXT)"""   )
            cur.execute(""" CREATE TABLE config (\
                            key TEXT PRIMARY KEY,\
                            value TEXT)""")
            db.commit()
        
        return db
    except Exception, e:
        raise Exception(e)
    
        