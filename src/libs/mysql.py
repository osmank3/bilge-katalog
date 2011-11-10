#!/usr/bin/env python
#-*- coding:utf-8 -*-

import MySQLdb
from sampledb import SampleDB

class database(SampleDB):
    def __init__(self):
        SampleDB.__init__(self)
        
    def mount(self, config):
        """
        function for connecting database with configuration
        
        config : database configuration dictionary
        """
        try:
            self.db = MySQLdb.connect(  host = config.mysqlServer,
                                        user = config.mysqlUserName,
                                        passwd = config.mysqlUserPass,
                                        db = config.mysqlDbName    )
            self.cur = self.db.cursor()
            self.mounted = True
        except MySQLdb.Error, e:
            raise Exception(e[0], e[1])
            
    def createUser(self, config):
        """
        function for creating new user on mysql server.
        
        config : database configuration dictionary
        """
        if not self.mounted:
            return
        self.cur.execute("""CREATE USER {mysqlUserName}@{mysqlServer}\
                            IDENTIFIED BY '{mysqlUserPass}'\
                            """.format(**config.__dict__))
        self.cur.execute("""GRANT USAGE ON *.* TO {mysqlUserName}@{mysqlServer}\
                            IDENTIFIED BY '{mysqlUserPass}' WITH\
                            MAX_QUERIES_PER_HOUR 0\
                            MAX_CONNECTIONS_PER_HOUR 0\
                            MAX_UPDATES_PER_HOUR 0\
                            MAX_USER_CONNECTIONS 0\
                            """.format(**config.__dict__))
        self.db.commit()
            
    def createDatabase(self, config):
        """
        function for creating new database on mysql server.
        
        config : database configuration dictionary
        """
        if not self.mounted:
            return
        self.cur.execute("""CREATE DATABASE IF NOT EXISTS {mysqlDbName}\
                            """.format(**config.__dict__))
        self.cur.execute("""GRANT ALL PRIVILEGES ON {mysqlDbName}.* TO\
                            {mysqlUserName}@{mysqlServer}\
                            """.format(**config.__dict__))
        self.cur.execute("use {mysqlDbName}".format(**config.__dict__))
        self.db.commit()

    def prepareTable(self):
        """function for creating tables on database"""
        if not self.mounted:
            return
        self.createTable("items", {
                            "no":{"type":"INT", "auto":True, "primary":True},
                            "upno":{"type":"INT"},
                            "name":{"type":"TEXT"},
                            "dateadd":{"type":"TIMESTAMP","default":"CURRENT_TIMESTAMP"},
                            "size":{"type":"INT","default":"'0'"},
                            "form":{"type":"""ENUM( "directory", "file" )"""}
                            }
                        )
        self.createTable("config", {
                            "key":{"type":"VARCHAR( 64 )", "primary":True},
                            "value":{"type":"TEXT"}
                            }
                        )
        self.db.commit()
    
    def getkeys(self, table):
        """
        function for taking column names from database
        
        table : ""
        
        returned : []
        """
        if not self.mounted:
            return
        
        query = "SHOW COLUMNS FROM %s"% table
        self.cur.execute(query)
        keys = []
        for i in self.cur.fetchall():
            keys.append(i[0])
        
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
        
        query = "CREATE TABLE IF NOT EXISTS %s ("% table
            
        for i in keys.keys():
            info = keys[i]
            keytype = info["type"]
            query += "`%s` %s "% (i, keytype)
            
            if info.has_key("null") and info["null"] == True:
                query += "NULL "
            else:
                query += "NOT NULL "
            
            if info.has_key("primary") and info["primary"] == True:
                query += "PRIMARY KEY "
            
            if info.has_key("auto") and info["auto"] == True:
                query += "AUTO_INCREMENT "
                
            if info.has_key("default"):
                query += "DEFAULT %s "% info["default"]
            
            query += ", "
        
        query = query[:-2] + ")"
        
        self.cur.execute(query)