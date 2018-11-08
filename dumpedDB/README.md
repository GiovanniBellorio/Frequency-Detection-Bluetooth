brew install gnu-sed

BACKUP:
bash couchdb-backup.sh -b -H 127.0.0.1 -d db_detection -f dumpedDB.json -u admin -p admin

RESTORE:
bash couchdb-backup.sh -r -H 127.0.0.1 -d db_detection -f dumpedDB.json -u admin -p admin