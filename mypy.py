#-*- coding: utf-8 -*-
# 20210610
from __future__ import print_function
_print=print
from time import time as now
_ = {'_':now()}
#exec('def tryx(l,e=print):\n try:return l()\n except Exception as ex:return ex if True==e else e(ex) if e else None')
def tryx(l,e=print):
    try: return l()
    except Exception as ex: return ex if True==e else e(ex) if e else None
###############
import sys,types,marshal,signal,json
_eval = eval #lambda s:eval(s)
_import = __import__
flag_py2 = sys.version_info.major==2
_reload = _eval('reload') if flag_py2 else _import('importlib').reload
def refresh(n=__name__):
    try: del sys.modules[n]
    finally: return _import(n)
if flag_py2: from urllib2 import urlopen
else: from urllib.request import urlopen
wc=lambda u=None, data=None, m='POST',timeout=10:tryx(lambda:urlopen(u,data=data,timeout=timeout).read().decode())
class MyJsonEncoder(json.JSONEncoder):
    def default(self, obj): return tryx(lambda:json.JSONEncoder.default(self,obj),str)
s2o = lambda s:tryx(lambda:json.loads(s))
o2s = lambda o,indent=None:tryx(lambda:json.dumps(o, indent=indent, ensure_ascii=False, cls=MyJsonEncoder))
read = lambda f,m='r',encoding='utf-8':open(f,m,encoding=encoding).read()
write = lambda f,s,m='w',encoding='utf-8':open(f,m,encoding=encoding).write(s)
load = lambda f:s2o(read(f))
save = lambda f,o:write(f,o2s(o))
dumps_func = lambda func:marshal.dumps(func.__code__)
loads_func = lambda codes,ctx,name=None:types.FunctionType(marshal.loads(codes),ctx,name=name)
file2func = lambda fn,ctx,name=None:types.FunctionType(marshal.loads(read(fn)),ctx,name=name)
func2file = lambda fc,fn:write(fn,dumps_func(fc))
class obj(dict):# dict+
    def __init__(self,pa=None):
        for k in pa or {}:self[k]=pa[k]
    def __getattr__(self,k):return tryx(lambda:self[k],False)
    def __setattr__(self,k,v):self[k]=v
class probe:# cool
    def __init__(self,ev): self._ev=ev
    def __getattr__(self,k): return self._ev(k)
    #def __setattr__(self,k,v):self[k]=v # todo
#myself = probe(lambda k:eval(k))
###############
def hook_quit(on_quit):
    signal.signal(signal.SIGINT, on_quit)
    if sys.platform != 'win32': signal.signal(signal.SIGHUP, on_quit)
    signal.signal(signal.SIGTERM, on_quit)
###############
sgn = lambda v:1 if v>0 else -1 if v<0 else 0 # tryx(lambda:1 if v>0 else -1 if v<0 else 0, lambda v:0)
lvl = lambda v,d=0.05:round(v/d-sgn(v)*0.5) #level to zero by d
def time_add(days=0,date=None,outfmt=None,infmt='%Y-%m-%d',months=0):
    import datetime
    _dt = datetime.datetime.strptime(date,infmt) if date else datetime.datetime.now()
    if months!=0:
        from dateutil.relativedelta import relativedelta
        _dt += relativedelta(months=months)
    _dt += datetime.timedelta(days=days)
    if outfmt is None: outfmt = infmt
    return _dt.strftime(outfmt)
almost = lambda v1,v2,epsilon=0.0001:abs(v1-v2)<epsilon
#e.g. acct_num = get_match(r'\D*(\d*)',str(acct))
import re
def get_match(p,s):
    m = re.search( p, s, re.M|re.I)
    if m: return m.group(1)
def tiny_email(user, mypass,sender, receiver, title, html, cc=None, bcc=None):
    import smtplib
    from email.mime.text import MIMEText
    msg=MIMEText(html,'html','utf-8')
    msg['From'] = sender
    if type(receiver) is str:
        receiver_a = [receiver,]
        receiver_s = receiver
    else:
        receiver_a = receiver
        receiver_s = ';'.join([str(v) for v in receiver])
    msg['To'] = receiver_s
    msg['Subject']= title
    if cc: msg['Cc'] = cc
    if bcc: msg['Bcc'] = bcc
    server=smtplib.SMTP_SSL("smtp.qq.com", 465) 
    server.login(user, mypass)
    server.sendmail(sender, receiver_a, msg.as_string())
    server.quit()
