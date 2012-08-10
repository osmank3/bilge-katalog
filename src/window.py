#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui_window import Ui_MainWindow
import catdialogs
import settings

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, bilge):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.__bilge = bilge
        self.exp = bilge.exp
        
        self.setTopCenter()
        self.OptionsButton.setHidden(True)
        self.DetailButton.setHidden(True)
        
        self.setContextMenus()
        self.setOptionsMenu()
        self.setSignals()
        
        self.board = []
        self.boardDo = None # "copy" or "cut"
        
        self.setCatList()
        
    def ready(self):
        return True
        
    def setSignals(self):
        self.actLocation.triggered.connect(self.location)
        self.actBack.triggered.connect(self.back)
        self.actForward.triggered.connect(self.forward)
        self.actUp.triggered.connect(self.up)
        self.actRefresh.triggered.connect(self.refresh)
        
        self.actDel.triggered.connect(self.delete)
        self.actCopy.triggered.connect(self.copy)
        self.actCut.triggered.connect(self.cut)
        self.actPaste.triggered.connect(self.paste)
        
        self.actNewCat.triggered.connect(self.createCat)
        #self.actNewFile.triggered.connect(self.newFile)
        #self.actNewDir.triggered.connect(self.newDir)
        
        self.actExport.triggered.connect(self.exportCat)
        self.actImport.triggered.connect(self.importCat)
        
        self.actOpen.triggered.connect(self.doubleClickAction)
        #self.actInfo.triggered.connect(self.infoAction)
        self.actSearch.triggered.connect(self.searching)
        
        self.actSet.triggered.connect(self.settings)
        
        self.connect(self.CatList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.doubleClickAction)
        self.connect(self.ExpList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.doubleClickAction)
        self.connect(self.CatList, QtCore.SIGNAL("itemActivated(QListWidgetItem *)"), self.doubleClickAction)
        self.connect(self.ExpList, QtCore.SIGNAL("itemActivated(QListWidgetItem *)"), self.doubleClickAction)
        self.connect(self.CatList, QtCore.SIGNAL("itemSelectionChanged()"), self.catSelectionChanged)
        self.connect(self.ExpList, QtCore.SIGNAL("itemSelectionChanged()"), self.expSelectionChanged)
        self.connect(self.CatList, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), self.catRightClick)
        self.connect(self.ExpList, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), self.expRightClick)
        
        self.connect(self.SearchLine, QtCore.SIGNAL("textChanged(QString)"), self.search)
        self.connect(self.LocationLine, QtCore.SIGNAL("returnPressed()"), self.setLocation)
        
        self.connect(self.BackButton, QtCore.SIGNAL("clicked()"), self.back)
        self.connect(self.ForwardButton, QtCore.SIGNAL("clicked()"), self.forward)
    
    def setContextMenus(self):
        self.catContext = QtGui.QMenu(self.CatList)
        self.catContext.addAction(self.actOpen)
        self.catContext.addAction(self.actInfo)
        self.catContext.addSeparator()
        self.catContext.addAction(self.actNewCat)
        self.catContext.addSeparator()
        self.catContext.addAction(self.actExport)
        self.catContext.addAction(self.actImport)
        self.catContext.addSeparator()
        self.catContext.addAction(self.actDel)
        self.catContext.addAction(self.actCut)
        self.catContext.addAction(self.actCopy)
        self.catContext.addAction(self.actPaste)
        
        self.expContext = QtGui.QMenu(self.ExpList)
        self.expContext.addAction(self.actOpen)
        self.expContext.addAction(self.actInfo)
        self.expContext.addSeparator()
        self.expContext.addMenu(self.menuNew)
        self.expContext.addSeparator()
        self.expContext.addAction(self.actDel)
        self.expContext.addAction(self.actCut)
        self.expContext.addAction(self.actCopy)
        self.expContext.addAction(self.actPaste)
        
    def setOptionsMenu(self):
        self.optionsMenu = QtGui.QMenu(self.OptionsButton)
        self.optionsMenu.addMenu(self.menuFile)
        self.optionsMenu.addMenu(self.menuEdit)
        self.optionsMenu.addMenu(self.menuView)
        self.optionsMenu.addMenu(self.menuGo)
        self.optionsMenu.addMenu(self.menuHelp)
        self.OptionsButton.setMenu(self.optionsMenu)
    
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
    
    def setTopCenter(self, operation=None):
        if operation == "search":
            self.LocationLine.setHidden(True)
            self.AddressLabel.setHidden(True)
            self.SearchLine.setHidden(False)
            self.SearchLine.setFocus()
        elif operation == "location":
            self.SearchLine.setHidden(True)
            self.AddressLabel.setHidden(True)
            self.LocationLine.setHidden(False)
            self.LocationLine.setFocus()
        else:
            self.SearchLine.setHidden(True)
            self.LocationLine.setHidden(True)
            self.AddressLabel.setHidden(False)

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
        if self.exp.expObj.curItem():
            self.AddressLabel.setText(self.exp.expObj.curItem().name)
        else:
            self.AddressLabel.clear()
        items = self.exp.listOfDir()
        for i in items:
            QtItem = QtGui.QListWidgetItem(i.name)
            setattr(QtItem, "item", i)
            self.ExpList.addItem(QtItem)
    
    def location(self):
        self.setTopCenter("location")
    
    def setLocation(self):
        address = self.LocationLine.text()
        self.LocationLine.clear()
        dirNames = address.split(os.sep)
        upno = 0
        for i in dirNames:
            if i == "":
                continue
            results = self.__bilge.db.get("items",{"upno":upno,"name":i})
            if len(results) == 1:
                upno = results[0]["no"]
            else:
                upno = None
                break
        
        if upno:
            item = self.__bilge.cat.Item(self.__bilge, no=upno)
            item.getDbInfo()
            self.exp.changeItem(item)
        
        self.refresh()
        self.setTopCenter()
    
    def doubleClickAction(self, selectedItem=None):
        if type(selectedItem) == bool:
            selecteds = []
            for i in self.ExpList.selectedItems():
                selecteds.append(i)
            if len(selecteds) == 0:
                for i in self.CatList.selectedItems():
                    selecteds.append(i)
            if len(selecteds) == 1:
                selectedItem = selecteds[0]
        if selectedItem and selectedItem.item.form == "directory":
            self.exp.changeItem(selectedItem.item)
            self.ExpList.setFocus()
            self.refresh()
                
    def catRightClick(self, point):
        self.CatList.setItemSelected(self.CatList.itemAt(point), True)
        self.catSelectionChanged()
        
        self.catContext.setDefaultAction(self.actOpen)
        
        coordinate = self.CatList.mapToGlobal(point)
        self.catContext.exec_(coordinate)
    
    def expRightClick(self, point):
        self.ExpList.setItemSelected(self.ExpList.itemAt(point), True)
        self.expSelectionChanged()
        
        if self.ExpList.itemAt(point).item.form == "directory":
            self.expContext.setDefaultAction(self.actOpen)
        else:# *** developing *** if form == "file" and file found on drive: default action is opening
            self.expContext.setDefaultAction(self.actInfo)
        
        coordinate = self.ExpList.mapToGlobal(point)
        self.expContext.exec_(coordinate)
    
    def catSelectionChanged(self):
        for i in self.ExpList.selectedItems():
            i.setSelected(False)
        self.actExport.setEnabled(True)
        
        selecteds = []
        for i in self.CatList.selectedItems():
            selecteds.append(i.item)
        self.setButtonsStatus(selecteds)
        self.setInfoLabel(selecteds)
    
    def expSelectionChanged(self):
        for i in self.CatList.selectedItems():
            i.setSelected(False)
        self.actExport.setEnabled(False)
        
        selecteds = []
        for i in self.ExpList.selectedItems():
            selecteds.append(i.item)
        self.setButtonsStatus(selecteds)
        self.setInfoLabel(selecteds)
        
    def setButtonsStatus(self, selecteds):
        if len(selecteds) == 0:
            self.actDel.setEnabled(False)
            self.actCut.setEnabled(False)
            self.actCopy.setEnabled(False)
            self.actExport.setEnabled(False)
            self.actInfo.setEnabled(False)
        else:
            self.actDel.setEnabled(True)
            self.actCut.setEnabled(True)
            self.actCopy.setEnabled(True)
            if len(selecteds) == 1:
                self.actInfo.setEnabled(True)
                self.actOpen.setEnabled(True)
            else:
                self.actInfo.setEnabled(False)
                self.actOpen.setEnabled(False)
        if not self.boardDo and not self.board:
            self.actPaste.setEnabled(False)
        elif len(selecteds) != 1:
            self.actPaste.setEnabled(False)
        else:
            self.actPaste.setEnabled(True)
    
    def setInfoLabel(self, selecteds):
        if len(selecteds) == 1:
            self.DetailButton.setHidden(False)
            item = selecteds[0]
            textFormat = {
                            "addressTitle" : self.tr("Address"),
                            "address" : item.relative_address,
                            "sizeTitle" : self.tr("Size"),
                            "size" : item.size,
                            "formTitle" : self.tr("Type"),
                            "form" : item.form,
                            "dateTitle" : self.tr("Adding Date"),
                            "date" : item.dateadd.isoformat(" ")
                         }
            if item.upno == 0:
                textFormat["address"] = "/"
            self.InfoLabel.setText("""<html><head/><body>
                    <div>
                        <span><b>{formTitle}</b>: {form} </span>
                        <span><b>{sizeTitle}</b>: {size} </span>
                        <span><b>{dateTitle}</b>: {date} </span>
                    </div>
                    <div>
                        <span><b>{addressTitle}</b>: {address}</span>
                    </div>
                    </body></html>""".format(**textFormat))
        else:
            self.InfoLabel.clear()
            self.DetailButton.setHidden(True)
    
    def delete(self):
        selecteds = []
        for i in self.ExpList.selectedItems():
            selecteds.append(i.item)
        for i in self.CatList.selectedItems():
            if len(selecteds) == 0:
                selecteds.append(i.item)
            
        for i in selecteds:
            i.delete()
        
        self.setCatList()
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
            selecteds = []
            for i in self.ExpList.selectedItems():
                selecteds.append(i.item)
            for i in self.CatList.selectedItems():
                if len(selecteds) == 0:
                    selecteds.append(i.item)
            if len(selecteds) == 1 and selecteds[0].item.form == "directory":
                upno = selecteds[0].no
            else:
                upno = self.exp.expObj.curItem().no
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
            self.setTopCenter("search")
            self.actLocation.setEnabled(False)
            
            self.expOldName = self.exp.expObj.name
            self.exp.newExp("search","search")
            self.exp.changeExp("search")
            
        else:
            self.SearchLine.clear()
            self.setTopCenter()
            self.actLocation.setEnabled(True)
            
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
        createDialog = catdialogs.CatDialog(self.__bilge, "create")
        createDialog.exec_()
        self.setCatList()
        self.refresh()
        
    def exportCat(self):
        selecteds = []
        for i in self.CatList.selectedItems():
            selecteds.append(i.item)
        exportDialog = catdialogs.CatDialog(self.__bilge, "export", selecteds)
        exportDialog.exec_()
    
    def importCat(self):
        importDialog = catdialogs.CatDialog(self.__bilge, "import")
        importDialog.exec_()
        self.setCatList()
        self.refresh()
        
    def settings(self):
        settingsDialog = settings.SettingsForm(self.__bilge)
        settingsDialog.exec_()

