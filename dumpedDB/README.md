# Installazione Ubuntu

1. Aprire una schell

2. Lanciare il comando

	'$ echo "deb https://apache.bintray.com/couchdb-deb {distribution} main" \
    		| sudo tee -a /etc/apt/sources.list'
    
	dove '$ {distribution}' viene scelto in base alla propria versione di Ubuntu:

		* Debian 8: jessie
		* Debian 9: stretch
		* Ubuntu 14.04: trusty
		* Ubuntu 16.04: xenial
		* Ubuntu 18.04: bionic
    	
    
    


brew install gnu-sed

BACKUP:
bash couchdb-backup.sh -b -H 127.0.0.1 -d db_detection -f dumpedDB.json -u admin -p admin

RESTORE:
bash couchdb-backup.sh -r -H 127.0.0.1 -d db_detection -f dumpedDB.json -u admin -p admin
