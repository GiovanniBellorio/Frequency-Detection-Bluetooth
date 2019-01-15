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
import getpass
from time import sleep

previousNumberOfStudends = 0

class AirTrackView(Frame):

	def __init__(self):
		super().__init__()

		self.startButton = []
		self.stopButton = []
		self.scrollbarLog = None

		self.INTERFACES = []
		self.iface = StringVar(self)
		self.sniffer = None
		self._job = None

		self.setup()
		self.initUI()


	def setup(self):
		# get interfaces lits
		self.INTERFACES = psutil.net_if_addrs()

	def initUI(self):

		self.master.title("AirTrack")
		#self.style = Style()
		#self.style.theme_use("default")

		top_label = Label(self, text = "Welcome to AirTrack:")
		top_label.pack(side = TOP, padx = 5, pady = 5, anchor = 'w')

		scrollbarLogFrame = Frame(self, relief = RAISED, borderwidth = 1)
		scrollbarLogFrame.pack(fill = BOTH, expand = True)

		self.pack(fill = BOTH, expand = True)

		self.scrollbarLog = scrolledtext.ScrolledText(scrollbarLogFrame, background = "black", foreground = "green")
		self.scrollbarLog.pack(fill = BOTH, expand = True, padx = 5, pady = 5)

		self.startButton = Button(self, text = "Start", command = self.start)
		self.startButton.pack(side = RIGHT, padx = 5, pady = 5)
		self.stopButton = Button(self, text = "Stop", command = self.stop, state = DISABLED)
		self.stopButton.pack(side = RIGHT)

		interface_label = Label(self, text = "Interface:")
		interface_label.pack(side = LEFT, padx = 5, pady = 5)

		interfaces_list = OptionMenu(self, self.iface, next(iter(self.INTERFACES)), *self.INTERFACES)
		interfaces_list.pack(side = LEFT)

		self.updateScrolltext("Select network interface and press Start.")


	def updateScrolltext(self, txt):
		# http://effbot.org/tkinterbook/text.htm  <-- qui spiega xk bisogna usare questa funzione!
		#print(txt)
		self.scrollbarLog.config(state = NORMAL)
		self.scrollbarLog.insert(END, str(txt) + "\n")
		self.scrollbarLog.see("end")
		self.scrollbarLog.config(state = DISABLED)


	def cleanScrollText(self):
		self.scrollbarLog.config(state = NORMAL)
		self.scrollbarLog.delete("1.0", END)
		self.scrollbarLog.config(state = DISABLED)


	def start(self):
		self.startButton.config(state=DISABLED)
		self.stopButton.config(state=NORMAL)
		self.sniffer = AirTrack.Sniffer('-i '+self.iface.get())
		self.sniffer.start()

		#AirTrack.start_session('-i '+self.iface.get())
		self.cleanScrollText()
		self.updateScrolltext("Inizio rilevazione:")

		numberOfpresences = 0

		def count():
			#print("called count")
			nonlocal numberOfpresences
			if numberOfpresences != len(self.sniffer.presences):
				numberOfpresences = len(self.sniffer.presences)

				self.cleanScrollText()
				self.updateScrolltext("Numero di presenze: " + str(numberOfpresences))
				self.updateScrolltext("---------------------")
				for presence in self.sniffer.presences:
					self.updateScrolltext(presence)

			self._job = self.after(5000, count)

		count()

	def stop(self):
		#os.killpg(os.getpgid(self.pid), signal.SIGINT)
		print("[*] Stop sniffing")
		self.sniffer.join(2.0)

		if self.sniffer.isAlive():
			self.sniffer.socket.close()

		# update database with the new records
		AirTrack.update_db()
		self.startButton.config(state=NORMAL)
		self.stopButton.config(state=DISABLED)

		if self._job is not None:
			self.after_cancel(self._job)
			self._job = None


def login_gui(root):
	def null_action():
		root.destroy()

	data = []

	login = Toplevel()
	login.geometry("275x125")
	login.title("Login")
	login.protocol("WM_DELETE_WINDOW", null_action)

	chkValue = BooleanVar()
	chkValue.set(False)

	try:
		with open ("data", "r") as file:
			data=file.readlines()
	except:
		pass

	def login_fun(event=None):
		if (AirTrack.connect_to_db(username_field.get(), password_field.get()) != -1):
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
	password_field = Entry(login, show="\u2022")
	password_field.grid(row=1,column=1)
	remember = Checkbutton(login, text="Ricordami", variable=chkValue)
	remember.grid(row=2, column=1)
	login_btn = Button(login ,text="Login", command=login_fun)
	login_btn.grid(row=3,column=1)
	login.bind('<Return>', login_fun)

	if (len(data) == 2):
		username_field.delete(0,END)
		username_field.insert(0, data[0].strip())
		password_field.delete(0,END)
		password_field.insert(0, data[1].strip())
	root.lower(belowThis=login)
	login.mainloop()

def main():

	# TODO: il parser andrebbe messo qua!

	if len(sys.argv) > 1:
		print("gui mode off")
		username = input("Enter username: ")
		password = getpass.getpass ("Enter password: ")

		AirTrack.connect_to_db(username, password)
		print("Start sniffing...\n")
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
		print("gui mode on")
		root = Tk()
		root.geometry("800x500")
		app = AirTrackView()

		if AirTrack.db_is_connected:
			app.updateScrolltext("\nDatabase connected")

		login_gui(root)
		root.mainloop()

if __name__ == '__main__':
	main()
