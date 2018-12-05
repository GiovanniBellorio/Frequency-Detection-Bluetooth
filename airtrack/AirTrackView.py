#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
			os.killpg(os.getpgid(proc.pid), signal.SIGINT)


		def start():
			self.updateScrolltext("Interface selected is: " +  self.iface.get() + "\n")
			cmd = 'sudo python3 AirTrack.py -i ' + self.iface.get() + ' -t LINUX'
			#global proc
			proc = subprocess.Popen(cmd, shell=True)
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
		stopButton = Button(self, text = "Stop", command = stop) #inserire command
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
