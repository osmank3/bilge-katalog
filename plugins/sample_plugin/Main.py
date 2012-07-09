#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

class Main(object):
    def __init__(self, api):
        self.api = api
        pass
    def install(self):
        pass
    def uninstall(self):
        pass
