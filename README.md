# Frequency Detection Bluetooth ![CI status](https://img.shields.io/badge/build-passing-brightgreen.svg)

[Frequency Detection Bluetooth](https://github.com/SfideDiProgrammazioneUniVR/PortafoglioVoti/issues/4) è un'applicazione per la rilevazione delle presenze all'interno di un'aula attraverso la connessione bluetooth. Verrà effettuata un'associazione univoca tra l'utente e il codice `UUID` del proprio dispositivo per registrare la presenza una volta connesso all'antenna master del sistema. 

## Indice

* [Progetto](#Progetto)
  * [Web App](#Web-App)
    * [Flask](#Flask)
    * [CouchDb](#CouchDb)
    * [Template Grafico](#Template-Grafico)
    * [Deploy Applicazione Python](#Deploy-Applicazione-Python)
  * [Pairing Bluetooth App](#Pairing-Bluetooth-App)
  * [Documentazione](#Documentazione)
* [Collaborazione](#Collaborazione)
* [Licenza](#Licenza)

## Progetto

Il progetto si basa su una `Web App` e su un applicazione che gestisce la rete `Pairing Bluetooth`. L'admin dopo aver eseguito l'associazione utente:uuid fisicamente alla prima connessione, avvia l'applicazione di rilevazione che si interfaccia con il db. Verrà registrato il timestamp di avvio connessione e quello di fine connessione del dispositivo. La presenza sarà registrata in secondi e su di essa verrà costruita una funzione monotona che determinerà progressivamente il punteggio accumulato.

Attività:

- [x] Analisi dei requisiti
- [ ] Analisi di fattibilità
- [ ] Analisi dell'infrastruttura

Riassumiamo e descriviamo i passi principali per la realizzazione del nostro sistema:

### Web App

Applicazione web per la memorizzazione delle presenze in linguaggio `python3` interpretato a lato server. Costruzione di un web-server attraverso il modulo `Flask` interfacciato al database NoSQL `CouchDb` basato su `JSON`. Il sistema accetta principalmente due tipologie di persone: admin e utente normale. L'admin ha una propria view per controllare l'andamento delle presenze. L'utente è colui che utilizza questo servizio di "timbratura" digitale attraverso il proprio smartphone.

#### Flask

Installazione del modulo attraverso:

`$ pip3 install Flask`

e utilizzo del medesimo nel programma python:

```python
from flask import Flask, session, request, flash
from flask.templating import render_template

if __name__ == '__main__':
    app.run(debug = True)
```

In questo modo possiamo attivare un web-server sul quale fare girare le nostre pagine.

#### CouchDb

Installazione del modulo attraverso:

`$ pip3 install couchdb`

e utilizzo del medesimo nel programma python:

```python
import logging
import couchdb

def __open(cls)
	cls.__db4LogCon = couchdb.Server("http://%s:%s@%s:5984/" % (cls.__user, cls.__pw, cls.__server))
	logging.info("Connection to database " + cls.__dbName + " created.")
```

Essendo un database NoSQL creiamo N documenti per N utenti dove possiamo estrarre informazioni e memorizzare i tempi di entrata e uscita.

#### Template Grafico

Realizzazione di un template dinamico basato su `html5`, `css3` e `javascript`, soprattutto responsive.

#### Deploy Applicazione Python

L'idea è di esportare questa applicazione per farla girare per esempio su un webserver `Apache`.

### Pairing Bluetooth App

...to do

### Documentazione

L'idea è di tenere traccia di tutte le nostre azioni attraverso il sistema di `GitHub`.

## Collaborazione

Per critiche o nuove idee contattare liberamente:	

* giovanni.bellorio@studenti.univr.it (GIOVANNI BELLORIO)
* simone.girardi@studenti.univr.it (SIMONE GIRARDI)

## Licenza
[GNU](https://www.gnu.org/licenses/gpl-3.0.html)