from flask import *

import importlib,json

app=Flask(__name__)

@app.route('/<c>.<m>')
def main(c,m):
    try:
        cc = importlib.import_module(c)(request=request)
        mm = getattr(cc,m)
        return (json.dumps(mm()))
    except Exception as ex:
        return ({'errmsg':str(ex)})

@app.route('/')
def default():return 'null'

#:st
#set FLASK_APP=svr.py && set FLASK_ENV=development
#python -m flask run -h 0.0.0.0 -p 8888 --with-threads --reload --debugger
#goto st
