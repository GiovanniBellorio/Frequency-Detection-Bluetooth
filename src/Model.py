#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Created on 26 ott 2018

Model.
Questo Model mantiene anche un log delle chiamate ai metodi.
La separazione con il database è forzata.

@author: Giovanni, ...
'''

from hashlib import md5, sha256
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
    
    def getUsername(self, id_utente):
        username = self.dataMapper.getUsername(id_utente)
        return username
    
    def getIdMac(self, id_utente):
        mac = self.dataMapper.getIdMac(id_utente)
        return mac
    
    def getMatricola(self, id_utente):
        matricola = self.dataMapper.getMatricola(id_utente)
        return matricola
    
    def getFrequenzaUsername(self, id_utente):
        frequenza = self.dataMapper.getFrequenzaUsername(id_utente)
        return frequenza
    
    def getUtentiPunteggi(self):
        utenti_punteggi = self.dataMapper.getUtentiPunteggi()
        return utenti_punteggi
    
    def getUtentiPerData(self, data):
        utenti_per_data = self.dataMapper.getUtentiPerData(data)
        return utenti_per_data
    
    def updateUtentiPunteggi(self, id_utente, tempo_totale, punteggio):
        ack_updateUtentiPunteggi = self.dataMapper.updateUtentiPunteggi(id_utente, tempo_totale, punteggio)
        return ack_updateUtentiPunteggi
    
    def getSupervisoriPunteggi(self):
        supervisori_punteggi = self.dataMapper.getSupervisoriPunteggi()
        return supervisori_punteggi
    
    def updateUserPwd(self, id_utente, password):
        ack_pwd = self.dataMapper.updateUserPwd(id_utente, password)
        return ack_pwd
    
    def updateUserMac(self, id_utente, mac):
        ack_mac = self.dataMapper.updateUserMac(id_utente, mac)
        return ack_mac
    
    def make_md5(self, s):
        encoding = 'utf-8'
        return md5(s.encode(encoding)).hexdigest()
    
    def make_sha256(self, s):
        encoding = 'utf-8'
        return sha256(s.encode(encoding)).hexdigest()
    
    def getProfiloUtente(self, matricola):
        id, utente = self.dataMapper.getProfiloUtente(matricola)
        return id, utente
    
    def updateRuolo(self, id_utente, ruolo):
        ack_ruolo = self.dataMapper.updateRuolo(id_utente, ruolo)
        return ack_ruolo
    
    def addUser(self, username, nome, cognome, matricola, mac, pwd):
        ack_user = self.dataMapper.addUser(username, nome, cognome, matricola, mac, pwd)
        return ack_user
    
    def deleteUser(self, id):
        ack_user = self.dataMapper.deleteUser(id)
        return ack_user
    
    def aggiungi_presenza(self, id, data):
        ack_aggiungi_presenza = self.dataMapper.aggiungi_presenza(id, data)
        return ack_aggiungi_presenza
    
    def elimina_presenza(self, id, idx_presenza):
        ack_elimina_presenza = self.dataMapper.elimina_presenza(id, idx_presenza)
        return ack_elimina_presenza
    
    def __del__(self):
        self.dataMapper.close() # Chiudere sempre il DataMapper
