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

counter = 0

class Interface(Frame):

	def __init__(self):
		super().__init__()

		self.INTERFACES = []
		self.iface = StringVar(self)

		self.setup()
		self.initUI()


	def setup(self):
        # TODO: self.INTERFACES = get interfaces_list()
        # .....
        # .........

		self.INTERFACES = ["1", "2", "3"]
		self.iface.set(self.INTERFACES[0]) # default value

	def updateScrolltext(self, sc, txt):
		# http://effbot.org/tkinterbook/text.htm  <-- qui spiega xk bsiogna usare questa funzione!
		sc.config(state = NORMAL)
		sc.insert(END, txt)
		sc.see("end")
		sc.config(state = DISABLED)

	def initUI(self):

		def stop():
			os.killpg(os.getpgid(proc.pid), signal.SIGINT)


		def start():
			cmd = 'sudo python3 airtrack.py -i wlp3s0 -t LINUX'
			global proc
			proc = subprocess.Popen(cmd, shell=True)
			# self.updateScrolltext(scrollbarLog, "Inizio rilevazione:\n")
			# def count():
			# 	global counter
			# 	counter += 1 #sostituire counter con una stringa che venga aggiornata con l'output del terminale in questa riga
			# 	self.updateScrolltext(scrollbarLog, str(counter) + "\n")
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

		scrollbarLog = scrolledtext.ScrolledText(scrollbarLogFrame, background = "black", foreground = "green")#, state=DISABLED)
		scrollbarLog.pack(fill = BOTH, expand = True, padx = 5, pady = 5)

		startButton = Button(self, text = "Start", command = start) #inserire command
		startButton.pack(side = RIGHT, padx = 5, pady = 5)
		stopButton = Button(self, text = "Stop", command = stop) #inserire command
		stopButton.pack(side = RIGHT)

		interface_label = Label(self, text = "Interface:")
		interface_label.pack(side = LEFT, padx = 5, pady = 5)

		interfaces_list = OptionMenu(self, self.iface, *self.INTERFACES)
		interfaces_list.pack(side = LEFT)

		self.updateScrolltext(scrollbarLog, "Select network interface and press Start.\n")


def main():

	root = Tk()
	root.geometry("800x500")
	app = Interface()
	root.mainloop()


if __name__ == '__main__':
	main()
