# Installazione CouchDB per Ubuntu

1. Aprire una shell

2. Lanciare il comando

	`$ echo "deb https://apache.bintray.com/couchdb-deb {distribution} main" \
    		| sudo tee -a /etc/apt/sources.list`
    
	dove `{distribution}` viene scelto in base alla propria versione di Ubuntu:

		* Debian 8: jessie
		* Debian 9: stretch
		* Ubuntu 14.04: trusty
		* Ubuntu 16.04: xenial
		* Ubuntu 18.04: bionic
		
		
3. Aggiornare la cache dei repository e installare il package:

	` $ sudo apt-get update && sudo apt-get install couchdb`
	
4. Seguire gli step del Setup Wizard che apparirà successivamente (da specificare)

5. Per far funzionare CoucDB bisogna creare un apposito utente di sistema, chiamato `coucdb`.

	Eseguire i seguenti comandi

	` $ adduser --system \
            --shell /bin/bash \
            --group --gecos \
            "CouchDB Administrator" couchdb `


6. Per controllare che l'installazione sia andata a buon fine:

	* aprire un browser
	* indirizzare a http://127.0.0.1:5984/_utils/index.html
	* loggarsi con Username = "admin" e Password la password scelta in fase di installazione nel Setup Wizard
	* creare un nuovo database (nome: db_detection)
	

Dopo la prima installazione il servizio CouchDB risulta già avviato.

In generale, per avviare il servizio lanciare il comando
`$ service couchdb start`

Analogamente, per arrestare il servizio digitare
`$ service couchdb stop`
	
Nel momento in cui non fosse più necessario l'utilizzo del servizio CouchDB, è consigliabile arrestarlo, perchè altrimenti risulta sempre attivo all'interno della propria macchina.


# Restore del database

Per eseguire il Restore del database: 

`$ bash couchdb-backup.sh -r -H 127.0.0.1 -d db_detection -f dumpedDB.json -u <nome_utente> -p <password>`

dove `<nome_utente>` è "admin" e `<password>` è la password scelta in fase di installazione nel Setup Wizard.


# Backup del database

Per eseguire il Backup del database:

`$ bash couchdb-backup.sh -b -H 127.0.0.1 -d db_detection -f dumpedDB.json -u <nome_utente> -p <password>` 

dove `<nome_utente>` è "admin" e `<password>` è la password scelta in fase di installazione nel Setup Wizard.

# Backup e Restore automatici

Per facilitare le operazioni di backup e restore del database, è stato creato lo script python **[script_backup_restore.py](https://github.com/GiovanniBellorio/Frequency-Detection-Wireless/blob/dev/dumpedDb/script_backup_restore.py)**

Si  possono utilizzare quindi i seguenti comandi:

```python3 script_backup_restore.py r``` per eseguire il restore del databse.

```python3 script_backup_restore.py b``` per eseguire il backup del databse.




# Organizzazione della struttura del database

Il database a supporto dell'applicazione Frequency-Detection-Wireless è una base di dati NoSQL, che utilizza il formato json.

La struttura del databse è la seguente:

* **id**: identificativo univoco dell'utente registrato nell'applicazione. Di tipo stringa.
* **utente**: sruttura che memorizza i dati personali dell'utente registrato, quali:
	* username
	* nome
	* cognome
	* matricola
* **pwd**: stringa alfanumerica che memorizza il doppio hash MD5 della password.
* **ruolo**: valore intero che può assumere i seguenti valori, in base ai privilegi dell'utente registrato:
	* 0: indica che l'utente è un _admin_.
	* 1: indica che l'utente è un _supervisore_.
	* 2: indica che l'utente è un _normale utilizzatore_.
* **macs**: lista dei vari indirizzi MAC del dispositivo con cui un utente utilizza l'applicazione.
* **incontri**: lista di elementi strutturati che descrivono un _incontro_.
		Ogni _incontro_ è descritto dai seguenti campi:
	* id: stringa identificativa univocoa per ogni incontro.
	* descrizione: campo che descrive il tipo di incontro.
	* data: la data in cui si svolge un certo incontro.
	* ora_inizio: l'ora in cui inizia l'incontro.
	* ora_fine: l'ora in cui termina l'incontro.
	* stato: descrive se l'incontro è già stato svolto o deve svolgersi (_CHIUSO_) oppure se l'evento è attualmente in corso (_APERTO_).
* **frequenze**: lista di elementi strutturati che descrivono una _frequenza_ (partecipazione) ad un determinato incontro.
		Ogni _frequenza_ è descritta dai seguenti campi:
	* data: la data di partecipazione.
	* ora_inizio: l'ora in cui l'utente prende parte all'incontro.
	* ora_fine: l'ora in cui l'utente termina l'incontro, cioè abbandona la partecipazione.
	* intervallo: valore intero espresso in secondi; indica il tempo totale di partecipazione a quel dato incontro.
	* incontro: valore che identifica l'incontro a cui l'utente ha partecipato; è l'id dell'incontro.
* **tempo_totale**: valore intero espresso in secondi; indica il tempo totale di partecipazione a tutti gli incontri.
* **punteggio**: valore intero che esprime il punteggio accumulato dall'utente; valore attribuito e incrementato secondo le scelte dell _admin_.
		


