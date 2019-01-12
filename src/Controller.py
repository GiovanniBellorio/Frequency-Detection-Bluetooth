#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Created on 26 0tt 2018

Controller dell'applicazione web

@author: Giovanni, Davide
'''
import requirements

from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from django.utils.html import strip_tags
from functools import wraps
from flask import Flask, request, flash, redirect, url_for, send_file
from flask.templating import render_template
from Model import Model
import os
import csv

# Classe di appoggio per i dati che arrivano dal DB
class User(UserMixin):
    def __init__(self, id_utente = None, username = '', ruolo = None):
        self.id = id_utente
        self.username = username
        self.ruolo = ruolo

# Applicazione Flask!
#logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__) 
app.model = Model()

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'
login_manager.session_protection = 'strong'

# Decorator for roles
def check_roles(roles = None, page = 'home'):
    def decorator(f):
        @wraps(f)
        def func_wrapper(*args, **kwargs):
            if current_user.ruolo in roles:
                return f(*args, **kwargs)
            return redirect(url_for(page, next=request.url)) 
        return func_wrapper
    return decorator

# Per impedire all'utente di tornare indietro dopo aver fatto il logout
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@login_manager.user_loader
def load_user(user_id):
    username = app.model.getUsername(user_id);
    if username is None:
        return None
    ruolo = app.model.getRuoloUsername(user_id);
    return User(user_id,username,ruolo)

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
        user = User(id_utente,username,ruolo)
        login_user(user)
        return redirect('/registro')
    else:
        flash('wrong password!')
        return redirect('/')

@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route("/view_modify_pwd", methods=['POST'])
@login_required
@check_roles([0,1,2],'registro')
def view_modify_pwd():
    return render_template('modify_pwd.html', matricola_profilo='admin')

@app.route("/view_modify_pwd_profilo", methods=['POST'])
@login_required
@check_roles([0],'registro')
def view_modify_pwd_profilo():
    matricola_profilo = strip_tags(request.form["matricola_profilo"]).strip()
    return render_template('modify_pwd.html', matricola_profilo=matricola_profilo)

@app.route("/modify_pwd", methods=['POST'])
@login_required
def modify_pwd():
    matricola_profilo = strip_tags(request.form["matricola_profilo"]).strip()
    password1 = strip_tags(request.form['pass1']).strip()
    password2 = strip_tags(request.form['pass2']).strip()
    if password1 == password2:
        user = current_user
        password_codificata = app.model.make_md5(app.model.make_md5(password2))
        if matricola_profilo == 'admin':
            ack_pwd = app.model.updateUserPwd(user.id, password_codificata)
        else:
            id_profilo, utente_profilo = app.model.getProfiloUtente(matricola_profilo)
            ack_pwd = app.model.updateUserPwd(id_profilo, password_codificata)
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
@check_roles([0,1,2],'registro')
def registro():
    user = current_user
    matricola = app.model.getMatricola(user.id)
    if user.ruolo == 1 or user.ruolo == 2:
        id_profilo, utente_profilo = app.model.getProfiloUtente(matricola)
        macs = app.model.getIdMac(id_profilo)
        mac = macs[0]['mac']
        if user.ruolo == 1:
            ruolo_profilo = "supervisore"
        elif user.ruolo == 2:
            ruolo_profilo = "utente"
        frequenza_profilo = app.model.getFrequenzaUsername(id_profilo)
        return render_template('registro.html', mac=mac, username=user.username, id_utente=user.id, utente_profilo=utente_profilo, frequenza_profilo=frequenza_profilo, ruolo_profilo=ruolo_profilo, ruolo=user.ruolo)
    elif user.ruolo == 0:
        utenti_punteggi = app.model.getUtentiPunteggi()
        supervisori_punteggi = app.model.getSupervisoriPunteggi()
        utenti_punteggi = sorted(utenti_punteggi, key=lambda utenti: utenti[0]['cognome'])
        supervisori_punteggi = sorted(supervisori_punteggi, key=lambda utenti: utenti[0]['cognome'])
        return render_template('registro.html', username=user.username, ruolo=user.ruolo, supervisori_punteggi=supervisori_punteggi, utenti_punteggi=utenti_punteggi)
    else:
        flash('wrong password!')
        return redirect('/')

@app.route("/registro_supervisori", methods=['POST'])
@login_required
def registro_supervisori():
    user = current_user
    supervisori_punteggi = app.model.getSupervisoriPunteggi()
    return render_template('registro.html', username=user.username, ruolo=user.ruolo, supervisori_punteggi=supervisori_punteggi)

@app.route("/registro_utenti", methods=['POST'])
@login_required
def registro_utenti():
    user = current_user
    utenti_punteggi = app.model.getUtentiPunteggi()
    return render_template('registro.html', username=user.username, ruolo=user.ruolo, utenti_punteggi=utenti_punteggi)

@app.route("/profilo", methods=['POST'])
@login_required
def profilo():
    user = current_user
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
    return render_template('aggiungiUtente.html')

@app.route("/aggiungi_utente", methods=['POST'])
@login_required
def aggiungi_utente():
    user = current_user
    username = strip_tags(request.form['username']).strip()
    nome = strip_tags(request.form['nome']).strip()
    cognome = strip_tags(request.form['cognome']).strip()
    matricola = str(strip_tags(request.form['matricola']).strip()).upper()
    mac = strip_tags(request.form['mac']).strip()
    pwd = strip_tags(request.form['password']).strip()
    password_codificata = str(app.model.make_md5(app.model.make_md5(pwd)))
    ack_user = app.model.addUser(username, nome, cognome, matricola, mac, password_codificata)
    return redirect('/registro')

@app.route("/elimina_utente", methods=['POST'])
@login_required
def elimina_utente():
    user = current_user
    matricola_profilo = strip_tags(request.form["matricola_profilo"]).strip()
    id_profilo, utente_profilo = app.model.getProfiloUtente(matricola_profilo)
    ack_user  = app.model.deleteUser(id_profilo)
    return redirect('/registro')

@app.route("/aggiungi_presenza", methods=['POST'])
@login_required
def aggiungi_presenza():
    user = current_user
    matricola_profilo = strip_tags(request.form["matricola_profilo"]).strip()
    id_profilo, utente_profilo = app.model.getProfiloUtente(matricola_profilo)
    ack_aggiungi_presenza = app.model.aggiungi_presenza(id_profilo)
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

@app.route("/export_punteggi", methods=['POST'])
@login_required
def export_punteggi():
    utenti_punteggi      = app.model.getUtentiPunteggi() # [utente][tempo][punteggio]
    supervisori_punteggi = app.model.getSupervisoriPunteggi()
    
    dati = list()
    for utente in utenti_punteggi:
        matricola = utente[0]['matricola']
        nome = utente[0]['nome']
        cognome = utente[0]['cognome']
        tempo = utente[1]
        punteggio = utente[2]
        dati.append({'matricola':matricola,'nome':nome,'cognome':cognome,'tempo':tempo,'punteggio':punteggio})
        
    nomeFile = 'voti.csv'
    with open(nomeFile, mode='w', encoding='utf-8') as csvFile:
        nomiCampi = ['matricola','nome','cognome','tempo','punteggio']
        writer = csv.DictWriter(csvFile,fieldnames=nomiCampi)
        writer.writeheader()
        for riga in dati:
            writer.writerow(riga)
    
    # scrittura nel db di tempo e punteggio come backup
    for riga in dati:
        matricola_profilo = riga['matricola']
        tempo_profilo = riga['tempo']
        punteggio_profilo = riga['punteggio']
        id_profilo, utente_profilo = app.model.getProfiloUtente(matricola_profilo)
        ack_updateUtentiPunteggi = app.model.updateUtentiPunteggi(id_profilo, tempo_profilo, punteggio_profilo)
        
    # download file
    try:
        return send_file("voti.csv", as_attachment=True)
    except Exception as e:
        self.log.exception(e)
        self.Error(400)
    
    return redirect('/registro')
        

if __name__ == '__main__': # Questo if deve essere ultima istruzione.
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port="5000", debug=True, use_reloader=True)  # Debug permette anche di ricaricare i file modificati senza rinizializzare il web server.