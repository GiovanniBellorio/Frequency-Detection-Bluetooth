#!/usr/bin/python3
# -*- coding: utf-8 -*-

# from tkinter import Tk, RIGHT, LEFT, TOP, BOTH, RAISED, scrolledtext, StringVar
from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import Frame, Button, Style, Label, OptionMenu
import subprocess
import time
import signal
import os
import psutil
import AirTrack
from time import sleep

counter = 0

class AirTrackView(Frame):

	def __init__(self):
		super().__init__()

		self.INTERFACES = []
		self.iface = StringVar(self)
		self.scrollbarLog = None
		self.sniffer = None

		self.setup()
		self.initUI()


	def setup(self):
		# get interfaces lits
		self.INTERFACES = psutil.net_if_addrs()


	def updateScrolltext(self, txt):
		# http://effbot.org/tkinterbook/text.htm  <-- qui spiega xk bisogna usare questa funzione!
		print(txt)
		self.scrollbarLog.config(state = NORMAL)
		self.scrollbarLog.insert(END, txt)
		self.scrollbarLog.see("end")
		self.scrollbarLog.config(state = DISABLED)

	def cleanScrollText(self):
		self.scrollbarLog.config(state = NORMAL)
		self.scrollbarLog.delete(END)
		self.scrollbarLog.config(state = DISABLED)

	def initUI(self):

		def stop():
			#os.killpg(os.getpgid(self.pid), signal.SIGINT)
			print("[*] Stop sniffing")
			self.sniffer.join(2.0)

			if self.sniffer.isAlive():
				self.sniffer.socket.close()

			# update database with the new records
			AirTrack.update_db()


		def start():
			self.sniffer = AirTrack.Sniffer('-i '+self.iface.get())
			self.sniffer.start()
			#AirTrack.start_session('-i '+self.iface.get())
			self.cleanScrollText()
			self.updateScrolltext("Inizio rilevazione:\n")
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



def login_gui():
	data = []

	login = Tk()
	login.geometry("300x100")
	login.title("Login")

	chkValue = BooleanVar()
	chkValue.set(False)

	try:
		with open ("data", "r") as file:
			data=file.readlines()
	except:
		pass

	def login_fun(event=None):
		AirTrack.connect_to_db(username_field.get(), password_field.get())
		if (chkValue.get()):
			with open ("data", "w") as file:
				file.write(username_field.get()+"\n"+password_field.get())
		login.destroy()

	username_label = Label(login ,text="Username")
	username_label.grid(row=0,column = 0)
	username_field = Entry(login)
	username_field.grid(row=0,column=1)
	password_label = Label(login ,text="Password")
	password_label.grid(row=1,column=0)
	password_field = Entry(login, show="*")
	password_field.grid(row=1,column=1)
	login_btn = Button(login ,text="Login", command=login_fun)
	login_btn.grid(row=2,column=0)
	login.bind('<Return>', login_fun)
	remember = Checkbutton(login, text="Ricorda?", variable=chkValue)
	remember.grid(row=2, column=1)

	if (len(data) == 2):
		username_field.delete(0,END)
		username_field.insert(0, data[0].strip())
		password_field.delete(0,END)
		password_field.insert(0, data[1].strip())
		chkValue.set(True)



	login.mainloop()

def main():

	# database connection
	# TODO qui ci va la schermata di login nel caso della GUI,
	# altrimnti vengono chieste in input solo usrname e passw.


	# TODO: il parser andrebbe messo qua!

	if len(sys.argv) > 1:
		print("gui mode off")
		# AirTrack.connect_to_db()
		login_gui()
		sniffer = AirTrack.Sniffer(sys.argv[1] + " " + sys.argv[2])
		sniffer.start()
		try:
			while True:
				sleep(100)
		except KeyboardInterrupt:
			print("[*] Stop sniffing")
			sniffer.join(2.0)

			if sniffer.isAlive():
				sniffer.socket.close()

		# update database with the new records
		AirTrack.update_db()

	else:
		# AirTrack.connect_to_db()
		login_gui()
		print("gui mode on")
		root = Tk()
		root.geometry("800x500")
		app = AirTrackView()
		print(AirTrack.db_is_connected)
		if AirTrack.db_is_connected:
			app.updateScrolltext("\nDatabase connected\n")
		root.mainloop()


if __name__ == '__main__':
	main()
