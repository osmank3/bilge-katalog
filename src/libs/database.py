#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import gettext

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
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
                    setattr(self, key.strip(), value.strip().replace("'","\\'"))
            return True
        else:
            return False

    def writeConfig(self):
        """Writing configuration to file."""
        if not os.path.exists(os.path.split(self.confFileAddress)[0]):
            os.mkdir(os.path.split(self.confFileAddress)[0])
        
        confFile = open(self.confFileAddress, "w")
        
        confFile.write(self.confFileHeader)
        for i in self.__dict__.keys():
            if i in self.configKeys:
                confFile.write("%s : %s\n"% (i, getattr(self, i)))
        
        confFile.close()

def mountDb(dbconfig):
    """Connecting to database"""
    if dbconfig.dbType == "mysql":
        if MYSQL:
            try:
                DB = mysql.database()
                DB.mount(dbconfig)
            except Exception, e:
                raise Exception(e[0], e[1])
        else:
            raise Exception(-1, "Mysql module could not import!")
    elif config.dbType == "sqlite":
        if SQLITE:
            try:
                DB = sqlite.database()
                DB.mount(dbconfig)
            except Exception, e:
                raise Exception(-1, e)
        else:
            raise Exception(-1, "Sqlite module could not import!")
    else:
        raise Exception(-1, "Wrong configured configuration file!")
    
    return DB

class ConfigOnDb(object):
    def __init__(self, bilge):
        self.__bilge = bilge
        self.__db = bilge.db
        self.lastconf = {}
        self.conf = {}
        self.readConfOnDb()
        
    def ready(self):
        return True
        
    def readConfOnDb(self):
        results = self.__db.get("config")
        self.lastconf = {}
        for i in results:
            self.lastconf[i["key"]] = i["value"]
        self.conf = self.lastconf.copy()
        
    def writeConfToDb(self):
        for i in self.conf.keys():
            if i not in self.lastconf.keys():
                self.__db.insert("config", {"key":i,"value":self.conf[i]})
            elif self.conf[i] != self.lastconf[i]:
                self.__db.update("config", {"value":self.conf[i]}, {"key":i})
                
        for i in self.lastconf.keys():
            if i not in self.conf.keys():
                self.__db.delete("config", {"key":i})
        
        self.readConfOnDb()
        
    def getConf(self, key):
        if key in self.conf.keys():
            return self.conf[key]
        else:
            return None
        
    def setConf(self, key, value):
        self.conf[key] = value
