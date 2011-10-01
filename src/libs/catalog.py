#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

class Item(object):
    def __init__(self, no=None infos=None, address=None):
        self.no = no
        self.real_address = address
        self.relative_address = None
        
        if infos:
            for i in infos.keys():
                setattr(self, i, infos[i])
        else:
            self.upno = None
            self.name = None
            self.form = None
            self.size = 0
            self.dateadd = None
    
    def getRealInfo(self, address=None):
        if address:
            self.real_address = address
        
        if self.real_address:
            if self.real_address[-1] == os.sep:
                self.real_address = self.real_address[:-1]
            
            if not self.name:
                self.name = os.path.split()[-1]
            
            if os.path.isfile(self.real_address):
                self.form = "file"
                self.size = int(os.stat(self.real_address).st_size)
            elif os.path.isdir(self.real_address):
                self.form = "directory"
        else:
            return False
            
    def getRelativeAddress(self, database):
        if self.upno and database:
            upno = self.upno
            self.relative_address = ""
            while upno != 0:
                results = database.get("items", [{"no":upno}])
                if len(results) == 1:
                    infos = results[0]
                    upno = infos["upno"]
                    self.relative_address = os.sep + infos["name"] + self.relative_address
                else: #There is no possibility :D
                    pass
        else:
            return False
    
    def getDbInfo(self, database, no=None):
        if no:
            self.no = no
        
        if self.no and database:
            results = database.get("items", [{"no":self.no}])
            if len(results) == 1:
                infos = results[0]
                for i in infos.keys():
                    setattr(self, i, infos[i])
            
                self.getRelativeAddress(database)
            else: #There is no possibility :D
                return False
        else:
            return False
            
    def insert2Db(self, database):
        if self.upno and self.name and self.form:
            row = { "upno":self.upno, "name":self.name,
                    "size":self.size, "form":self.form  }
            database.insert("items", row)
            
            results = database.get("items", order=["no"])
            self.getDbInfo(database, results[-1]["no"])
            
            return True
        else:
            return False

class RootItem(Item):
    def __init__(self):
        self.no = 0
        self.upno = None
        self.name = "ROOT"
        self.form = "directory"
        self.relative_address = "/"

class Explore(object):
    def __init__(self, database):
        self.db = database
        self.curItem = RootItem()
        self.refresh()
    
    def refresh(self):
        self.curItemList = self.fillList()
    
    def fillList(self, item=None):
        itemList = []
        if item:
            dirNo = item.no
        else:
            dirNo = self.curItem.no
            
        results = self.db.get("items", [{"upno":dirNo}], ["form"])
        for i in results:
            newItem = Item(infos=i)
            newItem.getRelativeAddress(self.db)
            
            itemList.append(newItem)
        
        return itemList
        
    def chdir(self, item):
        if item.name == "ROOT":
            self.__init__()
        elif item.form == "directory":
            self.curItem = item
            self.refresh()
        else:
            return False
    
    def turnUp(self):
        if self.curItem.upno:
            newItem = Item(no=self.curItem.upno)
            newItem.getDbInfo(database=self.db)
            
            self.curItem = newItem
            self.refresh()
        else:
            self.curItem = RootItem()
            self.refresh()

def insertAll2Db(item, database, progressItem):
    item.getRealInfo()
    if item.insert2Db(database):
        try:
            progressItem.increase()
        except AttributeError:
            pass
        
        if item.real_address:
            for i in os.listdir(item.real_address):
                address = item.address + os.sep + i
                newItem = Item(address = address)
                newItem.upno = item.no
                
                insertAll2Db(newItem, database, progressItem)
    else:
        return False