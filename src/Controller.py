'''
Created on 26 0tt 2018

Controller dell'applicazione web

@author: Giovanni
'''

import os
import logging
from flask import Flask, session, request, flash
from flask.templating import render_template

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__) # Applicazione Flask!

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
    if username == 'admin' and password == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()
 
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

@app.route("/registro")
def registro():
    if session.get('logged_in'):
        return render_template('registro.html')
    else:
        flash('wrong password!')
        return home()
        

if __name__ == '__main__': # Questo if deve essere ultima istruzione.
    app.secret_key = os.urandom(12)
    app.run(debug = True)  # Debug permette anche di ricaricare i file modificati senza rinizializzare il web server.