# Cython

Cython è un sistema di oofuscamento del codice python. Genera un file `.c` che poi può essere compilato in un eseguibile.

## Installazione

Per trasformare un codice python con cython bisogna seguire i seguenti passi. 

Installare [Pyenv](https://github.com/pyenv/pyenv#installation)

`$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv`

e aggiornare le variabili d'ambiente:

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
```

Controlla la versione:

`$ pyenv install 3.7.0` 
`$ pyenv versions`

Dopodichè installre `Cython` per python:

`$ pip3 install cython` 

## Script di esecuzione

E' stato creato uno script automatico per lanciare i comandi di compilazione Cython e per generare l'eseguibile. Il file è `make_cython.sh`.
Si avvia nel seguente modo: 

`$ ./make_cython.sh nome_utente nome_app` 

dove `nome_utente` e `nome_app` sono due parametri specifici della macchina e dell'applicazione prodotta.