'''
Created on 26 ott 2018

DataMapper

@author: Giovanni, ...
'''

import logging
import couchdb
from datetime import datetime
from DB_CONNECT import DB_CONNECT

class DM_CDB():
    """ Data mapper verso CouchDB. """
    __server    = None
    __dbName    = None
    __db4Log    = None
    __user      = None
    __pw        = None
    __db        = None
    __dbCon     = None # La connessione è condivisa !
    __db4LogCon = None # La connessione è condivisa !
    __nIstanze  = 0
    
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
            cls.__dbCon = cls.__db4LogCon = None
            logging.info("Connection closed.")
    
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
        
    def __del__(self):
        self.__nIstanze -= 1
        self.__close()
    
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
    
    def getUsername(self, id_utente):
        """ """
        cur = DM_CDB.__cursor()
        username = None
        for item in cur.view('_design/documenti-view/_view/view_id_utente'):
            if item.id == id_utente:
                tmp = item.value
                
        username = tmp['username']
        return username
    
    def getMatricola(self, id_utente):
        """ """
        cur = DM_CDB.__cursor()
        ruolo = 0
        for item in cur.view('_design/documenti-view/_view/view_id_utente'):
            if item.id == id_utente:
                value = item.value
                matricola = value['matricola']
        return matricola 
       
    def getFrequenzaUsername(self, id_utente):
        """ """
        cur = DM_CDB.__cursor()
        frequenza = []
        for item in cur.view('_design/documenti-view/_view/view_id_frequenze'):
            if item.id == id_utente:
                frequenza = item.value
        return frequenza
    
    def getUtentiPunteggi(self):
        """ """
        cur = DM_CDB.__cursor()
        utenti_punteggi  = []
        for item in cur.view('_design/documenti-view/_view/view_id_punteggio'):
            ruolo = item.key
            if ruolo == 2: # utente normale
                utenti_punteggi.append(item.value)
        return utenti_punteggi 
    
    def getSupervisoriPunteggi(self):
        """ """
        cur = DM_CDB.__cursor()
        utenti_punteggi  = []
        for item in cur.view('_design/documenti-view/_view/view_id_punteggio'):
            ruolo = item.key
            if ruolo == 1: # utente normale
                utenti_punteggi.append(item.value)
        return utenti_punteggi 
    
    def updateUserPwd(self, id_utente, password):
        """ """
        ack_pwd = False
        cur = DM_CDB.__cursor()
        doc = cur[str(id_utente)]
        if not ack_pwd:
            doc['pwd'] = password
            cur[doc.id] = doc
            ack_pwd = True
        return ack_pwd
    
    def updateUserMac(self, id_utente, mac):
        """ """
        ack_mac = False
        cur = DM_CDB.__cursor()
        doc = cur[str(id_utente)]
        if not ack_mac:
            doc['macs'][0]['mac'] = mac
            #doc['macs'].append({'mac':mac})
            cur[doc.id] = doc
            ack_mac = True
        return ack_mac
    
    def addUser(self, username, nome, cognome, matricola, mac, pwd):
        """ """
        cur = DM_CDB.__cursor()
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
        ack_user = False
        if not ack_user:
            cur.save(entry)
            ack_user = True
        return ack_user
    
    def deleteUser(self, id):
        """ """
        ack_user = False
        cur = DM_CDB.__cursor()
        doc = cur[str(id)]
        if not ack_user:
            cur.delete(doc)
            ack_user = True
        return ack_user
    
    def getIdMac(self, id_utente):
        """ """
        cur = DM_CDB.__cursor()
        for item in cur.view('_design/documenti-view/_view/view_id_mac'):
            if item.id == id_utente:
                mac = item.value
        return mac
    
    def getProfiloUtente(self, matricola):
        """ """
        cur = DM_CDB.__cursor()
        id = 0
        utente  = []
        for item in cur.view('_design/documenti-view/_view/view_id_utente'):
            value = item.value
            matricola_db = value['matricola']
            if matricola == matricola_db:
                id = item.id
                
        for item in cur.view('_design/documenti-view/_view/view_id_punteggio'):
            if id == item.id:
                utente.append(item.value)
        
        return id, utente
    
    def updateRuolo(self, id_utente, ruolo):
        """ """
        if ruolo == "Supervisore":
            ruolo = 1
        elif ruolo == "Utente":
            ruolo = 2
        ack_ruolo = False
        cur = DM_CDB.__cursor()
        doc = cur[str(id_utente)]
        if not ack_ruolo:
            doc['ruolo'] = ruolo
            cur[doc.id] = doc
            ack_ruolo = True
        return ack_ruolo
    
    def updateUtentiPunteggi(self, id_utente, tempo_totale, punteggio):
        ack_updateUtentiPunteggi = False
        cur = DM_CDB.__cursor()
        doc = cur[str(id_utente)]
        if not ack_updateUtentiPunteggi:
            doc['tempo_totale'] = str(tempo_totale)
            doc['punteggio'] = punteggio
            cur[doc.id] = doc
            ack_updateUtentiPunteggi = True
        return ack_updateUtentiPunteggi