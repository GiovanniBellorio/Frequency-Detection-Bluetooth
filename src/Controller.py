'''
Created on 26 0tt 2018

Controller dell'applicazione web

@author: Giovanni, Davide
'''

import os
import logging
from django.utils.html import strip_tags
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask import Flask, request, flash, redirect, session
from flask_sessionstore import Session
from flask.templating import render_template
from Model import Model

# Classe di appoggio per i dati che arrivano dal DB
class User(UserMixin):
    
    __instance = None
    
    def __init__(self, id_utente = None, username = '', ruolo = None):
        if User.__instance != None:
            raise Exception("This class is a singleton!")
        self.id = id_utente
        self.username = username
        self.ruolo = ruolo
        User.__instance = self
        
    @staticmethod
    def getUser():
        """ Static access method. """
        if User.__instance == None:
            raise Exception("This class is a singleton!")
        return User.__instance
    
    @staticmethod
    def deleteUser():
        User.__instance = None

# Applicazione Flask!
sessione = Session()
#logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__) 
app.model = Model()

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'
login_manager.session_protection = 'strong'

# Per impedire all'utente di tornare indietro dopo aver fatto il logout
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/')
def home():
    return render_template('login.html')
 
@app.route('/login', methods=['POST'])
def login():
    username = strip_tags(request.form['username'])
    password = strip_tags(request.form['pass'])
    password_codificata = app.model.make_md5(app.model.make_md5(password))
    num_rows, id_utente = app.model.getCountUsernamePassword(username, password_codificata)
    ruolo = app.model.getRuoloUsername(id_utente)
    if num_rows == 1:
        User(id_utente,username,ruolo)
        login_user(User.getUser())
        return redirect('/registro')
    else:
        flash('wrong password!')
        return redirect('/')

@login_manager.user_loader
def load_user(user_id):
    user = User.getUser()
    if user.id == str(user_id):
        return user
    return None

@app.route("/logout", methods=['POST'])
@login_required
def logout():
    User.deleteUser()
    logout_user()
    return redirect('/')

@app.route("/view_modify_pwd", methods=['POST','GET'])
@login_required
def view_modify_pwd():
    return render_template('modify_pwd.html')

@app.route("/modify_pwd", methods=['POST'])
@login_required
def modify_pwd():
    password1 = strip_tags(request.form['pass1']).strip()
    password2 = strip_tags(request.form['pass2']).strip()
    if password1 == password2:
        user = User.getUser()
        password_codificata = app.model.make_md5(app.model.make_md5(password2))
        ack_pwd = app.model.updateUserPwd(user.id, password_codificata)
        if ack_pwd:
            return redirect('/registro')
        else:
            return redirect('/view_modify_pwd')
    else:
        return redirect('/view_modify_pwd')
    
@app.route("/view_modify_mac", methods=['POST','GET'])
@login_required
def view_modify_mac():
    matricola_profilo = strip_tags(request.form["matricola_profilo"]).strip()
    return render_template('modify_mac.html', matricola_profilo=matricola_profilo)
    
@app.route("/modify_mac", methods=['POST'])
@login_required
def modify_mac():
    mac1 = strip_tags(request.form['mac1']).strip()
    mac2 = strip_tags(request.form['mac2']).strip()
    matricola_profilo = strip_tags(request.form["matricola_profilo"]).strip()
    id_profilo, utente_profilo = app.model.getProfiloUtente(matricola_profilo)
    if mac1 == mac2:
        user = User.getUser()
        ack_mac = app.model.updateUserMac(id_profilo, mac1)
        if ack_mac:
            return redirect('/registro')
        else:
            return redirect('/view_modify_mac')
    else:
        return redirect('/view_modify_mac')
        
# 0 --> admin, 
# 1 --> supervisore, 
# 2 --> utente normale
@app.route("/registro", methods=['POST','GET'])
@login_required
def registro():
    user = User.getUser()
    matricola = app.model.getMatricola(user.id)
    if user.ruolo == 2:
        frequenza = app.model.getFrequenzaUsername(user.id)
        return render_template('registro.html', username=user.username, matricola=matricola, id_utente=user.id, ruolo=user.ruolo, frequenza=frequenza)
    #elif ruolo == 1:
    elif user.ruolo == 0:
        utenti_punteggi = app.model.getUtentiPunteggi()
        supervisori_punteggi = app.model.getSupervisoriPunteggi()
        return render_template('registro.html', username=user.username, ruolo=user.ruolo, supervisori_punteggi=supervisori_punteggi, utenti_punteggi=utenti_punteggi)
    else:
        flash('wrong password!')
        return redirect('/')

@app.route("/registro_supervisori", methods=['POST'])
@login_required
def registro_supervisori():
    user = User.getUser()
    supervisori_punteggi = app.model.getSupervisoriPunteggi()
    return render_template('registro.html', username=user.username, ruolo=user.ruolo, supervisori_punteggi=supervisori_punteggi)

@app.route("/registro_utenti", methods=['POST'])
@login_required
def registro_utenti():
    user = User.getUser()
    utenti_punteggi = app.model.getUtentiPunteggi()
    return render_template('registro.html', username=user.username, ruolo=user.ruolo, utenti_punteggi=utenti_punteggi)

@app.route("/profilo", methods=['POST'])
@login_required
def profilo():
    user = User.getUser()
    username     = user.username
    id_utente    = user.id
    matricola_profilo = request.form['matricola']
    id_profilo, utente_profilo = app.model.getProfiloUtente(matricola_profilo)
    ruolo_profilo = app.model.getRuoloUsername(id_profilo)
    macs = app.model.getIdMac(id_profilo)
    mac = macs[0]['mac']
    if ruolo_profilo == 0:
        ruolo_profilo = "admin"
    elif ruolo_profilo == 1:
        ruolo_profilo = "supervisore"
    elif ruolo_profilo == 2:
        ruolo_profilo = "utente"
    frequenza_profilo = app.model.getFrequenzaUsername(id_profilo)
    return render_template('profilo.html', mac=mac, username=username, id_utente=id_utente, utente_profilo=utente_profilo, frequenza_profilo=frequenza_profilo, ruolo_profilo=ruolo_profilo)

@app.route("/view_aggiungi_utente", methods=['POST'])
@login_required
def view_aggiungi_utente():
    user = User.getUser()
    return render_template('aggiungiUtente.html')

@app.route("/aggiungi_utente", methods=['POST'])
@login_required
def aggiungi_utente():
    user = User.getUser()
    username = strip_tags(request.form['username']).strip()
    nome = strip_tags(request.form['nome']).strip()
    cognome = strip_tags(request.form['cognome']).strip()
    matricola = strip_tags(request.form['matricola']).strip()
    mac = strip_tags(request.form['mac']).strip()
    pwd = strip_tags(request.form['password']).strip()
    password_codificata = str(app.model.make_md5(app.model.make_md5(pwd)))
    ack_user = app.model.addUser(username, nome, cognome, matricola, mac, password_codificata)
    return redirect('/registro')

@app.route("/elimina_utente", methods=['POST'])
@login_required
def elimina_utente():
    user = User.getUser()
    matricola_profilo = strip_tags(request.form["matricola_profilo"]).strip()
    id_profilo, utente_profilo = app.model.getProfiloUtente(matricola_profilo)
    ack_user   = app.model.deleteUser(id_profilo)
    return redirect('/registro')

@app.route("/cambio_ruolo", methods=['POST'])
@login_required
def cambio_ruolo():
    matricola_profilo = strip_tags(request.form["matricola_profilo"]).strip()
    id_profilo, utente_profilo = app.model.getProfiloUtente(matricola_profilo)
    ruolo_profilo = app.model.getRuoloUsername(id_profilo)
    option_ruolo  = request.form['option_ruolo']
    if ruolo_profilo == 1 and option_ruolo == "Supervisore":
        pass
    elif ruolo_profilo == 2 and option_ruolo == "Utente":
        pass
    else:
        ack_ruolo = app.model.updateRuolo(id_profilo, option_ruolo)
    return redirect('/registro')
        

if __name__ == '__main__': # Questo if deve essere ultima istruzione.
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_KEY']   = os.urandom(16)
    app.secret_key = os.urandom(12)
    sessione.init_app(app)
    app.run(debug=True, use_reloader=True)  # Debug permette anche di ricaricare i file modificati senza rinizializzare il web server.
