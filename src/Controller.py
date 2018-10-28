'''
Created on 26 0tt 2018

Controller dell'applicazione web

@author: Giovanni
'''

import os
import logging
from flask import Flask, session, request, flash
from flask.templating import render_template
from Model import Model

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__) # Applicazione Flask!
app.model = Model()

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return registro()
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    username = request.form['username']
    password = request.form['pass']
    count = app.model.getCountUsernamePassword(username, password)
    if count == 1:
        session['logged_in'] = True
        session['username']  = username
    else:
        flash('wrong password!')
    return home()
 
@app.route("/logout", methods=['POST'])
def logout():
    session['logged_in'] = False
    session['username']  = ""
    return home()

@app.route("/registro")
def registro():
    if session.get('logged_in'):
        return render_template('registro.html', username=session.get('username'))
    else:
        flash('wrong password!')
        return home()
        

if __name__ == '__main__': # Questo if deve essere ultima istruzione.
    app.secret_key = os.urandom(12)
    app.run(debug = True)  # Debug permette anche di ricaricare i file modificati senza rinizializzare il web server.