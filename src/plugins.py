#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import json
import tarfile
import shutil

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

class disp_api(object):
    def __init__(self, disp):
        self.__disp = disp
    
    def addMenu(self):
        """"""
        pass
        
    def showDialog(self):
        """"""
        pass
        
class db_api(object):
    def __init__(self, db):
        self.__db = db
        
    def get(self, pluginName, table, where=None, order=None):
        """
        function for taking data from database
        
        pluginName : ""
        table : ""
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        order : []
        
        returned : [{"key":"value", ...}, ...]
        """
        return self.__db.get(table, where, order)
        
    def insert(self, pluginName, table, row):
        """
        function for inserting row to database
        
        pluginName : ""
        table : ""
        row : {"key":"value", ...}
        """
        if table not in ["items", "config"]:
            self.__db.insert(table, row)
    
    def update(self, pluginName, table, row, where):
        """
        function for updating the row where on the database
        
        pluginName : ""
        table : ""
        row : {"key":"value", ...}
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        """
        if table not in ["items", "config"]:
            self.__db.update(table, row, where)
        
    def delete(self, pluginName, table, where):
        """
        function for deleting anything from database
        
        pluginName : ""
        table : ""
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        """
        if table not in ["items", "config"]:
            self.__db.delete(table, where)
    
    def createTable(self, pluginName, table, keys):
        """
        function for creating table on database
        
        pluginName : ""
        table : ""
        keys : {"key":{ "type":"TYPE","null":False,"auto":False,
                        "primary":False,"default":"DEFAULT"     }, ...}
        """
        if table not in ["items", "config"]:
            self.__db.createTable(table, keys)
            
    def deleteTable(self, pluginName, table):
        """
        function for deleting table on database
        
        pluginName : ""
        table : ""
        """
        if "," not in table and table.strip() not in ["items", "config"]:
            self.__db.deleteTable(table)

class plug_api(object):
    def __init__(self, db, disp):
        self.db = db
        self.disp = disp
        
class Plugs(object):
    def __init__(self, bilge):
        self.__bilge = bilge
        
        #create api
        dbapi = db_api(self.__bilge.db)
        dispapi = disp_api(self.__bilge.disp)
        self.api = plug_api(dbapi, dispapi)
        
        self.plugins = []
        self.fillPlugins()
        
    def ready(self):
        return True
        
    def fillPlugins(self):
        self.plugins = []
        conf = self.__bilge.conf.getConf("plugins")
        try:
            plugins = json.loads(conf)
        except TypeError:
            plugins = []
        for pluginfo in plugins:
            if os.getuid() != 0:
                sys.path.append(os.getenv("HOME") + os.sep + ".bilge-katalog/plugins")
            sys.path.append(os.getcwd() + os.sep + "plugins")
            
            plug_module, ext = os.path.splitext(pluginfo["main_module"])
            plug = __import__("{0}.{1}".format(pluginfo["name"], plug_module),
                                      fromlist = ["Main"])
            pluginItem = plug.Main(self.api)
            
            pluginfo["module"] = pluginItem
            
            self.plugins.append(pluginfo)
        
    def plugInstall(self, address):
        upgradeFrom = None
        if os.getuid() == 0:
            pluginsDir = os.getcwd() + os.sep + "plugins"
        else:
            pluginsDir = os.getenv("HOME") + os.sep + ".bilge-katalog/plugins"
        sys.path.append(pluginsDir)
        plugtar = tarfile.open(address, "r:gz")
        dirs = []
        metadata = []
        for i in plugtar.getmembers():
            if os.sep not in i.name:
                dirs.append(i.name)
            if "metadata.json" in i.name:
                metadata.append(i)
        if len(dirs) != 1 or len(metadata) != 1:
            raise Exception(-1, "Not plugin archive or wrong configured plugin archive")
        else:
            pluginName = dirs[0]
            try:
                jsonfile = plugtar.extractfile(metadata[0])
            except ValueError:
                raise Exception(-1, "Wrong configured json file")
            pluginfo = json.loads(jsonfile.read().decode("utf-8"))
            if "dependencies" in pluginfo.keys():
                for i in pluginfo["dependencies"]:
                    try:
                        __import__(i)
                    except ImportError:
                        raise Exception(-1, "Dependency not found: " + i)
            if "main_module" in pluginfo.keys():
                plug_module, ext = os.path.splitext(pluginfo["main_module"])
            else:
                plug_module = "Main"
                
            if os.path.exists(pluginsDir + os.sep + pluginfo["name"]) or os.path.exists(pluginsDir + os.sep + pluginName):
                for plug in self.plugins:
                    if pluginfo["name"] == plug["name"]:
                        if int(pluginfo["version"]) > int(plug["version"]):
                            self.plugUninstall(plug, upgrade=True)
                            upgradeFrom = plug["verison"]
                
            try:
                plugtar.extractall(pluginsDir)
                pluginAddress = pluginsDir + os.sep + pluginName
                if pluginName != pluginfo["name"]:
                    oldName = pluginName
                    os.rename(pluginAddress, pluginsDir + os.sep + pluginfo["name"])
                                
                try:
                    plug = __import__("{0}.{1}".format(pluginfo["name"], plug_module),
                                      fromlist = ["Main"])
                    pluginItem = plug.Main(self.api)
                    pluginItem.install(upgradeFrom)
                except ImportError:
                    raise Exception(-1, "Plugins main_module cound not import!")
                
                pluginfo["installed_dir"] = pluginsDir
                pluginfo["module"] = pluginItem
                pluginfo["activated"] = True
                self.plugins.append(pluginfo)
                newConf = json.dumps(self.plugins, default=lambda x: None)
                self.__bilge.conf.setConf("plugins", newConf)
            except Exception as e:
                for i in dirs:
                    if i == oldName:
                        i = pluginfo["name"]
                    if os.path.exists(pluginsDir + os.sep + i):
                        shutil.rmtree(pluginsDir + os.sep + i)
                raise e
        
    def plugUninstall(self, plugin, upgrade=False):
        n = 0
        while n < len(self.plugins):
            curPlug = self.plugins[n]
            if plugin["name"] == curPlug["name"]:
                if not upgrade:
                    curPlug["module"].uninstall()
                if os.path.exists(curPlug["installed_dir"] + os.sep + curPlug["name"]):
                    shutil.rmtree(curPlug["installed_dir"] + os.sep + curPlug["name"])
                self.plugins.pop(n)
                
            n += 1
        newConf = json.dumps(self.plugins, default=lambda x:None)
        self.__bilge.conf.setConf("plugins", newConf)
        
    def creatingCat(self, item):
        address = item.real_address
        if os.path.exists(address) and not os.path.isdir(address):
            name, ext = os.path.splitext(address)
            ext = ext.lower().replace(".","")
            for i in self.plugins:
                if "extensions" in i.keys() and ext in i["extensions"] and i["activated"] == True:
                    i["module"].run("getFileInfo", {"no":item.no,"address":item.real_address})
        
    def showInfo(self, item):
        for i in self.plugins:
            if i["activated"] == True:
                print(i["module"].run("showFileInfo",item.no))
        
    def searching(self, text):
        founded = []
        for i in self.plugins:
            if i["activated"] == True:
                for j in i["module"].run("search",text):
                    if j not in founded:
                        founded.append(j)
        return founded
    
    def delete(self, no):
        for i in self.plugins:
            i["module"].run("delete", no)
    
    def exportInfo(self, no):
        extensions = {}
        for i in self.plugins:
            if i["activated"] == True:
                infos = i["module"].run("export", no)
                if infos != False:
                    extensions[i["name"]] = infos
        return extensions
    
    def importInfo(self, extName, no, data):
        for i in self.plugins:
            if i["name"] == extName and i["activated"] == True:
                i["module"].run("import", {"no":no, "data":data})
    
    def runPluginFunction(self, text):
        #text'i parçala ve ilgili fonsiyonu çalıştır.
        pass
