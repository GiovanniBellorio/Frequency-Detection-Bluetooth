#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import couchdb

#__server = "192.168.43.120"
#__server = "localhost"
__server = "157.27.134.188"
__dbName = 'db_detection'
__db4Log = 'admin'
__user   = 'admin'
__pw     = 'admin'

if __name__ == '__main__':
	print("INIZIO ESECUZIONE")
	print("--------------------------------------------------------------------------------")

	if str(sys.argv[1]) == "b":
		os.system("rm dumpedDB.json")
		os.system("bash couchdb-backup.sh -b -H "+__server+" -d "+__dbName+" -f dumpedDB.json -u "+__user+" -p "+__pw)

	if str(sys.argv[1]) == "r":
		__db4LogCon = couchdb.Server("http://%s:%s@%s:5984/" % (__user, __pw, __server))
		__db4LogCon.delete(__dbName)
		__db4LogCon.create(__dbName)
		__db4LogCon = None
		os.system("bash couchdb-backup.sh -r -H "+__server+" -d "+__dbName+" -f dumpedDB.json -u "+__user+" -p "+__pw)
		
	print("FINE ESECUZIONE")
	print("--------------------------------------------------------------------------------")