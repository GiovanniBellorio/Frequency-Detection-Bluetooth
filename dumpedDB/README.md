# Installazione couchDB per Ubuntu

1. Aprire una schell

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

5. Per controllare che l'installazione sia andata a buon fine:

	* aprire un browser
	* indirizzare a http://127.0.0.1:5984/_utils/index.html
	* loggarsi con Username = "admin" e Password la password scelta in fase di installazione nel Setup Wizard


# Restore del database

Per eseguire il Restore del database: 

`$ bash couchdb-backup.sh -r -H 127.0.0.1 -d db_detection -f dumpedDB.json -u <nome_utente> -p <password>`

dove `<nome_utente>` è "admin" e `<password>` è la password scelta in fase di installazione nel Setup Wizard.




    	
    
    


brew install gnu-sed

BACKUP:
bash couchdb-backup.sh -b -H 127.0.0.1 -d db_detection -f dumpedDB.json -u admin -p admin

RESTORE:
bash couchdb-backup.sh -r -H 127.0.0.1 -d db_detection -f dumpedDB.json -u admin -p admin
