'''
Created on 26 ott 2018

DataMapper

@author: Giovanni, ...

'''

#from datetime import datetime
import logging
import couchdb
import datetime
import time
from DB_CONNECT import DB_CONNECT

class DM_CDB():
    """ Data mapper verso CouchDB. """
    __server = None
    __dbName = None
    __db4Log = None
    __user = None
    __pw = None
    __db = None
    __dbCon = None # La connessione è condivisa !
    __db4LogCon = None # La connessione è condivisa !
    __nIstanze = 0

    @classmethod
    def __open(cls):
        if cls.__dbCon is None:
            try: # readonly
                cls.__dbCon = couchdb.Server("http://%s:3306/" % (cls.__server))
                logging.info("Connection to database " + cls.__dbName + " created.")
            except couchdb.ServerError as err:
                logging.error("Error connecting to CouchDB at %s.\nDetails: %s.", cls.__server, err)
                cls.__dbCon = cls.__db4LogCon
                exit()
            else: # Questo else è del TRY
                try: # read - write
                    cls.__db4LogCon = couchdb.Server("http://%s:%s@%s:3306/" % (cls.__user, cls.__pw, cls.__server))
                    logging.info("Connection to database " + cls.__dbName + " created.")
                except couchdb.ServerError as err:
                    logging.error("Error connecting to couchdb at %s.\nDetails: %s.", cls.__server, err)
                    cls.__dbCon = cls.__db4LogCon
                    exit()
                return "New connection opened."
        return "Connection already opened."

    @classmethod
    def __close(cls):
        if cls.__nIstanze == 0 and cls.__dbCon is not None:
            #cls.__dbCon.close()
            #cls.__db4LogCon.close()
            logging.info("Connection closed.")
            cls.__dbCon = cls.__db4LogCon = None

    @classmethod
    def __cursor(cls):
        """ Ritorna un cursore che restituisce dict invece di tuple per ciascuna riga di una select."""
        if cls.__dbName in cls.__dbCon:
            cls.__db = cls.__dbCon[cls.__dbName]
            return cls.__db

    @classmethod
    def __cursor4log(cls):
        """ Ritorna un cursore per scrivere nel database cls.__db4Log. """
        if cls.__dbName in cls.__db4LogCon:
            cls.__db = cls.__db4LogCon[cls.__dbName]
            return cls.__db


    def __init__(self):
        """ Import parametri da file """
        self.db_connect = DB_CONNECT()
        DM_CDB.__server = self.db_connect.get__server()
        DM_CDB.__dbName = self.db_connect.get__dbName()
        DM_CDB.__db4Log = self.db_connect.get__db4Log()
        DM_CDB.__user   = self.db_connect.get__user()
        DM_CDB.__pw     = self.db_connect.get__pw()

        """ Connessione db """
        DM_CDB.__open()
        DM_CDB.__nIstanze += 1


    def close(self):
        """ Chiude in modo esplicito la connessione, se non ci sono altre istanze attive """
        self.__del__()

    def getCountUsernamePassword(self, username, password):
        """ """
        cur = DM_CDB.__cursor()
        num_rows = 0
        id_utente = 0
        for item in cur.view('_design/documenti-view/_view/view_usr_pwd'):
            key = item.key
            username_db = key['username']
            password_db = item.value
            if username == username_db and password == password_db:
                num_rows += 1
                id_utente = item.id
        return num_rows, id_utente

    def getRuoloUsername(self, id_utente):
        """ """
        cur = DM_CDB.__cursor()
        ruolo = 0
        for item in cur.view('_design/documenti-view/_view/view_id_utente'):
            if item.id == id_utente:
                ruolo = item.key
        return ruolo

    def getAllMac(self):
        """ """
        cur = DM_CDB.__cursor()
        mac = []
        for item in cur.view('_design/documenti-view/_view/view_id_mac'):
            mac.append(item.value[0]['mac'])
        return mac

    def update_Records(self, new_record):
        cur = DM_CDB.__cursor()
        for item in cur.view("_design/documenti-view/_view/view_id_mac"):
            mac = item.value[0]['mac']
            if mac == new_record.mac_addr:
                id = item.id
                break

        current_date = datetime.date.today()
        current_date = current_date.strftime("%d-%m-%Y")
        doc = cur[str(id)]
        doc['frequenze'].append({"data": current_date,
                                 "ora_inizio": str(datetime.datetime.fromtimestamp(new_record.first_time).strftime('%H:%M:%S')),
                                 "ora_fine": str(datetime.datetime.fromtimestamp(new_record.last_time).strftime('%H:%M:%S')),
                                 "intervallo": str(datetime.timedelta(seconds=(new_record.last_time - new_record.first_time))),
                                 "incontro": ""})
        cur[doc.id] = doc

    def __del__(self):
        DM_CDB.__nIstanze -= 1
        DM_CDB.__close()
