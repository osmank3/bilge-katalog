#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")


class SampleDB(object):
    def __init__(self):
        """"""
        self.mounted = False
        self.db = None
        self.cur = None
        
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
                                if type(i[j][1]) == str:
                                    i[j][1] = i[j][1].replace("'","\\'")
                                query += "{0} LIKE '%{1}%' ".format(j, i[j][1])
                            else:
                                if type(i[j][1]) == str:
                                    i[j][1] = i[j][1].replace("'","\\'")
                                query += "%s %s '%s' "% (j, i[j][0], i[j][1])
                        elif type(i[j]) in [str,int,long]:
                            if type(i[j]) == str:
                                i[j] = i[j].replace("'","\\'")
                            query += "%s = '%s' "% (j, i[j])
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
            values.append(str(row[i]).replace("'","\\'"))
        
        query += "(%s) "% (", ".join(keys))
        query += "VALUES ('%s')"% ("', '".join(values))
        
        self.cur.execute(query)
        self.db.commit()
    
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
            setlist.append("%s = '%s'"% (i, row[i]).replace("'","\\'"))
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
                            if type(i[j][1]) == str:
                                i[j][1] = i[j][1].replace("'","\\'")
                            query += "{0} LIKE '%{1}%' ".format(j, i[j][1])
                        else:
                            if type(i[j][1]) == str:
                                i[j][1] = i[j][1].replace("'","\\'")
                            query += "%s %s '%s' "% (j, i[j][0], i[j][1])
                    elif type(i[j]) in [str,int,long]:
                        if type(i[j]) == str:
                            i[j] = i[j].replace("'","\\'")
                        query += "%s = '%s' "% (j, i[j])
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
                            if type(i[j][1]) == str:
                                i[j][1] = i[j][1].replace("'","\\'")
                            query += "{0} LIKE '%{1}%' ".format(j, i[j][1])
                        else:
                            if type(i[j][1]) == str:
                                i[j][1] = i[j][1].replace("'","\\'")
                            query += "%s %s '%s' "% (j, i[j][0], i[j][1])
                    elif type(i[j]) in [str,int,long]:
                        if type(i[j]) == str:
                            i[j] = i[j].replace("'","\\'")
                        query += "%s = '%s' "% (j, i[j])
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
