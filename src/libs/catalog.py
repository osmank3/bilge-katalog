#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

class Item(object):
    def __init__(self, bilge, no=None, infos=None, address=None):
        self.__bilge = bilge
        self.__db = bilge.db
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
                self.name = os.path.split(self.real_address)[-1]
            
            if os.path.isfile(self.real_address):
                self.form = "file"
                self.size = int(os.stat(self.real_address).st_size)
            elif os.path.isdir(self.real_address):
                self.form = "directory"
        else:
            return False
            
    def getRelativeAddress(self):
        if self.upno and self.__db:
            upno = self.upno
            self.relative_address = ""
            while upno != 0:
                results = self.__db.get("items", [{"no":upno}])
                if len(results) == 1:
                    infos = results[0]
                    upno = infos["upno"]
                    self.relative_address = os.sep + infos["name"] + self.relative_address
                else: #There is no possibility :D
                    pass
        else:
            return False
    
    def getDbInfo(self, no=None):
        if no:
            self.no = no
        if self.no and self.__db:
            results = self.__db.get("items", [{"no":self.no}])
            if len(results) == 1:
                infos = results[0]
                for i in infos.keys():
                    setattr(self, i, infos[i])
            
                self.getRelativeAddress()
            else: #There is no possibility :D
                return False
        else:
            return False
            
    def insert2Db(self):
        if self.upno != None and self.name != None and self.form != None:
            row = { "upno":self.upno, "name":self.name,
                    "size":self.size, "form":self.form  }
            self.__db.insert("items", row)
            
            results = self.__db.get("items", order=["no"])
            self.getDbInfo(results[-1]["no"])
            
            return True
        else:
            return False
    
    def insert2DbRecursive(self, progressItem):
        self.getRealInfo()
        if self.insert2Db():
            try:
                progressItem.increase()
            except AttributeError:
                pass
            
            self.__bilge.plugs.creatingCat(self)
            
            if self.real_address and self.form == "directory":
                for i in os.listdir(self.real_address):
                    address = self.real_address + os.sep + i
                    newItem = Item(self.__bilge, address = address)
                    newItem.upno = self.no
                    
                    newItem.insert2DbRecursive(progressItem)
            return True
        else:
            return False
            
    def delete(self):
        if self.no:
            self.__db.delete("items", {"no":self.no})
            self.__bilge.plugs.delete(self.no)
            
            if self.form == "directory":
                childs = self.__db.get("items", {"upno":self.no})
                for i in childs:
                    newItem = Item(self.__bilge, infos=i)
                    newItem.delete()
                    
            return True
        else:
            return False
            
    def copyInDb(self, upno):
        if upno:
            oldNo = self.no
            self.upno = upno
            self.insert2Db()
            
            if self.form == "directory":
                childs = self.__db.get("items", {"upno":oldNo})
                for i in childs:
                    newItem = Item(self.__bilge, infos=i)
                    newItem.copyInDb(self.no)
                    
            return True
        else:
            return False
            
    def update(self, newInfo):
        if self.no:
            self.__db.update("items",newInfo,{"no":self.no})
            
            return True
        else:
            return False

class ExploreObject(object):
    def __init__(self, name, form="normal"):
        """
        exploring object init function
        
        name : ""
        form : "normal" or "search"
        """
        self.name = name
        self.form = form
        self.history = []
        self.index = -1
        
        if self.form == "search":
            self.searchList = []
        
    def curItem(self):
        """
        function for getting current item on history
        
        returned : item object or None
        """
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
        if self.index > 0 or (self.form == "search" and self.index > -1):
            self.index -= 1
            
    def forward(self):
        if len(self.history) > self.index + 1:
            self.index += 1

class Explorer(object):
    def __init__(self, bilge):
        self.__bilge = bilge
        self.__db = bilge.db
        self.expObjList = []
        self.expObj = self.newExp("main")
        
    def ready(self):
        return True
        
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
        
        if type(curItem) == type(None):
            if self.expObj.form == "search":
                return self.expObj.searchList
            return []
            
        results = self.__db.get("items", {"upno":curItem.no}, ["form","name"])
        for i in results:
            newItem = Item(self.__bilge, infos=i)
            newItem.getRelativeAddress()
            
            itemList.append(newItem)
        
        return itemList
        
    def fillSearchList(self, text):
        itemList = []
        if self.expObj.form == "search":
            noList = []
            results = self.__db.get("items", {"name":["like",text]}, ["form","name"])
            for i in results:
                noList.append(i["no"])
            
            plugsearch = self.__bilge.plugs.searching(text)
            for i in plugsearch:
                if i not in noList:
                    noList.append(i)
            
            for i in noList:
                newItem = Item(self.__bilge, no=i)
                newItem.getDbInfo()
                
                itemList.append(newItem)
            
            self.expObj.searchList = itemList
    
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
            newItem = Item(self.__bilge, no=curItem.upno)
            newItem.getDbInfo()
            
            self.changeItem(newItem)

