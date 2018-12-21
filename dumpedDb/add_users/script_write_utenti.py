#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import re
import couchdb
from hashlib import md5

__server    = "157.27.26.206"
__dbName    = 'db_detection'
__db4Log    = 'admin'
__user      = 'admin'
__pw        = 'Frequency-Detection-Wireless'
__db4LogCon = None


def make_md5(s):
    encoding = 'utf-8'
    return md5(s.encode(encoding)).hexdigest()


def __cursor():
    """ Ritorna un cursore per scrivere nel database cls.__db4Log. """
    if __dbName in __db4LogCon:
        __db = __db4LogCon[__dbName]
        return __db


def addUser(username, nome, cognome, matricola, mac, pwd):
    """ """
    cur = __cursor()
    id_doc = 0
    for item in cur.view('_design/documenti-view/_view/view_id_utente'):
        if int(item.id) > id_doc:
            id_doc = int(item.id)
    id_doc = int(id_doc)
    id_doc += 1
    utente    = {'username':username, 'nome':nome, 'cognome':cognome, 'matricola':matricola}
    macs      = [{'mac':mac}]
    incontri  = []
    frequenze = []
    entry     = {'_id':str(id_doc), 'utente':utente, 'pwd':pwd, 'ruolo':2, 'macs':macs, 'incontri':incontri, 'frequenze':frequenze, 'tempo_totale': '0', 'punteggio':0}
    cur.save(entry)


def main():
	print("INIZIO ESECUZIONE")
	print("--------------------------------------------------------------------------------")

	entry = []

	with open("mac_address.csv", newline="", encoding='utf-8') as filecsv:
	    reader = csv.reader(filecsv, delimiter=",")
	    for row in reader:
	    	entry.append(row[1])

	global __db4LogCon
	__db4LogCon = couchdb.Server("http://%s:%s@%s:3306/" % (__user, __pw, __server))
	for item in entry:
		doc = item.split()
		username  = doc[0].lower() + "_" + doc[1].lower() # nome_cognome in minuscolo
		nome      = doc[0][0].upper() + doc[0][1:] # prima lettera maiuscola
		cognome   = doc[1][0].upper() + doc[1][1:] # prima lettera maiuscola
		matricola = doc[2].upper() # in maiuscolo
		mac       = doc[3].lower() # in minuscolo
		pwd       = make_md5(make_md5(doc[0].lower())) # md5 in minuscolo
		addUser(username, nome, cognome, matricola, mac, pwd)
		print("[ " + username + " " + nome + " " + cognome + " " + matricola + " " + mac + " " + pwd + " ]")
	__db4LogCon = None

	#print(entry)
		
	print("FINE ESECUZIONE")
	print("--------------------------------------------------------------------------------")


if __name__ == '__main__':
	main()