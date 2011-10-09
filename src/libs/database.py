#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import gettext

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

#For multilanguage support
gettext.install("bilge-katalog", unicode=1)

#mysql support
try:
    import mysql
    MYSQL = True
except ImportError:
    MYSQL = False

#sqlite support
try:
    import sqlite
    SQLITE = True
except ImportError:
    SQLITE = False

class ConfigForDb(object):
    """Configuration object for reading and writing database paramaters on configuration file."""
    def __init__(self):
        self.configKeys = [ "dbType",
                            "mysqlServer",
                            "mysqlUserName",
                            "mysqlUserPass",
                            "mysqlDbName",
                            "sqliteDbAddress",
                            "dbPrefix"          ]
        self.confFileAddress = os.environ["HOME"] + "/.bilge-katalog/config"
        self.confFileHeader = """\
# This file generated automaticaly by Bilge-Katalog
#
# If you don't know what you're doing, do not make changes to this file
"""

    def readConfig(self):
        """Reading configuration from file."""
        if os.path.exists(self.confFileAddress):
            confFile = open(self.confFileAddress, "r")
            confLines = confFile.readlines()
            confFile.close()
            
            for i in confLines:
                if i[0] == "#":
                    continue
                if ":" not in i:
                    continue
                key, value = i.split(":")
                if key.strip() in self.configKeys:
                    setattr(self, key.strip(), value.strip())
            return True
        else:
            return False

    def writeConfig(self):
        """Writing configuration to file."""
        confFile = open(self.confFileAddress, "w")
        
        confFile.write(self.confFileHeader)
        for i in self.__dict__.keys():
            if i in self.configKeys:
                confFile.write("%s : %s\n"% (i, getattr(self, i)))
        
        confFile.close()

def mountDb(config):
    """Connecting to database"""
    if config.dbType == "mysql" and MYSQL:
        try:
            DB = mysql.database()
            DB.mount(config)
        except Exception, e:
            raise Exception(e[0], e[1])
    elif config.dbType == "sqlite" and SQLITE:
        try:
            DB.sqlite.database()
            DB.mount(config)
        except Exception, e:
            raise Exception(-1, e)
    else:
        raise Exception(-1, "Wrong configured configuration file!")
    
    return DB

class SampleDB(object):
    def __init__(self):
        """"""
        self.mounted = False
        self.db = None
        self.cur = None
        
    def mount(self, config):
        """
        function for connecting database with configuration
        
        config : database configuration dictionary
        """
        pass #after mounting self.mounted = True
        
    def get(self, table, where=None, order=None):
        """
        function for taking data from database
        
        table : ""
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        order : []
        
        returned : [{"key":"value", ...}, ...]
        """
        if not self.mounted:
            return
        
        keys = self.getkeys(table)
        
        query = "SELECT * FROM %s "% table
        if where != None and type(where) == list:
            query += "WHERE "
            if type(where) == dict:
                where = [where]
            for i in where:
                if type(i) == dict:
                    query += " ( "
                    n = 0
                    for j in i.keys():
                        if n != 0:
                            query += "AND "
                        if type(i[j]) == list:
                            if i[j][0].lower() == "like":
                                query += "{0} LIKE '%{1}%' ".format(j, i[j][1])
                            else:
                                query += "%s %s '%s' "% (j, i[j][0], i[j][1])
                        elif type(i[j]) == str:
                            query += "%s = '%s' "% (j, i[j])
                        n += 1
                    query += " ) "
                elif type(i) == str:
                    query += "%s "% i
        
        if order != None:
            query += "ORDER BY " + ", ".join(order)
        
        self.cur.execute(query)
        results = []
        for i in self.cur.fetchall():
            result = {}
            n = 0
            while len(i) > n:
                result[keys[n]] = i[n]
                n += 1
            results.append(result)
        
        return results
        
    def getkeys(self, table):
        """
        function for taking column names from database
        
        table : ""
        
        returned : []
        """
        pass
    
    def insert(self, table, row):
        """
        function for inserting row to database
        
        table : ""
        row : {"key":"value", ...}
        """
        if not self.mounted:
            return
        
        query = "INSERT INTO %s "% table
        keys = []
        values = []
        for i in row.keys():
            keys.append(i)
            values.append(row[i])
        
        query += "(%s) "% (", ".join(keys))
        query += "VALUES ('%s')"% ("', '".join(values))
        
        self.cur.execute(query)
    
    def update(self, table, row, where):
        """
        function for updating the row where on the database
        
        table : ""
        row : {"key":"value", ...}
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        """
        if not self.mounted:
            return
        
        query = "UPDATE %s SET "% table
        setlist = []
        for i in row.keys():
            setlist.append("%s = '%s'"% (i, row[i]))
        query += ", ".join(setlist) + " WHERE "
        if type(where) == dict:
            where = [where]
        for i in where:
            if type(i) == dict:
                query += " ( "
                n = 0
                for j in i.keys():
                    if n != 0:
                        query += "AND "
                    if type(i[j]) == list:
                        if i[j][0].lower() == "like":
                            query += "{0} LIKE '%{1}%' ".format(j, i[j][1])
                        else:
                            query += "%s %s '%s' "% (j, i[j][0], i[j][1])
                    elif type(i[j]) == str:
                        query += "%s = '%s' "% (j, i[j])
                    n += 1
                query += " ) "
            elif type(i) == str:
                query += "%s "% i
        
        self.cur.execute(query)
    
    def delete(self, table, where):
        """
        function for deleting anything from database
        
        table : ""
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        """
        if not self.mounted:
            return
        
        query = "DELETE FROM %s WHERE "% table
        if type(where) == dict:
            where = [where]
        for i in where:
            if type(i) == dict:
                query += " ( "
                n = 0
                for j in i.keys():
                    if n != 0:
                        query += "AND "
                    if type(i[j]) == list:
                        if i[j][0].lower() == "like":
                            query += "{0} LIKE '%{1}%' ".format(j, i[j][1])
                        else:
                            query += "%s %s '%s' "% (j, i[j][0], i[j][1])
                    elif type(i[j]) == str:
                        query += "%s = '%s' "% (j, i[j])
                    n += 1
                query += " ) "
            elif type(i) == str:
                query += "%s "% i
        
        self.cur.execute(query)
    
    def createTable(self, table, keys):
        """
        function for creating table on database
        
        table : ""
        keys : {"key":{ "type":"TYPE","null":False,"auto":False,
                        "primary":False,"default":"DEFAULT"     }, ...}
        """    
        pass