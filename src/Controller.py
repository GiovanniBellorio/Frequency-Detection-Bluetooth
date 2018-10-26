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
        return "Hello!!!  <a href='/logout'>Logout</a>"
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['pass'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()
 
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


if __name__ == '__main__': # Questo if deve essere ultima istruzione.
    app.secret_key = os.urandom(12)
    app.run(debug = True)  # Debug permette anche di ricaricare i file modificati senza rinizializzare il web server.