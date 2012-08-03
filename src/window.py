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
from ui_window import Ui_MainWindow
import createcat
import settings

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, bilge):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.__bilge = bilge
        self.exp = bilge.exp
        
        self.setToolBars()
        self.setSignals()
        
        self.board = []
        self.boardDo = None # "copy" or "cut"
        
        self.setCatList()
        
    def ready(self):
        return True
    
    def setToolBars(self):
        """Adding toolbars actions"""
        self.ExpBar.addAction(self.actBack)
        self.ExpBar.addAction(self.actForward)
        self.ExpBar.addAction(self.actUp)
        self.ExpBar.addAction(self.actRefresh)
        
        self.EditBar.addAction(self.actCut)
        self.EditBar.addAction(self.actCopy)
        self.EditBar.addAction(self.actPaste)
        self.EditBar.addAction(self.actDel)
        self.EditBar.addAction(self.actExport)
        
        self.searchLine = QtGui.QLineEdit()
        self.searchLine.setEnabled(False)
        self.searchButton = QtGui.QPushButton()
        self.searchButton.setCheckable(True)
        self.searchButton.setObjectName("searchButton")
        self.searchButton.setText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.SearchBar.addWidget(self.searchLine)
        self.SearchBar.addWidget(self.searchButton)
        
    def setSignals(self):
        self.actBack.triggered.connect(self.back)
        self.actForward.triggered.connect(self.forward)
        self.actUp.triggered.connect(self.up)
        self.actRefresh.triggered.connect(self.refresh)
        
        self.actDel.triggered.connect(self.delete)
        self.actCopy.triggered.connect(self.copy)
        self.actCut.triggered.connect(self.cut)
        self.actPaste.triggered.connect(self.paste)
        
        self.actExit.triggered.connect(self.close)
        
        self.actNewCat.triggered.connect(self.createCat)
        #self.actNewFile.triggered.connect(self.newFile)
        #self.actNewDir.triggered.connect(self.newDir)
        
        self.actExport.triggered.connect(self.exportCat)
        self.actImport.triggered.connect(self.importCat)
        
        #self.actInfo.triggered.connect(self.infoAction)
        
        self.actSet.triggered.connect(self.settings)
        
        self.connect(self.CatList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.doubleClickAction)
        self.connect(self.ExpList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.doubleClickAction)
        self.connect(self.CatList, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.clickAction)
        self.connect(self.ExpList, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.clickAction)
        
        self.connect(self.searchButton, QtCore.SIGNAL("toggled(bool)"), self.searching)
        self.connect(self.searchLine, QtCore.SIGNAL("textChanged(QString)"), self.search)
        
    def setCatList(self, itemList=None):
        if itemList:
            catalogs = itemList
        else:
            class rootItem(object):
                no = 0
            catalogs = self.exp.listOfDir(rootItem())
        
        self.CatList.clear()
        for i in catalogs:
            QtItem = QtGui.QListWidgetItem(i.name)
            setattr(QtItem, "item", i)
            self.CatList.addItem(QtItem)

    def back(self):
        self.exp.back()
        self.refresh()
    
    def forward(self):
        self.exp.forward()
        self.refresh()
    
    def up(self):
        self.exp.up()
        self.refresh()
    
    def refresh(self):
        self.ExpList.clear()
        items = self.exp.listOfDir()
        for i in items:
            QtItem = QtGui.QListWidgetItem(i.name)
            setattr(QtItem, "item", i)
            self.ExpList.addItem(QtItem)
        self.clickAction()
    
    def doubleClickAction(self, selectedItem=None):
        if selectedItem and selectedItem.item.form == "directory":
            self.exp.changeItem(selectedItem.item)
            self.refresh()
    
    def clickAction(self, selectedItem=None):
        for i in self.ExpList.selectedItems():
            i.setSelected(False)
        for i in self.CatList.selectedItems():
            i.setSelected(False)
        if selectedItem:
            selectedItem.setSelected(True)
            if selectedItem in self.CatList.selectedItems():
                self.actExport.setEnabled(True)
            else:
                self.actExport.setEnabled(False)
    
    def delete(self):
        selecteds = []
        for i in self.ExpList.selectedItems():
            selecteds.append(i.item)
        for i in self.CatList.selectedItems():
            if len(selecteds) == 0:
                selecteds.append(i.item)
            
        for i in selecteds:
            i.delete()
        
        self.refresh()
        
    def copy(self):
        selecteds = []
        for i in self.ExpList.selectedItems():
            selecteds.append(i.item)
        for i in self.CatList.selectedItems():
            if len(selecteds) == 0:
                selecteds.append(i.item)
            
        self.board = selecteds[:]
        self.boardDo = "copy"
    
    def cut(self):
        selecteds = []
        for i in self.ExpList.selectedItems():
            selecteds.append(i.item)
        for i in self.CatList.selectedItems():
            if len(selecteds) == 0:
                selecteds.append(i.item)
            
        self.board = selecteds[:]
        self.boardDo = "cut"
    
    def paste(self):
        if self.boardDo and self.board:
            upno = self.exp.expObj.curItem().no
            #*** developing **** edit when context menu is ready for using
            for i in self.board:
                if self.boardDo == "copy":
                    i.copyInDb(upno)
                    
                elif self.boardDo == "cut":
                    info = {"upno":upno}
                    i.update(info)
            
            if self.boardDo == "cut":
                self.board = []
                self.boardDo = None
            
            self.refresh()
            
    def searching(self, status):
        if status:
            self.searchLine.setEnabled(True)
            
            self.expOldName = self.exp.expObj.name
            self.exp.newExp("search","search")
            self.exp.changeExp("search")
            
        else:
            self.searchLine.setEnabled(False)
            self.searchLine.clear()
            
            self.exp.changeExp(self.expOldName)
            del self.expOldName
        
        self.refresh()
        
    def search(self, text):
        if len(text) > 2:
            self.exp.fillSearchList(str(text))
        else:
            self.exp.expObj.searchList = []
        
        self.refresh()
        
    def createCat(self):
        createDialog = createcat.CreateCat(self.__bilge)
        createDialog.exec_()
        self.setCatList()
        self.refresh()
        
    def settings(self):
        settingsDialog = settings.SettingsForm(self.__bilge)
        settingsDialog.exec_()
        
    def exportCat(self):
        selecteds = []
        for i in self.CatList.selectedItems():
            selecteds.append(i.item)
        
        exportCatList = []
        for i in selecteds:
            exportCatList.append(i.exportFromDb())
        
        if len(exportCatList) > 0:
            exportDict = {
                            "exportDate" : datetime.datetime.now(),
                            "exporterName" : "Bilge-Katalog",
                            "exporterVersion" : 0.1,
                            "items" : exportCatList
                         }
            jsonFileName = QtGui.QFileDialog.getSaveFileName(
                                                caption = "Save Export File",
                                                filter = "Json File(*.json)")
            jsonFile = open(jsonFileName, "w")
            jsonFile.write(json.dumps(exportDict, indent=2, sort_keys=True, default=lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None))
            jsonFile.close()
            QtGui.QMessageBox.information(  self, "Exporting",
                                            "Catalog(s) exported to:\n {0}.".format(jsonFileName), 0)
    
    def importCat(self):
        jsonFileName = QtGui.QFileDialog.getOpenFileName(
                                                caption = "Choose Import File",
                                                filter = "Json File(*.json)")
        if os.path.exists(jsonFileName):
            jsonFile = open(jsonFileName, "r")
            importDict = json.loads(jsonFile.read())
            jsonFile.close()
            
            if importDict["exporterName"] == "Bilge-Katalog":
                for i in importDict["items"]:
                    newItem = self.__bilge.cat.Item(self.__bilge)
                    newItem.import2Db(i)
            
            QtGui.QMessageBox.information(  self, "Importing",
                                            "Importing is completed.", 0)
            
        self.setCatList()
        self.refresh()
            
            

#testing lines start in here
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(None)
    window.show()
    sys.exit(app.exec_())
