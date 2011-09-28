#!/usr/bin/env python
#-*- coding:utf-8 -*-

import MySQLdb
from database import SampleDB

class database(SampleDB):
    def __init__(self):
        SampleDB.__init__(self)
        
    def mount(self, config):
        """function for connecting database with configuration"""
        try:
            self.db = MySQLdb.connect(  host = config.mysqlServer,
                                        user = config.mysqlUserName,
                                        passwd = config.mysqlUserPass,
                                        db = config.mysqlDbName    )
            self.cur = self.db
            self.mounted = True
        except MySQLdb.Error, e:
            raise Exception(e[0], e[1])
            
    def createUserAndTable(self, config):
        """function for creating new user and database on mysql server."""
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
        self.cur.execute("""CREATE DATABASE IF NOT EXISTS {mysqlDbName}\
                            """.format(**config.__dict__))
        self.cur.execute("""GRANT ALL PRIVILEGES ON {mysqlDbName}.* TO\
                            {mysqlUserName}@{mysqlServer}\
                            """.format(**config.__dict__))
        self.db.commit()

    def prepareTable(self):
        """function for creating tables on database"""
        if not self.mounted:
            return
        self.cur.execute("""CREATE TABLE IF NOT EXISTS items (\
                            no INT NOT NULL AUTO_INCREMENT PRIMARY KEY ,\
                            upno INT NOT NULL ,\
                            name TEXT NOT NULL ,\
                            dateadd TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\
                            size INT NOT NULL DEFAULT  '0',\
                            form ENUM(  "file",  "directory" ) NOT NULL )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS config (\
                            key VARCHAR( 64 ) NOT NULL PRIMARY KEY ,\
                            value TEXT NOT NULL )""")
        self.db.commit()
    
    def getkeys(self, table):
        """function for taking column names from database"""
        if not self.mounted:
            return
        
        query = "SHOW COLUMNS FROM %s"% table
        self.cur.execute(query)
        keys = []
        for i in self.cur.fetchall():
            keys.append(i[0])
        
        return keys