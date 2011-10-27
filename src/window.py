#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui_window import Ui_MainWindow

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, explore):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.exp = explore
        
        self.setToolBars()
        self.setSignals()
        
        self.setCatList()
        
    
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
        
        self.searchLine = QtGui.QLineEdit()
        self.searchButton = QtGui.QPushButton()
        self.searchButton.setObjectName("searchButton")
        self.searchButton.setText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.SearchBar.addWidget(self.searchLine)
        self.SearchBar.addWidget(self.searchButton)
        
    def setSignals(self):
        pass
        self.actBack.triggered.connect(self.back)
        self.actForward.triggered.connect(self.forward)
        self.actUp.triggered.connect(self.up)
        self.actRefresh.triggered.connect(self.refresh)
        
        #self.actDel.triggered.connect(self.delete)
        #self.actCopy.triggered.connect(self.copy)
        #self.actCut.triggered.connect(self.cut)
        #self.actPaste.triggered.connect(self.paste)
        
        #self.actNewFile.triggered.connect(self.newFile)
        #self.actNewDir.triggered.connect(self.newDir)
        
        #self.actInfo.triggered.connect(self.infoAction)
        
        #self.actSet.triggered.connect(self.settings)
        
        self.connect(self.CatList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.doubleClickAction)
        self.connect(self.ExpList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.doubleClickAction)
        self.connect(self.CatList, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.clickAction)
        self.connect(self.ExpList, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.clickAction)
        
        #self.connect(self.searchButton, QtCore.SIGNAL("clicked()"), self.search)
        #self.connect(self.searchLine, QtCore.SIGNAL("returnPressed()"), self.searchButton, QtCore.SLOT("click()"))
        #self.connect(self.searchLine, QtCore.SIGNAL("textChanged(QString)"), self.searchButtonStatus)
        
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


#testing lines start in here
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(None)
    window.show()
    sys.exit(app.exec_())