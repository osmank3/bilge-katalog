#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

class Main(object):
    def __init__(self, api):
        """Look at api referance from application webpage for using api"""
        self.api = api
        pass
    def install(self, upgradeFrom=None):
        """This function is lauched when extensions installing."""
        pass
    def uninstall(self):
        """This function is lauched when extensions uninstalling."""
        pass
    def run(self, command, params):
        """
        commands            params                          return
        "getFileInfo"       {"no":int,"address":str}        None
        "search"            str --> search text             []
        "showFileInfo"      int --> item no                 {}
        "delete"            int --> item no                 None
        "export"            int --> item no                 json supported python data types
        "import"            {"no":int,"data":exported data} None
        """
        pass
