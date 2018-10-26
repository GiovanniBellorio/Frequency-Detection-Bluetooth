'''
Created on 26 ott 2018

DataMapper

@author: Giovanni
'''

from datetime import datetime
import logging
import psycopg2.extras

class DM_PG():
    """ Data mapper verso PostgreSQL. Per semplicità, i parametri di connessione sono attributi di classe: dovrebbero essere
        scritti in un file esterno e caricati durante __init__. """
    __server = "dbserver.scienze.univr.it"
    __db = "did2014"
    __db4Log = 'id367xdk'
    __user = 'id367xdk'
    __pw = 'Bacibaci.1995'
    __dbCon = None # La connessione è condivisa !
    __db4LogCon = None # La connessione è condivisa !
    __nIstanze = 0
    
    @classmethod
    def __open(cls):
        if cls.__dbCon is None:
            try:
                cls.__dbCon = psycopg2.connect(host=cls.__server, database=cls.__db, user=cls.__user, password=cls.__pw)
                cls.__dbCon.set_session(readonly=True, autocommit=True) # Connessione di lettura condivisa
                logging.info("Connection to database " + cls.__db + " created.")
            except psycopg2.OperationalError as err:
                logging.error("Error connecting to PostgreSQL DBMS at %s.\nDetails: %s.", cls.__server, err)
                cls.__dbCon = cls.__db4LogCon = None
                exit()
            else: # Questo else è del TRY
                try:
                    cls.__db4LogCon = psycopg2.connect(host=cls.__server, database=cls.__db4Log, user=cls.__user, password=cls.__pw)
                    cls.__db4LogCon.set_session(autocommit=True) # Connessione di scrittura condivisa
                    logging.info("Connection to database " + cls.__db4Log + " created.")
                except psycopg2.OperationalError as err:
                    logging.error("Error connecting to PostgreSQL DBMS at %s.\nDetails: %s.", cls.__server, err)
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
        return cls.__dbCon.cursor(cursor_factory = psycopg2.extras.DictCursor)

    @classmethod
    def __cursor4log(cls):
        """ Ritorna un cursore per scrivere nel database cls.__db4Log. """
        return cls.__db4LogCon.cursor()

    
    def __init__(self):
        DM_PG.__open()
        DM_PG.__nIstanze += 1

    def close(self):
        """ Chiude in modo esplicito la connessione, se non ci sono altre istanze attive """
        self.__del__()

    def __del__(self):
        DM_PG.__nIstanze -= 1
        DM_PG.__close()

    def getFacolta(self, name):
        """ Ritorna il dict {id,nome,url,dataCreazione} della facoltà di nome "name" se esite, None altrimenti. """
        with DM_PG.__cursor() as cur:
            cur.execute("SELECT id,nome,url,datacreazione \
                         FROM Facolta \
                         WHERE nome ILIKE %s", (name,))
            facolta = cur.fetchone()
            return facolta

    def getCorsoStudiFacolta(self, idF):
        """ Ritorna una list di dict {id,nome,codice,durataAnni} di tutti i corsi di studi associati alla facoltà con id 'idF' """
        with DM_PG.__cursor() as cur:
            cur.execute('SELECT cs.id, cs.nome, cs.codice, cs.durataanni as "durataAnni" \
                         FROM corsostudi cs JOIN corsoinfacolta csf ON cs.id = csf.id_corsostudi \
                         WHERE csf.id_facolta = %s \
                         ORDER BY cs.nome', (int(idF),))
            return list(cur)

    def getAnniAccademiciFacolta(self, idF):
        """ Ritorna una list di stringhe rappresentanti gli anni accademici di tutti i corsi di studi associati alla facoltà con id 'idF' """
        with type(self).__cursor() as cur:
            cur.execute('SELECT DISTINCT ie.annoaccademico \
                         FROM inserogato ie JOIN corsostudi cs ON ie.id_corsostudi = cs.id \
                                            JOIN corsoinfacolta csf ON cs.id = csf.id_corsostudi \
                         WHERE csf.id_facolta = %s \
                         ORDER BY ie.annoaccademico DESC', (int(idF),))
            lista = list()
            for tupla in cur:
                lista.append(tupla[0])
            return lista

    def getCorsoStudi(self, idCS):
        """ Ritorna dict {idCS,nome,codice,durataAnni,annoaccademico,stato} del corso di studi 'idCS' """
        with type(self).__cursor() as cur:
            cur.execute('SELECT cs.id, cs.nome, cs.codice, cs.durataanni as "durataAnni", scs.annoaccademico as "annoAccademicoUltimoStato", st.valore as "ultimoStato" \
                         FROM corsostudi cs JOIN statodics scs ON cs.id = scs.id0_corsostudi \
                                            JOIN statocs st ON scs.id1_statocs = st.id \
                         WHERE cs.id = %s \
                         ORDER BY annoaccademico desc', (int(idCS),))
            return cur.fetchone()

    def getInsEroConDoc(self, idCS, annoA):
        """ Ritorna una list di dict {id,nome,discr,hamoduli,modulo,nomeModulo,discriminanteModulo,crediti,docente} di tutti gli insegnamenti \
            erogati del corso di studi 'idCS' nell'anno accademico 'annoA' """
        with type(self).__cursor() as cur:
            cur.execute("SELECT DISTINCT ie.id, i.nomeins as nome, d.nome as discr, ie.hamoduli, abs(ie.modulo) as modulo, \
                                ie.nomemodulo as "'nomeModulo'", ie.discriminantemodulo as "'discriminanteModulo'", haunita, \
                                nomeunita as "'nomeUnita'", ie.crediti, p.nome || ' ' || p.cognome as docente \
                         FROM inserogato ie JOIN insegn i ON ie.id_insegn = i.id \
                                            JOIN corsostudi cs ON ie.id_corsostudi = cs.id \
                                            LEFT JOIN discriminante d ON ie.id_discriminante = d.id \
                                            LEFT JOIN docenza doc ON doc.id_inserogato = ie.id \
                                            JOIN persona p ON doc.id_persona = p.id \
                         WHERE cs.id = %s AND ie.annoaccademico = %s \
                         ORDER BY i.nomeins, modulo", (int(idCS), annoA))
            return list (cur)
        
    def log(self, idModel:str, instant:datetime, methodName:str):
        """ Scrive il log sulla tabella InsegnamentiLog che deve essere presente nel database cls.__database4Log.
            CREATE TABLE INSEGNAMENTILOG(id SERIAL PRIMARY KEY,idModeApp VARCHAR NOT NULL,instant TIMESTAMP NOT NULL,methodName VARCHAR NOT NULL) """
        if idModel is None or methodName is None or instant is None:
            return
        with DM_PG.__cursor4log() as cur:
            cur.execute("INSERT INTO InsegnamentiLog(idModeApp,instant,methodName) VALUES (%s,%s,%s)", (idModel, instant, methodName))
            if cur.rowcount != 1:
                logging.error("Log has not been written. Details: " + idModel + ", " + str(instant) + "," + methodName)
                return False
            return True