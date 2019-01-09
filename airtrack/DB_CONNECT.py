'''
Created on 26 ott 2018

DataMapper

@author: Giovanni, ...
'''

class DB_CONNECT():

    #__server = "localhost"
    __server = "157.27.26.206"
    __dbName = 'db_detection'
    __db4Log = 'admin'
    __user   = 'admin'
    #__pw     = 'admin'
    __pw     = 'Frequency-Detection-Wireless'

    @classmethod
    def get__server(cls):
        return cls.__server;

    @classmethod
    def get__dbName(cls):
        return cls.__dbName;

    @classmethod
    def get__db4Log(cls):
        return cls.__db4Log;

    @classmethod
    def get__user(cls):
        return cls.__user;

    @classmethod
    def get__pw(cls):
        return cls.__pw;
