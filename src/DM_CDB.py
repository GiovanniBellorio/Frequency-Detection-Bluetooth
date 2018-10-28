'''
Created on 26 ott 2018

DataMapper

@author: Giovanni
'''

#from datetime import datetime
import logging
import couchdb

class DM_CDB():
    """ Data mapper verso CouchDB. Per semplicità, i parametri di connessione sono attributi di classe: dovrebbero essere
        scritti in un file esterno e caricati durante __init__. """
    __server = "localhost"
    __dbName = 'db_detection'
    __db = None
    __db4Log = 'admin'
    __user = 'admin'
    __pw = 'admin'
    __dbCon = None # La connessione è condivisa !
    __db4LogCon = None # La connessione è condivisa !
    __nIstanze = 0
    
    @classmethod
    def __open(cls):
        if cls.__dbCon is None:
            try: # readonly
                cls.__dbCon = couchdb.Server("http://%s:5984/" % (cls.__server))
                logging.info("Connection to database " + cls.__dbName + " created.")
            except couchdb.ServerError as err:
                logging.error("Error connecting to CouchDB at %s.\nDetails: %s.", cls.__server, err)
                cls.__dbCon = cls.__db4LogCon = None
                exit()
            else: # Questo else è del TRY
                try: # read - write
                    cls.__db4LogCon = couchdb.Server("http://%s:%s@%s:5984/" % (cls.__user, cls.__pw, cls.__server))
                    logging.info("Connection to database " + cls.__dbName + " created.")
                except couchdb.ServerError as err:
                    logging.error("Error connecting to couchdb at %s.\nDetails: %s.", cls.__server, err)
                    cls.__dbCon = cls.__db4LogCon = None
                    exit()
                return "New connection opened."
        return "Connection already opened."
    
    @classmethod
    def __close(cls):
        if cls.__nIstanze == 0 and cls.__dbCon is not None:
            cls.__dbCon.close()
            cls.__db4LogCon.close()
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
        DM_CDB.__open()
        DM_CDB.__nIstanze += 1

    def close(self):
        """ Chiude in modo esplicito la connessione, se non ci sono altre istanze attive """
        self.__del__()
    
    def getCountUsernamePassword(self, username, password):
        cur = DM_CDB.__cursor()
        count = 0
        for item in cur.view('_design/documenti-view/_view/view_usr_pwd'):
            username_db = item.key
            password_db = item.value
            if username == username_db and password == password_db:
                count += 1
        return count
        
    def __del__(self):
        DM_CDB.__nIstanze -= 1
        DM_CDB.__close()