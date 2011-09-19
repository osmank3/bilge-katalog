#!/usr/bin/env python
#-*- coding:utf-8 -*-

import MySQLdb

def mount(config):
    """function for connecting database with configuration"""
    try:
        db = MySQLdb.connect(   host = config.mysqlServer,
                                user = config.mysqlUserName,
                                passwd = config.mysqlUserPass,
                                db = config.mysqlDbName    )
        return db
    except MySQLdb.Error, e:
        raise Exception(e[0], e[1])

def createUserAndTable(config, db):
    """function for creating new user and database on mysql server."""
    cur = db.cursor()
    cur.execute(""" CREATE USER {mysqlUserName}@{mysqlServer}\
                    IDENTIFIED BY '{mysqlUserPass}'\
                    """.format(**config.__dict__))
    cur.execute(""" GRANT USAGE ON *.* TO {mysqlUserName}@{mysqlServer}\
                    IDENTIFIED BY '{mysqlUserPass}' WITH\
                    MAX_QUERIES_PER_HOUR 0\
                    MAX_CONNECTIONS_PER_HOUR 0\
                    MAX_UPDATES_PER_HOUR 0\
                    MAX_USER_CONNECTIONS 0\
                    """.format(**config.__dict__))
    cur.execute(""" CREATE DATABASE IF NOT EXISTS {mysqlDbName}\
                    """.format(**config.__dict__))
    cur.execute(""" GRANT ALL PRIVILEGES ON {mysqlDbName}.* TO\
                    {mysqlUserName}@{mysqlServer}\
                    """.format(**config.__dict__))
    db.commit()

def prepareTable(db):
    """function for creating tables on database"""
    cur = db.cursor()
    cur.execute(""" CREATE TABLE IF NOT EXISTS items (\
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY ,\
                    up_id INT NOT NULL ,\
                    name TEXT NOT NULL ,\
                    dateadd TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\
                    size INT NOT NULL DEFAULT  '0',\
                    form ENUM(  "file",  "directory" ) NOT NULL )""")
    cur.execute(""" CREATE TABLE IF NOT EXISTS config (\
                    key VARCHAR( 64 ) NOT NULL PRIMARY KEY ,\
                    value TEXT NOT NULL )""")
    db.commit()