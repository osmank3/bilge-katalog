#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui_createcat import Ui_CreateCatForm

class CreateCat(QtGui.QDialog, Ui_CreateCatForm):
    def __init__(self, bilge):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        self.__bilge = bilge
        
        self.connect(self.CatNextButton, QtCore.SIGNAL("clicked()"), self.next)
        self.connect(self.CatDirButton, QtCore.SIGNAL("clicked()"), self.chooseDir)
    
    def chooseDir(self):
        directory = QtGui.QFileDialog.getExistingDirectory(
                                        caption = "Choose Directory",
                                        options = QtGui.QFileDialog.ShowDirsOnly
                                        | QtGui.QFileDialog.DontResolveSymlinks)
        if directory and directory != "":
            self.CatDirLine.setText(directory)
        else:
            self.CatDirLine.clear()
    
    def next(self):
        directory = str(self.CatDirLine.text())
        if directory != "" and os.path.exists(directory):
            self.CatProgress.setProperty("value", 0)
            self.CatStacked.setCurrentWidget(self.CatPage2)
            
            self.progressItem = progress(directory)
            self.connect(self.progressItem, QtCore.SIGNAL("progressStat(int)"), self.CatProgress.setValue)
            self.connect(self.progressItem, QtCore.SIGNAL("finished(bool)"), self.CatCloseButton, QtCore.SLOT("setEnabled(bool)"))
            self.connect(self.progressItem, QtCore.SIGNAL("refresh"), self.repaint)
            
            self.setCursor(QtCore.Qt.WaitCursor)
            
            item = self.__bilge.cat.Item(self.__bilge, address=directory)
            item.upno = 0
            item.insert2DbRecursive(self.progressItem)
            
            self.setCursor(QtCore.Qt.ArrowCursor)

class progress(QtCore.QObject):
        def __init__(self, address=None):
            QtCore.QObject.__init__(self)
            
            self.numOfItems = 0
            self.curNum = 0
            if address:
                self.numOfItems = self.getNumOfItems(address) + 1
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
