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
