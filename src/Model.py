'''
Created on 26 ott 2018

Model.
Questo Model mantiene anche un log delle chiamate ai metodi.
La separazione con il database è forzata.

@author: Giovanni, ...
'''

from datetime import date
from DM_CDB import DM_CDB

class Model(object):
    """ Realizza il modello dei dati da pubblicare. """
    
    def __init__(self):
        self.id = "Model_" + date.today().isoformat()
        self.dataMapper = DM_CDB() # DataMapper verso CouchDB
        
    def getCountUsernamePassword(self, username, password):
        num_rows, id_utente = self.dataMapper.getCountUsernamePassword(username, password)
        return num_rows, id_utente
    
    def getRuoloUsername(self, id_utente):
        ruolo = self.dataMapper.getRuoloUsername(id_utente)
        return ruolo
    
    def getFrequenzaUsername(self, id_utente):
        frequenza = self.dataMapper.getFrequenzaUsername(id_utente)
        return frequenza
    
    def getUtentiPunteggi(self):
        utenti_punteggi = self.dataMapper.getUtentiPunteggi()
        return utenti_punteggi
        
    def __del__(self):
        self.dataMapper.close() # Chiudere sempre il DataMapper