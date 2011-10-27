#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

class Item(object):
    def __init__(self, no=None, infos=None, address=None):
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

class ExploreObject(object):
    def __init__(self, name, form="normal"):
        self.name = name
        self.form = form
        self.history = []
        self.index = -1
        
    def curItem(self):
        if self.index >= 0:
            return self.history[self.index]
        else:
            return None
            
    def forwardItem(self):
        if len(self.history) > self.index + 1:
            return self.history[self.index + 1]
        else:
            return None
            
    def backItem(self):
        if self.index > 0:
            return self.history[self.index - 1]
        else:
            return None
            
    def addHistory(self, item):
        if len(self.history) > self.index + 1:
            self.history = self.history[:self.index+1]
        
        self.history.append(item)
        self.index += 1
        
    def back(self):
        if self.index > 0:
            self.index -= 1
            
    def forward(self):
        if len(self.history) > self.index + 1:
            self.index += 1

class Explorer(object):
    def __init__(self, database):
        self.__db = database
        self.expObjList = []
        self.expObj = self.newExp("main")
        
    def newExp(self, name, form="normal"):
        for i in self.expObjList:
            if i.name == name:
                return i
        
        obj = ExploreObject(name, form)
        self.expObjList.append(obj)
        
        return obj
        
    def changeExp(self, name):
        new = True
        for i in self.expObjList:
            if i.name == name:
                self.expObj = i
                new = False
                
        if new:
            self.expObj = self.newExp(name)
        
    def delExp(self, name):
        n = 0
        while n < len(self.expObjList):
            if self.expObjList[n].name == name:
                self.expObjList.pop(n)
                break
            n += 1
            
    def listOfDir(self, item=None):
        itemList = []
        if item:
            curItem = item
        else:
            curItem = self.expObj.curItem()
        
        if type(curItem) == None:
            return []
            
        results = self.__db.get("items", {"upno":curItem.no}, "form")
        for i in results:
            newItem = Item(infos=i)
            newItem.getRelativeAddress(self.__db)
            
            itemList.append(newItem)
        
        return itemList
        
    def back(self):
        self.expObj.back()
        
    def forward(self):
        self.expObj.forward()
        
    def changeItem(self, item):
        if self.expObj.backItem() and item.no == self.expObj.backItem().no:
            self.back()
        elif self.expObj.forwardItem() and item.no == self.expObj.forwardItem().no:
            self.forward()
        elif not self.expObj.curItem() or item.no != self.expObj.curItem().no:
            self.expObj.addHistory(item)
            
    def up(self):
        curItem = self.expObj.curItem()
        if curItem and curItem.upno != 0:
            newItem = Item(no=curItem.upno)
            newItem.getDbInfo(database=self.__db)
            
            self.changeItem(newItem)

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