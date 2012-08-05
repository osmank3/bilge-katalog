#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import json
import datetime

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui_catdialogs import Ui_CatDialogs

class CatDialog(QtGui.QDialog, Ui_CatDialogs):
    def __init__(self, bilge, method, params=None):
        """
        method          params
        "create"        None
        "import"        None
        "export"        [itemList]
        """
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        self.__bilge = bilge
        self.method = method
        self.params = params
        
        if self.method == "export":
            self.CatLabel.setText(self.tr("Choose a json file for saving"))
            self.CatNextButton.setText(self.tr("Export"))
            self.CatProgressLabel.setText(self.tr("Catalog exporting..."))
        elif self.method == "import":
            self.CatLabel.setText(self.tr("Choose a json file for importing"))
            self.CatNextButton.setText(self.tr("Import"))
            self.CatProgressLabel.setText(self.tr("Catalog importing..."))
        
        self.connect(self.CatNextButton, QtCore.SIGNAL("clicked()"), self.next)
        self.connect(self.CatToolButton, QtCore.SIGNAL("clicked()"), self.chooseAddress)
    
    def chooseAddress(self):
        if self.method == "create":
            address = QtGui.QFileDialog.getExistingDirectory(
                                        caption = "Choose Directory",
                                        options = QtGui.QFileDialog.ShowDirsOnly
                                        | QtGui.QFileDialog.DontResolveSymlinks)
        elif self.method == "export":
            address = QtGui.QFileDialog.getSaveFileName(
                                        caption = "Save Export File",
                                        filter = "Json File(*.json)")
        elif self.method == "import":
            address = QtGui.QFileDialog.getOpenFileName(
                                        caption = "Choose Import File",
                                        filter = "Json File(*.json)")
        else:
            address = ""
        
        if address and address != "":
            self.CatAddressLine.setText(address)
        else:
            self.CatAddressLine.clear()
    
    def next(self):
        address = str(self.CatAddressLine.text())
        if address != "":
            self.CatProgress.setProperty("value", 0)
            self.CatStacked.setCurrentWidget(self.CatPage2)
            if self.method in ["create","import"] and os.path.exists(address):
                if self.method == "create":
                    self.progressItem = progress(address)
                else:
                    jsonFile = open(address, "r")
                    importDict = json.loads(jsonFile.read())
                    jsonFile.close()
                    
                    if importDict["exporterName"] == "Bilge-Katalog":
                        num = 0
                        for i in importDict["items"]:
                            num += numOfItems(i)
                    
                    self.progressItem = progress(numbers=num)
                self.connect(self.progressItem, QtCore.SIGNAL("progressStat(int)"), self.CatProgress.setValue)
                self.connect(self.progressItem, QtCore.SIGNAL("finished(bool)"), self.CatCloseButton, QtCore.SLOT("setEnabled(bool)"))
                self.connect(self.progressItem, QtCore.SIGNAL("refresh"), self.repaint)
                
                self.setCursor(QtCore.Qt.WaitCursor)
                
                if self.method == "create":
                    item = self.__bilge.cat.Item(self.__bilge, address=address)
                    item.upno = 0
                    item.insert2DbRecursive(self.progressItem)
                
                elif self.method == "import":
                    if importDict["exporterName"] == "Bilge-Katalog":
                        for i in importDict["items"]:
                            newItem = self.__bilge.cat.Item(self.__bilge)
                            newItem.import2Db(i, self.progressItem)
                
                self.setCursor(QtCore.Qt.ArrowCursor)
            elif self.method == "export":
                exportCatList = []
                for i in self.params:
                    exportCatList.append(i.exportFromDb())
                
                if len(exportCatList) > 0:
                    exportDict = {
                                    "exportDate" : datetime.datetime.now(),
                                    "exporterName" : "Bilge-Katalog",
                                    "exporterVersion" : 0.1,
                                    "items" : exportCatList
                                 }
                    jsonFile = open(address, "w")
                    jsonFile.write(json.dumps(exportDict, indent=2, sort_keys=True, default=lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None))
                    jsonFile.close()
                    self.CatProgress.setProperty("value", 100)
                    self.CatCloseButton.setEnabled(True)

def numOfItems(itemDict):
    num = 1
    if itemDict["form"] == "directory":
        for i in itemDict["content"]:
            if itemDict["form"] == "directory":
                num += numOfItems(i)
            else:
                num += 1
    return num

class progress(QtCore.QObject):
        def __init__(self, address=None, numbers=None):
            QtCore.QObject.__init__(self)
            
            self.numOfItems = 0
            self.curNum = 0
            if address:
                self.numOfItems = self.getNumOfItems(address) + 1
            elif numbers:
                self.numOfItems = numbers
            else:
                self.numOfItems = 1
            
        def getNumOfItems(self, address):
            oldDir = os.getcwd()
            os.chdir(address)
            dirList = os.listdir("./")
            numOfItems = len(dirList)
            
            for i in dirList:
                if os.path.isdir(i):
                    numOfItems += self.getNumOfItems(i)
                    
            os.chdir(oldDir)
            return numOfItems
            
        def increase(self):
            self.curNum += 1
            self.showPercent()
            
        def getPercent(self):
            percent = 100 * self.curNum / self.numOfItems
            return percent
            
        def showPercent(self):
            if self.getPercent() == 100:
                self.emit(QtCore.SIGNAL("progressStat(int)"), self.getPercent())
                self.emit(QtCore.SIGNAL("finished(bool)"), True)
                self.emit(QtCore.SIGNAL("refresh"))
            else:
                self.emit(QtCore.SIGNAL("progressStat(int)"), self.getPercent())
                self.emit(QtCore.SIGNAL("refresh"))
