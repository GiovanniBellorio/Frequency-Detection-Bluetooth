#!/usr/bin/python3
# -*- coding: utf-8 -*-

if __name__ == 'requirements':
    import sys
    #from importlib import import_module
    from pip._internal import main as pipmain

    print('Check all dependencies...\n')

    if sys.version_info < (3, 0, 0, 'final', 0):
        print('Python 3.0 or later is required!\n')
        sys.exit()
        
    try:
        import django
    except ImportError:
        print('django was no module installed\n')
        pipmain(['install', 'django'])
        print('django was installed\n')
        
    try:
        import functools 
    except ImportError:
        print('functools was no module installed\n')
        pipmain(['install', 'functools'])
        print('functools was installed\n')
        
    try:
        import flask
    except ImportError:
        print('flask was no module installed\n')
        pipmain(['install', 'flask'])
        print('flask was installed\n')
        
    try:
        import flask_login 
    except ImportError:
        print('flask_login was no module installed\n')
        pipmain(['install', 'flask_login'])
        print('flask_login was installed\n')
        
    try:
        import couchdb 
    except ImportError:
        print('couchdb was no module installed\n')
        pipmain(['install', 'couchdb'])
        print('couchdb was installed\n')
    
    try:
        import werkzeug 
    except ImportError:
        print('werkzeug was no module installed\n')
        pipmain(['install', 'werkzeug'])
        print('werkzeug was installed\n')
        
    print('Great, all it was installed!\n')
