#!/bin/bash

# ---------------------------------------------------
# INIZIO SCRIPT CYTHON
# ---------------------------------------------------

# Primo parametro: Nome Utente
# Secondo parametro: Nome Applicazione py

echo "INIZIO ESECUZIONE"
echo "--------------------------------------------------------------------------------"

utente=$1
nome_app=$2

cython --embed -o $nome_app.c $nome_app.py
gcc -v -Os -I /Users/$utente/.pyenv/versions/3.7.0/include/python3.7m/ -L /Library/Frameworks/Python.framework/Versions/3.7/lib/ -o $nome_app $nome_app.c -lpython3.7 -lpthread -lm -lutil -ldl

echo "--------------------------------------------------------------------------------";
echo "FINE ESECUZIONE";