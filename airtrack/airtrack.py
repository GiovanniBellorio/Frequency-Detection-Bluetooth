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
from scapy.all import *
from pprint import pprint
from logging.handlers import RotatingFileHandler
from Model import Model

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


NAME = 'AirTack'
DESCRIPTION = 'a command line tool for logging 802.11 probe request frames'
DEBUG = False

mac_list_from_db = []           # list of valid mac address
records_from_sniffing = []      # list of record to write on database
model = Model()                 # model for database

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
                    print(("updating mac: " + str(record.mac_addr) + " last_time: " + str(record.last_time)), end="")
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


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
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
    args = parser.parse_args()

    if not args.interface:
        print('error: capture interface not given, try --help')
        sys.exit(-1)

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
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(args.output, maxBytes=args.max_bytes, backupCount=args.max_backups)
    logger.addHandler(handler)
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

    # set monitor mode
    print("setting monitor mode...")
    if platform_OS.system() == "Linux":
        os.system("service network-manager stop")
        os.system("ifconfig " + args.interface + " down")
        os.system("iwconfig " + args.interface + " mode Monitor")
        os.system("ifconfig " + args.interface + " up")

        print("start sniffing...")
        sniff(iface=args.interface, prn=built_packet_cb, store=0)

        restore_network(args)
    elif platform_OS.system() == "Darwin":
        print("start sniffing...")
        sniff(iface=args.interface, prn=built_packet_cb, store=0, monitor=True)


    # update database with the new records

    print("updating database...")
    time.sleep(5)
    for record in records_from_sniffing:
        if record.last_time - record.first_time > 0:
            model.update_Records(record)

    print("end.")


def restore_network(args):
    os.system("ifconfig " + args.interface + " down")
    os.system("iwconfig " + args.interface + " mode Managed")
    os.system("ifconfig " + args.interface + " up")
    os.system("service network-manager start")

def connect_to_db():
    # Sinc db
    username = 'admin'
    password = 'admin'

    encoded_passwd = model.make_md5(model.make_md5(password))
    num_rows, id_utente = model.getCountUsernamePassword(username, encoded_passwd)
    ruolo = model.getRuoloUsername(id_utente)

    if num_rows == 1 and ruolo != 2:
        global mac_list_from_db
        mac_list_from_db = model.getAllMac()

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



if __name__ == '__main__':
    main()
