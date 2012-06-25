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
            DB = sqlite.database()
            DB.mount(config)
        except Exception, e:
            raise Exception(-1, e)
    else:
        raise Exception(-1, "Wrong configured configuration file!")
    
    return DB
