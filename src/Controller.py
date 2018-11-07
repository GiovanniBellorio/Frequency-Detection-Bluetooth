'''
Created on 26 0tt 2018

Controller dell'applicazione web

@author: Giovanni, Davide
'''

import os
import logging
from flask import Flask, session, request, flash, escape
#from flask_sessionstore import Session
from flask.templating import render_template
from Model import Model
from django.utils.html import strip_tags


#sessione = Session()
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
def login():
    username = strip_tags(request.form['username'])
    password = strip_tags(request.form['pass'])
    password_codificata = app.model.make_md5(app.model.make_md5(password))
    num_rows, id_utente = app.model.getCountUsernamePassword(username, password_codificata)
    if num_rows == 1:
        session['logged_in'] = True
        session['username']  = username
        session['id_utente'] = id_utente
    else:
        flash('wrong password!')
    return home()
 
@app.route("/logout", methods=['POST'])
def logout():    
    session['logged_in'] = False
    session['username']  = ""
    session['id_utente'] = 0
    #session.clear();
    return home()

@app.route("/view_modify_pwd", methods=['POST'])
def view_modify_pwd():
    return render_template('modify_pwd.html')

@app.route("/modify_pwd", methods=['POST'])
def modify_pwd():
    password1 = strip_tags(request.form['pass1'])
    password2 = strip_tags(request.form['pass2'])
    if password1 == password2:
        password_codificata = app.model.make_md5(app.model.make_md5(password2))
        id_utente = session.get('id_utente')
        ack_pwd = app.model.updateUserPwd(id_utente, password_codificata)
        if ack_pwd:
            return registro()
        else:
            return view_modify_pwd()
    else:
        return view_modify_pwd()

@app.route("/registro")
def registro():
    if session.get('logged_in'):
        username  = session.get('username')
        id_utente = session.get('id_utente')
        ruolo = app.model.getRuoloUsername(id_utente) # 1 --> admin, 2 --> utente normale
        if ruolo == "2":
            frequenza = app.model.getFrequenzaUsername(id_utente)
            return render_template('registro.html', username=username, id_utente=id_utente, ruolo=ruolo, frequenza=frequenza)
        elif ruolo == "1":
            utenti_punteggi = app.model.getUtentiPunteggi()
            return render_template('registro.html', username=username, id_utente=id_utente, ruolo=ruolo, utenti_punteggi=utenti_punteggi)
    else:
        flash('wrong password!')
        return home()
        

if __name__ == '__main__': # Questo if deve essere ultima istruzione.
    #app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_KEY']   = os.urandom(16)
    app.secret_key = os.urandom(12)
    #sessione.init_app(app)
    app.run(debug = True)  # Debug permette anche di ricaricare i file modificati senza rinizializzare il web server.