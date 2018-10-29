# Frequency Detection Bluetooth ![CI status](https://img.shields.io/badge/build-passing-brightgreen.svg)

[Frequency Detection Bluetooth](https://github.com/SfideDiProgrammazioneUniVR/PortafoglioVoti/issues/4) è un'applicazione per la rilevazione delle presenze all'interno di un'aula attraverso la connessione bluetooth.

## Indice

* [Progetto](#Progetto)
** [Web App (WA)](#Web-App-(WA))
** [Flask](#Flask)
** [CouchDb](#CouchDb)
** [Template Grafico](#Template-Grafico)
* [Documentazione](#Documentazione)
* [Collaborazione](#Collaborazione)
* [Licenza](#Licenza)

## Progetto

Descriviamo i passi principali per la realizzazione della nostra idea:

### Web App (WA)

Applicazione web per la memorizzazione delle presenze scritta in `python` attraverso il modulo `Flask` interfacciato al database `CouchDb` basato su `JSON`. Ci sono principalmente due tipologie di persone: admin e utente normale. L'admin ha una propria view per controllare l'andamento delle presenze. L'utente è colui che utilizza questo servizio di "timbratura" digitale attraverso il proprio smartphone.

#### Flask

```pyhon
from flask import Flask, session, request, flash
from flask.templating import render_template

if __name__ == '__main__':
    app.run(debug = True)
```

#### CouchDb

```pyhon
import logging
import couchdb

def __open(cls)
	cls.__db4LogCon = couchdb.Server("http://%s:%s@%s:5984/" % (cls.__user, cls.__pw, cls.__server))
	logging.info("Connection to database " + cls.__dbName + " created.")
```

#### Template Grafico

Template basato su `html5`, `css3` e `javascript`.

### Pairing Bluetooth App (PBA)
...

### Documentazione

L'idea è di tenere traccia di tutte le nostre azioni attraverso il sistema di `GitHub`.

## Collaborazione
Per critiche o nuove idee contattare liberamente giovanni.bellorio@studenti.univr.it (GIOVANNI BELLORIO) o simone.girardi@studenti.univr.it (SIMONE GIRARDI).

## Licenza
[GNU](https://www.gnu.org/licenses/gpl-3.0.html)