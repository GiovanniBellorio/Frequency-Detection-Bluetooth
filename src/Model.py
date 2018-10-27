'''
Created on 26 ott 2018

Semplice Model.
Questo Model mantiene anche un log delle chiamate ai metodi.
La separazione con il database è forzata.

@author: Giovanni
'''

from datetime import date
from DM_CDB import DM_CDB

class Model(object):
    """ Realizza il modello dei dati da pubblicare. """
    
    def __init__(self):
        self.id = "Model_" + date.today().isoformat()
        self.dataMapper = DM_CDB() # DataMapper verso CouchDB
        
        
        
    
    
    def __del__(self):
        self.dataMapper.close() # Chiudere sempre il DataMapper