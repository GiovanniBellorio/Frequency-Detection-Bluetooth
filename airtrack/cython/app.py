#!/usr/bin/python
# -*- coding: utf-8 -*-

'''

+++++++++++++++++++++++++++++++++++++++++++ DataMapper() +++++++++++++++++++++++++++++++++++++++++++

'''
import logging
import couchdb
import datetime
import time

class DM_CDB():
    """ Data mapper verso CouchDB. """
    __server = "localhost"
    #__server = "157.27.134.188"
    __dbName    = 'db_detection'
    __db4Log    = 'admin'
    __user      = 'admin'
    __pw        = 'admin'
    __db        = None
    __dbCon     = None # La connessione è condivisa !
    __db4LogCon = None # La connessione è condivisa !
    __nIstanze  = 0

    @classmethod
    def __open(cls):
        if cls.__dbCon is None:
            try: # readonly
                cls.__dbCon = couchdb.Server("http://%s:5984/" % (cls.__server))
                logging.info("Connection to database " + cls.__dbName + " created.")
            except couchdb.ServerError as err:
                logging.error("Error connecting to CouchDB at %s.\nDetails: %s.", cls.__server, err)
                cls.__dbCon = cls.__db4LogCon
                exit()
            else: # Questo else è del TRY
                try: # read - write
                    cls.__db4LogCon = couchdb.Server("http://%s:%s@%s:5984/" % (cls.__user, cls.__pw, cls.__server))
                    logging.info("Connection to database " + cls.__dbName + " created.")
                except couchdb.ServerError as err:
                    logging.error("Error connecting to couchdb at %s.\nDetails: %s.", cls.__server, err)
                    cls.__dbCon = cls.__db4LogCon
                    exit()
                return "New connection opened."
        return "Connection already opened."

    @classmethod
    def __close(cls):
        if cls.__nIstanze == 0 and cls.__dbCon is not None:
            cls.__dbCon = cls.__db4LogCon = None
            logging.info("Connection closed.")

    @classmethod
    def __cursor(cls):
        """ Ritorna un cursore che restituisce dict invece di tuple per ciascuna riga di una select."""
        if cls.__dbName in cls.__dbCon:
            cls.__db = cls.__dbCon[cls.__dbName]
            return cls.__db

    @classmethod
    def __cursor4log(cls):
        """ Ritorna un cursore per scrivere nel database cls.__db4Log. """
        if cls.__dbName in cls.__db4LogCon:
            cls.__db = cls.__db4LogCon[cls.__dbName]
            return cls.__db

    def __init__(self):
        """ Connessione db """
        DM_CDB.__open()
        DM_CDB.__nIstanze += 1;

    def close(self):
        """ Chiude in modo esplicito la connessione, se non ci sono altre istanze attive """
        self.__del__()
    
    
    def __del__(self):
        self.__nIstanze -= 1;
        self.__close()
        
    def getCountUsernamePassword(self, username, password):
        """ """
        cur = DM_CDB.__cursor()
        num_rows = 0
        id_utente = 0
        for item in cur.view('_design/documenti-view/_view/view_usr_pwd'):
            key = item.key
            username_db = key['username']
            password_db = item.value
            if username == username_db and password == password_db:
                num_rows += 1
                id_utente = item.id
        return num_rows, id_utente

    def getRuoloUsername(self, id_utente):
        """ """
        cur = DM_CDB.__cursor()
        ruolo = 0
        for item in cur.view('_design/documenti-view/_view/view_id_utente'):
            if item.id == id_utente:
                ruolo = item.key
        return ruolo

    def getAllMac(self):
        """ """
        cur = DM_CDB.__cursor()
        mac = []
        for item in cur.view('_design/documenti-view/_view/view_id_mac'):
            mac.append(item.value[0]['mac'])
        return mac

    def update_Records(self, new_record):
        cur = DM_CDB.__cursor()
        for item in cur.view("_design/documenti-view/_view/view_id_mac"):
            mac = item.value[0]['mac']
            if mac == new_record.mac_addr:
                id = item.id
                break

        current_date = datetime.date.today()
        current_date = current_date.strftime("%d-%m-%Y")
        doc = cur[str(id)]
        doc['frequenze'].append({"data": current_date,
                                 "ora_inizio": str(datetime.datetime.fromtimestamp(new_record.first_time).strftime('%H:%M:%S')),
                                 "ora_fine": str(datetime.datetime.fromtimestamp(new_record.last_time).strftime('%H:%M:%S')),
                                 "intervallo": str(datetime.timedelta(seconds=(new_record.last_time - new_record.first_time))),
                                 "incontro": ""})
        cur[doc.id] = doc


'''

+++++++++++++++++++++++++++++++++++++++++++ Model() +++++++++++++++++++++++++++++++++++++++++++

'''
from hashlib import md5
from datetime import date

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

    def getAllMac(self):
        mac = self.dataMapper.getAllMac()
        return mac

    def update_Records(self, new_record):
        self.dataMapper.update_Records(new_record)

    def make_md5(self, s):
        encoding = 'utf-8'
        return md5(s.encode(encoding)).hexdigest()
    
    def __del__(self):
        self.dataMapper.close() # Chiudere sempre il DataMapper


'''

+++++++++++++++++++++++++++++++++++++++++++ AirTrack() +++++++++++++++++++++++++++++++++++++++++++

'''
import platform as platform_OS
import os
import time
import datetime
import argparse
import netaddr
import sys
import logging
import signal
import shlex
from configparser import ConfigParser
from scapy.all import *
from pprint import pprint
from logging.handlers import RotatingFileHandler

class RecordFormSniffing:

    def __init__(self, mac_addr, first_time, last_time, overTreshold):
        self.mac_addr = mac_addr
        self.first_time = first_time
        self.last_time = last_time
        self.overTreshold = overTreshold

    def update(self, new_last_time, overTreshold):
        self.last_time = new_last_time
        if overTreshold:
            self.overTreshold = overTreshold

    # Metodo per aggiornare la data di inizio in caso di lettura da Log
    def debug_update_first(self, new_first_time):
        self.first_time = new_first_time

NAME = 'AirTrack'
DESCRIPTION = 'a command line tool for logging 802.11 probe request frames'
DEBUG = False

mac_list_from_db = []           # list of valid mac address
records_from_sniffing = []      # list of record to write on database
#model = Model()                 # model for database

def build_packet_callback(
    time_fmt,
    logger,
    delimiter,
    mac_info,
    ssid,
    rssi,
    ):

    def packet_callback(packet):

        if not packet.haslayer(Dot11):
            return

        # we are looking for management frames with a probe subtype
        # if neither match we are done here

        if packet.type != 0 or packet.subtype != 0x04:
            return

        # list of output fields

        fields = []

        # determine preferred time format

        log_time = str(int(time.time()))
        if time_fmt == 'iso':
            log_time = datetime.now().isoformat()

        fields.append(log_time)

        # append the mac address itself

        fields.append(packet.addr2)

        # ----------------------------------------------------------------
        # check for a valid mac address

        if packet.addr2 in mac_list_from_db:
            for record in records_from_sniffing:
                if record.mac_addr == packet.addr2:
                    print(("updating mac: " + str(record.mac_addr) + " last_time: " + str(record.last_time)))
                    record.update(int(time.time()), False)
                    print(" --> " + str(record.last_time))
                    break

        # ----------------------------------------------------------------

        # parse mac address and look up the organization from the vendor octets

        if mac_info:
            try:
                parsed_mac = netaddr.EUI(packet.addr2)
                fields.append(parsed_mac.oui.registration().org)
            except netaddr.core.NotRegisteredError as e:
                fields.append('UNKNOWN')

        # include the SSID in the probe frame

        if ssid:
            fields.append(packet.info)

        if rssi:
            rssi_val = -(256 - ord(packet.notdecoded[-0x04:-3]))
            fields.append(str(rssi_val))

        logger.info(delimiter.join(fields))

    return packet_callback


def start_session(args_string):
    print(args_string)

    parser = argparse.ArgumentParser(description=DESCRIPTION, )
    parser.add_argument('-i', '--interface', help='capture interface')
    parser.add_argument('-t', '--time', default='iso', help='output time format (unix, iso)')
    parser.add_argument('-o', '--output', default='airtrack.log', help='logging output location')
    parser.add_argument('-b', '--max-bytes', default=5000000, help='maximum log size in bytes before rotating')
    parser.add_argument('-c', '--max-backups', default=99999, help='maximum number of log files to keep')
    parser.add_argument('-d', '--delimiter', default='\t', help='output field delimiter')
    parser.add_argument('-f', '--mac-info', action='store_true', help='include MAC address manufacturer')
    parser.add_argument('-s', '--ssid', action='store_true', help='include probe SSID in output')
    parser.add_argument('-r', '--rssi', action='store_true', help='include rssi in output')
    parser.add_argument('-D', '--debug', action='store_true', help='enable debug output')
    parser.add_argument('-l', '--log', action='store_true', help='enable scrolling live view of the logfile')
    parser.add_argument('-j', '--input', help='read from log file')

    args = parser.parse_args([args_string])
    args.interface = args.interface.strip()

    if not args.interface:
        print('error: capture interface not given, try --help')
        sys.exit(-1)

    print('---'+args.interface+"---")

    """
    TODO: choose in which mode you want to start Monitor/AP-only
    ...
    ......
    .................

    """

    # database connection
    print("connecting to database...")
    connect_to_db()

    DEBUG = args.debug
    # setup our rotating logger

    logger = logging.getLogger(NAME)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(args.output, maxBytes=args.max_bytes, backupCount=args.max_backups)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    if args.log:
        logger.addHandler(logging.StreamHandler(sys.stdout))
    built_packet_cb = build_packet_callback(
        args.time,
        logger,
        args.delimiter,
        args.mac_info,
        args.ssid,
        args.rssi,
        )

    if args.input:
        print("start sniffing from file... " + args.input)
        sniff_from_file(args.input) # Sniff from log file
    else:
        print("start sniffing...")

        # set monitor mode

        if platform_OS.system() == "Linux":
            os.system("service network-manager stop")
            os.system("ifconfig " + args.interface + " down")
            os.system("iwconfig " + args.interface + " mode Monitor")
            os.system("ifconfig " + args.interface + " up")
            sniff(iface=args.interface, prn=built_packet_cb, store=0) # Wi-Fi sniff
            restore_network(args)
        elif platform_OS.system() == "Darwin":
            sniff(iface=args.interface, prn=built_packet_cb, store=0, monitor=True) # Wi-Fi sniff

    # update database with the new records

    print("updating database...")
    time.sleep(5)
    for record in records_from_sniffing:
        if record.last_time - record.first_time > 0:
            Model().update_Records(record)

    print("done.")


def restore_network(args):
    os.system("ifconfig " + args.interface + " down")
    os.system("iwconfig " + args.interface + " mode Managed")
    os.system("ifconfig " + args.interface + " up")
    os.system("service network-manager start")

def connect_to_db():
    # Sinc db
    username = 'admin'
    password = 'admin'

    encoded_passwd = Model().make_md5(Model().make_md5(password))
    num_rows, id_utente = Model().getCountUsernamePassword(username, encoded_passwd)
    ruolo = Model().getRuoloUsername(id_utente)

    if num_rows == 1 and ruolo != 2:
        global mac_list_from_db
        mac_list_from_db = Model().getAllMac()

        for mac in mac_list_from_db:
            records_from_sniffing.append(RecordFormSniffing(mac, int(time.time()), int(time.time()), False))


    # 1. mi connetto al db --> OK
    # 2. leggo la lista dei mac address iscritti al corso --> OK
    # 3. salvo tale lista in una tabella hash o in una lista --> OK
    # 4. chiudo il db [opzionale] --> OK
    # 5. inizio lo sniffing e confronto ogni pacchetto sniffato con quelli nella lista letta precedentemente --> OK
    # 6. se necessario resetto il contatore relativo al mac appena riscontrato valido entro la treshold --> OK
    # 7. altrimenti alzo un flag indicante il superamento della treshold --> OK
    # 8. al termine dello sniffing sincronizzo il db con i valori di inizio e fine di ogni mac --> OK

# Il log deve essere nel formato '(<UNIX_TIMESTAMP>\t<MAC>\n){1,}'
def sniff_from_file(file):
    with open(file) as log:
        records_from_log = log.readlines()
        records_from_log = [item.split("\t") for item in records_from_log]

        # Modifica di tutti i tempi di inizio con il tempo di inizio del file di Log
        for record in records_from_sniffing:
            record.debug_update_first(int(records_from_log[0][0]))

        # Rimozione di simboli superflui a seguito della lettura del file
        for item in records_from_log:
            item[1] = item[1].strip()

        for mac_from_log in records_from_log: # Scorre tutte le righe del file di Log
            if mac_from_log[1] in mac_list_from_db:
                for record in records_from_sniffing:
                    if record.mac_addr == mac_from_log[1]:
                        print(("updating mac: " + str(record.mac_addr) + " last_time: " + str(record.last_time)))
                        record.update(int(mac_from_log[0]), False) # Aggiorna con il timestamp presente nel file di log
                        print(" --> " + str(record.last_time))
                        break


'''

+++++++++++++++++++++++++++++++++++++++++++ view() +++++++++++++++++++++++++++++++++++++++++++

'''
#from tkinter import Tk, RIGHT, LEFT, TOP, BOTH, RAISED, scrolledtext, StringVar
from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import Frame, Button, Style, Label, OptionMenu
import subprocess
import time
import signal
import os
import psutil

counter = 0

class AirTrackView(Frame):
	
    def __init__(self):
        super().__init__()
		
        self.INTERFACES = []
        self.iface = StringVar(self)
        self.scrollbarLog = None
		
        self.setup()
        self.initUI()

    def setup(self):
        # get interfaces lits
        self.INTERFACES = psutil.net_if_addrs()

    def updateScrolltext(self, txt):
        # http://effbot.org/tkinterbook/text.htm  <-- qui spiega xk bisogna usare questa funzione!
        print("updateScrolltext called..." + txt)
        self.scrollbarLog.config(state = NORMAL)
        self.scrollbarLog.insert(END, txt)
        self.scrollbarLog.see("end")
        self.scrollbarLog.config(state = DISABLED)

    def initUI(self):

        def stop():
            #os.killpg(os.getpgid(self.pid), signal.SIGINT)
            pass

        def start():
            AirTrack.start_session('-i '+self.iface.get())
			# self.updateScrolltext("Inizio rilevazione:\n")
			# def count():
			# 	global counter
			# 	counter += 1 #sostituire counter con una stringa che venga aggiornata con l'output del terminale in questa riga
			# 	self.updateScrolltext(str(counter) + "\n")
			# 	self.after(1000, count)
			# count()

        self.master.title("AirTrack")
		#self.style = Style()
		#self.style.theme_use("default")

        top_label = Label(self, text = "Welcome to AirTrack:")
        top_label.pack(side = TOP, padx = 5, pady = 5, anchor = 'w')

        scrollbarLogFrame = Frame(self, relief = RAISED, borderwidth = 1)
        scrollbarLogFrame.pack(fill = BOTH, expand = True)

        self.pack(fill = BOTH, expand = True)

        self.scrollbarLog = scrolledtext.ScrolledText(scrollbarLogFrame, background = "black", foreground = "green")#, state=DISABLED)
        self.scrollbarLog.pack(fill = BOTH, expand = True, padx = 5, pady = 5)

        startButton = Button(self, text = "Start", command = start) #inserire command
        startButton.pack(side = RIGHT, padx = 5, pady = 5)
        stopButton = Button(self, state=DISABLED, text = "Stop", command = stop) #inserire command
        stopButton.pack(side = RIGHT)

        interface_label = Label(self, text = "Interface:")
        interface_label.pack(side = LEFT, padx = 5, pady = 5)

        interfaces_list = OptionMenu(self, self.iface, next(iter(self.INTERFACES)), *self.INTERFACES)
        interfaces_list.pack(side = LEFT)

        self.updateScrolltext("Select network interface and press Start.\n")


def main():
    root = Tk()
    root.geometry("800x500")
    app = AirTrackView()
    root.mainloop()

if __name__ == '__main__':
    main()