#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import json

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui_settings import Ui_SettingsForm

class SettingsForm(QtGui.QDialog, Ui_SettingsForm):
    def __init__(self, bilge):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        self.__bilge = bilge
        
        self.changedTabs = []
        
        self.fillPlugins()
        
        #signals
        self.connect(self.AddButton, QtCore.SIGNAL("clicked()"), self.newPlugin)
        self.connect(self.DeleteButton, QtCore.SIGNAL("clicked()"), self.deletePlugin)
        self.connect(self.ResetButton, QtCore.SIGNAL("clicked()"), self.resetSettings)
        self.connect(self.ApplyButton, QtCore.SIGNAL("clicked()"), self.applySettings)
        
        self.connect(self.PluginsTable, QtCore.SIGNAL("itemChanged (QTableWidgetItem *)"), self.enableButtons)
        self.connect(self.Tabs, QtCore.SIGNAL("currentChanged(int)"), self.tabChanged)
        
        
        
    def fillPlugins(self):
        n = 0
        self.PluginsTable.setRowCount(0)
        for i in self.__bilge.plugs.plugins:
            self.PluginsTable.setRowCount(n + 1)
            item = QtGui.QTableWidgetItem()
            self.PluginsTable.setVerticalHeaderItem(n, item)
            item = QtGui.QTableWidgetItem()
            if i["activated"] == True:
                item.setCheckState(2)
            else:
                item.setCheckState(0)
            item.setText(i["name"])
            self.PluginsTable.setItem(n, 0, item)
            item = QtGui.QTableWidgetItem()
            item.setText(i["description"])
            self.PluginsTable.setItem(n, 1, item)
            
            n += 1
    
    def newPlugin(self):
        if self.Tabs.currentIndex() not in self.changedTabs:
            enabled = False
        else:
            enabled = True
        pluginAddress = QtGui.QFileDialog.getOpenFileName(
                                                caption = "Choose Plugin File",
                                                filter = "Plugin File(*.tar.gz)")
        #try:
        if os.path.exists(pluginAddress):
            self.__bilge.plugs.plugInstall(str(pluginAddress))
        #except Exception as e:
        #    print(e)
        self.fillPlugins()
        if not enabled:
            if self.Tabs.currentIndex() in self.changedTabs:
                self.changedTabs.remove(self.Tabs.currentIndex())
            self.ResetButton.setEnabled(False)
            self.ApplyButton.setEnabled(False)
        
    def deletePlugin(self):
        if self.Tabs.currentIndex() not in self.changedTabs:
            enabled = False
        else:
            enabled = True
        items = self.PluginsTable.selectedItems()
        for i in self.__bilge.plugs.plugins:
            if i["name"] == items[0].text():
                self.__bilge.plugs.plugUninstall(i)
                self.fillPlugins()
        if not enabled:
            if self.Tabs.currentIndex() in self.changedTabs:
                self.changedTabs.remove(self.Tabs.currentIndex())
            self.ResetButton.setEnabled(False)
            self.ApplyButton.setEnabled(False)
            
        
    def resetSettings(self):
        if self.Tabs.currentIndex() == 0:
            if 0 in self.changedTabs:
                self.changedTabs.remove(0)
            pass
        elif self.Tabs.currentIndex() == 1:
            self.fillPlugins()
            if 1 in self.changedTabs:
                self.changedTabs.remove(1)
        
        if self.Tabs.currentIndex() not in self.changedTabs:
            self.ResetButton.setEnabled(False)
            self.ApplyButton.setEnabled(False)
        
    def enableButtons(self):
        if self.Tabs.currentIndex() not in self.changedTabs:
            self.changedTabs.append(self.Tabs.currentIndex())
        self.ResetButton.setEnabled(True)
        self.ApplyButton.setEnabled(True)
        
    def tabChanged(self, index):
        if index in self.changedTabs:
            self.ResetButton.setEnabled(True)
            self.ApplyButton.setEnabled(True)
        else:
            self.ResetButton.setEnabled(False)
            self.ApplyButton.setEnabled(False)
            
        
    def applySettings(self):
        if self.Tabs.currentIndex() == 0:
            if 0 in self.changedTabs:
                self.changedTabs.remove(0)
            pass
        elif self.Tabs.currentIndex() == 1:
            n = 0
            settingsChanged = False
            while n < self.PluginsTable.rowCount():
                item = self.PluginsTable.item(n, 0)
                name = item.text()
                if item.checkState() == 0:
                    activated = False
                else:
                    activated = True
                
                for i in self.__bilge.plugs.plugins:
                    if i["name"] == name and i["activated"] != activated:
                        i["activated"] = activated
                        settingsChanged = True
                n += 1
                
            if settingsChanged:
                newConf = json.dumps(self.__bilge.plugs.plugins, default=lambda x:None)
                self.__bilge.conf.setConf("plugins", newConf)
            if 1 in self.changedTabs:
                self.changedTabs.remove(1)
            self.fillPlugins()
            
        self.ResetButton.setEnabled(False)
        self.ApplyButton.setEnabled(False)
