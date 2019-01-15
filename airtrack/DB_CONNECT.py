#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Created on 26 ott 2018

DataMapper

@author: Giovanni, ...
'''

import configparser

class DB_CONNECT():
    #__server = "127.0.0.1"
    __server = None
    __dbName = 'db_detection'
    __db4Log = 'admin'
    __user   = None
    __pw     = None
    __port   = None

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.out')
        DB_CONNECT.__server = config['topsecret.server.com']['Server']
        DB_CONNECT.__port   = config['topsecret.server.com']['Port']
        DB_CONNECT.__user   = config['topsecret.server.com']['User']
        DB_CONNECT.__pw     = config['topsecret.server.com']['Password']

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

    def get__port(cls):
        return cls.__port;
