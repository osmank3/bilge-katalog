#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

#For using unicode utf-8 on python2
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")


class SampleDB(object):
    def __init__(self):
        """"""
        self.mounted = False
        self.db = None
        self.cur = None
        self.escText = "\\"
        
    def mount(self, config):
        """
        function for connecting database with configuration
        
        config : database configuration dictionary
        """
        pass #after mounting self.mounted = True
        
    def ready(self):
        return self.mounted
        
    def get(self, table, where=None, order=None):
        """
        function for taking data from database
        
        table : ""
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        order : []
        
        returned : [{"key":"value", ...}, ...]
        """
        if not self.mounted:
            return
        
        keys = self.getkeys(table)
        
        query = "SELECT * FROM %s "% table
        if where != None:
            query += "WHERE "
            if type(where) == dict:
                where = [where]
            for i in where:
                if type(i) == dict:
                    query += " ( "
                    n = 0
                    for j in i.keys():
                        if n != 0:
                            query += "AND "
                        if type(i[j]) == list:
                            if i[j][0].lower() == "like":
                                query += "{0} LIKE '%{1}%' ".format(j, self.__setEsc(i[j][1]))
                            else:
                                query += "%s %s '%s' "% (j, i[j][0], self.__setEsc(i[j][1]))
                        elif type(i[j]) not in [list, dict]:
                            query += "%s = '%s' "% (j, self.__setEsc(i[j]))
                        n += 1
                    query += " ) "
                elif type(i) == str:
                    query += "%s "% i
        
        if order != None:
            if type(order) == str:
                order = [order]
            query += "ORDER BY " + ", ".join(order)
        
        self.cur.execute(query)
        results = []
        for i in self.cur.fetchall():
            result = {}
            n = 0
            while len(i) > n:
                result[keys[n]] = i[n]
                n += 1
            results.append(result)
        
        return results
        
    def getkeys(self, table):
        """
        function for taking column names from database
        
        table : ""
        
        returned : []
        """
        pass
    
    def insert(self, table, row):
        """
        function for inserting row to database
        
        table : ""
        row : {"key":"value", ...}
        """
        if not self.mounted:
            return
        
        query = "INSERT INTO %s "% table
        keys = []
        values = []
        for i in row.keys():
            keys.append(str(i))
            values.append(self.__setEsc(str(row[i])))
        
        query += "(`%s`) "% ("`, `".join(keys))
        query += "VALUES ('%s')"% ("', '".join(values))
        
        self.cur.execute(query)
    
    def update(self, table, row, where):
        """
        function for updating the row where on the database
        
        table : ""
        row : {"key":"value", ...}
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        """
        if not self.mounted:
            return
        
        query = "UPDATE %s SET "% table
        setlist = []
        for i in row.keys():
            setlist.append("`%s` = '%s'"% (i, self.__setEsc(row[i])))
        query += ", ".join(setlist) + " WHERE "
        if type(where) == dict:
            where = [where]
        for i in where:
            if type(i) == dict:
                query += " ( "
                n = 0
                for j in i.keys():
                    if n != 0:
                        query += "AND "
                    if type(i[j]) == list:
                        if i[j][0].lower() == "like":
                            query += "`{0}` LIKE '%{1}%' ".format(j, self.__setEsc(i[j][1]))
                        else:
                            query += "`%s` %s '%s' "% (j, i[j][0], self.__setEsc(i[j][1]))
                    elif type(i[j]) not in [list,dict]:
                        query += "`%s` = '%s' "% (j, self.__setEsc(i[j]))
                    n += 1
                query += " ) "
            elif type(i) == str:
                query += "%s "% i
        
        self.cur.execute(query)
    
    def delete(self, table, where):
        """
        function for deleting anything from database
        
        table : ""
        where : [{"key":["like or =","value"] or "value"},"AND or OR", ...]
        """
        if not self.mounted:
            return
        
        query = "DELETE FROM %s WHERE "% table
        if type(where) == dict:
            where = [where]
        for i in where:
            if type(i) == dict:
                query += " ( "
                n = 0
                for j in i.keys():
                    if n != 0:
                        query += "AND "
                    if type(i[j]) == list:
                        if i[j][0].lower() == "like":
                            query += "{0} LIKE '%{1}%' ".format(j, self.__setEsc(i[j][1]))
                        else:
                            query += "%s %s '%s' "% (j, i[j][0], self.__setEsc(i[j][1]))
                    elif type(i[j]) not in [list,dict]:
                        query += "%s = '%s' "% (j, self.__setEsc(i[j]))
                    n += 1
                query += " ) "
            elif type(i) == str:
                query += "%s "% i
        
        self.cur.execute(query)
    
    def createTable(self, table, keys):
        """
        function for creating table on database
        
        table : ""
        keys : {"key":{ "type":"TYPE","null":False,"auto":False,
                        "primary":False,"default":"DEFAULT"     }, ...}
        """    
        pass
        
    def deleteTable(self, table):
        """
        function for deleting table on database
        
        table : ""
        """
        if "," not in table:
            query = "DROP TABLE IF EXISTS %s"% table
            self.cur.execute(query)
            self.db.commit()
    
    def sync(self):
        self.db.commit()
    
    def __setEsc(self, text):
        if type(text) == str:
            text = text.replace("'","%s'"% (self.escText))
        return text
