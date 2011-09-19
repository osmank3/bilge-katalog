#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

class Item(object):
    def __init__(self, no=None, address=None):
        self.no = no
        self.real_address = address
        
        self.upno = None
        self.name = None
        self.form = None
        self.size = 0
        self.dateadd = None
        self.relative_address = None
    
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
    
    def getDbInfo(self, database, no=None):
        if no:
            self.no = no
        
        if self.no and database:
            database.cur.execute("""SELECT * FROM items
                                    WHERE id = "%s" """% self.no)
            infos = database.cur.fetchone()
            self.upno = infos[1]
            self.name = infos[2]
            self.dateadd = infos[3]
            self.size = infos[4]
            self.form = infos[5]
            
            addressList = []
            upno = self.upno
            self.relative_address = ""
            while upno != 0:
                database.cur.execute("""SELECT up_id, name FROM items
                                        WHERE id = "%s" """% upno)
                infos = database.cur.fetchone()
                upno = infos[0]
                addressList.append(infos[1])
            
            for i in addressList.reverse():
                self.relative_address += (i + os.sep)
        else:
            return False
            
    def insert2Db(self, database):
        if self.upno and self.name and self.form:
            database.cur.execute("""INSERT INTO items (up_id, name, size, form)
                                    VALUES ( "{upno}", "{name}", "{size}", "{form}" )
                                    """.format(**self.__dict__))
            
            database.cur.execute("""SELECT max(id) FROM items""")
            self.no = database.cur.fetchone[0]
            self.getDbInfo()
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
            
        self.db.cur.execute("""SELECT id FROM items
                                WHERE up_id = "%s"
                                ORDER BY form"""% dirNo)
        
        for i in self.db.cur.fetchall():
            newItem = Item(no=i[0])
            newItem.getDbInfo(database=self.db)
            
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

def insertAll2Db(item, progressItem):
    item.getRealInfo()
    if item.insert2Db():
        try:
            progressItem.increase()
        except AttributeError:
            pass
        
        if item.real_address:
            for i in os.listdir(item.real_address):
                address = item.address + os.sep + i
                newItem = Item(address = address)
                newItem.upno = item.no
                
                insertAll2Db(newItem, progressItem)
    else:
        return False