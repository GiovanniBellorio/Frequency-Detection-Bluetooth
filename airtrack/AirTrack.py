#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import urllib.request  # for internet connection
from configparser import ConfigParser
from scapy.all import *
from threading import Thread, Event
from pprint import pprint
from logging.handlers import RotatingFileHandler
from Model import Model

NAME = 'AirTrack'
DESCRIPTION = 'a command line tool for logging 802.11 probe request and QoS data frames'
DEBUG = False

mac_list_from_db = []           # list of valid mac address
records_from_sniffing = []      # list of record to write on database
db_is_connected = False


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



class Sniffer(Thread):
    def  __init__(self, args_string):
        super().__init__()

        self.daemon = True
        self.socket = None
        self.stop_sniffer = Event()
        self.presences = set()

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

        self.args = parser.parse_args([args_string])
        self.args.interface = self.args.interface.strip()

        if not self.args.interface:
            print('error: capture interface not given, try --help')
            sys.exit(-1)

        DEBUG = self.args.debug
        # setup our rotating logger

        logger = logging.getLogger(NAME)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = RotatingFileHandler(self.args.output, maxBytes=self.args.max_bytes, backupCount=self.args.max_backups)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.propagate = False

        if self.args.log:
            logger.addHandler(logging.StreamHandler(sys.stdout))

        self.built_packet_cb = self.build_packet_callback(self.args.time, logger, self.args.delimiter, self.args.mac_info, self.args.ssid, self.args.rssi)



    def run(self):
        self.socket = conf.L2listen(type=ETH_P_ALL,iface=self.args.interface,filter="ip")

        #sniff(opened_socket=self.socket,prn=self.print_packet,stop_filter=self.should_stop_sniffer)
        if platform_OS.system() == "Linux":
            os.system("service network-manager stop")
            os.system("ifconfig " + self.args.interface + " down")
            os.system("iwconfig " + self.args.interface + " mode Monitor")
            os.system("ifconfig " + self.args.interface + " up")
            sniff(iface=self.args.interface, prn=self.built_packet_cb, store=0, stop_filter=self.should_stop_sniffer) # Wi-Fi sniff
            self.restore_network(self.args)
        elif platform_OS.system() == "Darwin":
            print("sniffing from osx")
            sniff(iface=self.args.interface, prn=self.built_packet_cb, store=0, stop_filter=self.should_stop_sniffer, monitor=True) # Wi-Fi sniff
            print("after sniffing from osx")


    def join(self, timeout=None):
        self.stop_sniffer.set()
        super().join(timeout)

    def should_stop_sniffer(self, packet):
        return self.stop_sniffer.isSet()

    def print_packet(self, packet):
        ip_layer = packet.getlayer(IP)
        print("[!] New Packet: {src} -> {dst}".format(src=ip_layer.src, dst=ip_layer.dst))

    def restore_network(self, args):
        os.system("ifconfig " + args.interface + " down")
        os.system("iwconfig " + args.interface + " mode Managed")
        os.system("ifconfig " + args.interface + " up")
        os.system("service network-manager stop")
        os.system("service network-manager start")

    def getCurrentPresences(arg):
        return self.presences


    def build_packet_callback(self, time_fmt,logger,delimiter,mac_info,ssid,rssi):

        def packet_callback(packet):

            if not packet.haslayer(Dot11):  # <--- necessaria la versione 2.4.0 di scapy (aggiornare il codice)
                return

            # we are looking for management frames with a probe subtype or for QoS
            # if neither match we are done here

            if packet.type != 0 or packet.subtype != 0x04:
                if packet.type != 0x02:
                    return

            # list of output fields

            fields = []

            # determine preferred time format

            log_time = str(int(time.time()))
            if time_fmt == 'iso':
                log_time = datetime.now().isoformat()

            # ----------------------------------------------------------------
            # check for a valid mac address for the course

            if packet.addr2 in mac_list_from_db:
                fields.append(log_time)                                         # append the log time
                fields.append(packet.addr2)                                     # append the mac address itself
                self.presences.add(packet.addr2)
                for record in records_from_sniffing:
                    if record.mac_addr == packet.addr2:
                        #print(("updating mac: " + str(record.mac_addr) + " last_time: " + str(record.last_time)), end="")
                        record.update(int(time.time()), False)
                        #print(" --> " + str(record.last_time))
                        break

            # ----------------------------------------------------------------

            # parse mac address and look up the organization from the vendor octets

            # if mac_info:
            #     try:
            #         parsed_mac = netaddr.EUI(packet.addr2)
            #         fields.append(parsed_mac.oui.registration().org)
            #     except netaddr.core.NotRegisteredError as e:
            #         fields.append('UNKNOWN')
            #
            # # include the SSID in the probe frame
            #
            # if ssid:
            #     fields.append(packet.info)
            #
            # if rssi:
            #     rssi_val = -(256 - ord(packet.notdecoded[-0x04:-3]))
            #     fields.append(str(rssi_val))

            logger.info(delimiter.join(fields))

        return packet_callback



def connect_to_db(username, password):
    print("connecting to database...")
    # Sinc db

    wait_for_internet_connection()

    encoded_passwd = Model().make_md5(Model().make_md5(password))
    num_rows, id_utente = Model().getCountUsernamePassword(username, encoded_passwd)
    ruolo = Model().getRuoloUsername(id_utente)

    global db_is_connected
    db_is_connected = True

    if num_rows == 1 and ruolo != 2:
        global mac_list_from_db
        global records_from_sniffing
        mac_list_from_db = Model().getAllMac()

        for mac in mac_list_from_db:
            records_from_sniffing.append(RecordFormSniffing(mac, int(time.time()), int(time.time()), False))

    else:
        print('Login error')
        return -1


def update_db():
    print("updating database...")

    wait_for_internet_connection()

    for record in records_from_sniffing:
        if record.last_time - record.first_time > 0:
            Model().update_Records(record)

    print("done.")


def wait_for_internet_connection():
    while True:
        try:
            response = urllib.request.urlopen('http://www.google.com', timeout=1)
            return
        except urllib.error.URLError:
            print("waiting for internet connection...")
            pass





#
# print('---'+args.interface+"---")
#
# """
# TODO: choose in which mode you want to start Monitor/AP-only
# ...
# ......
# .................
#
# """
#
#
#
#
#
# if args.input:
#     print("start sniffing from file... " + args.input)
#     sniff_from_file(args.input) # Sniff from log file
# else:
#     print("start sniffing...")
#
#     # set monitor mode
#
#
#
#     # 1. mi connetto al db --> OK
#     # 2. leggo la lista dei mac address iscritti al corso --> OK
#     # 3. salvo tale lista in una tabella hash o in una lista --> OK
#     # 4. chiudo il db [opzionale] --> OK
#     # 5. inizio lo sniffing e confronto ogni pacchetto sniffato con quelli nella lista letta precedentemente --> OK
#     # 6. se necessario resetto il contatore relativo al mac appena riscontrato valido entro la treshold --> OK
#     # 7. altrimenti alzo un flag indicante il superamento della treshold --> OK
#     # 8. al termine dello sniffing sincronizzo il db con i valori di inizio e fine di ogni mac --> OK
#
# # Il log deve essere nel formato '(<UNIX_TIMESTAMP>\t<MAC>\n){1,}'
# def sniff_from_file(file):
#     with open(file) as log:
#         records_from_log = log.readlines()
#         records_from_log = [item.split("\t") for item in records_from_log]
#
#         # Modifica di tutti i tempi di inizio con il tempo di inizio del file di Log
#         for record in records_from_sniffing:
#             record.debug_update_first(int(records_from_log[0][0]))
#
#         # Rimozione di simboli superflui a seguito della lettura del file
#         for item in records_from_log:
#             item[1] = item[1].strip()
#
#         for mac_from_log in records_from_log: # Scorre tutte le righe del file di Log
#             if mac_from_log[1] in mac_list_from_db:
#                 for record in records_from_sniffing:
#                     if record.mac_addr == mac_from_log[1]:
#                         print(("updating mac: " + str(record.mac_addr) + " last_time: " + str(record.last_time)), end="")
#                         record.update(int(mac_from_log[0]), False) # Aggiorna con il timestamp presente nel file di log
#                         print(" --> " + str(record.last_time))
#                         break

# if __name__ == '__main__':
#     main()
