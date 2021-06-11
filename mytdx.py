from pytdx.hq import TdxHq_API as hq
import sys
def get_market(code):
    code=str(code)[-6:].zfill(6) 
    if code.startswith('6') or code.startswith('9') or code.startswith('11') or code.startswith('5'):
      return 1,code #sh
    else:
      return 0,code

class mytdx:
    def __init__(self,tdxhq_host,tdxhq_port,auto_connect=True):
        #tdxhq_host = '47.103.48.45' # get from fuyi client-ap directly..
        #tdxhq_port=7709
        self.host = tdxhq_host
        self.port = tdxhq_port
        _hq = hq(heartbeat=True, auto_retry=True
                 #, raise_exception=True
                 )
        if auto_connect == True:
            if not _hq.connect(tdxhq_host, tdxhq_port):
                print('failed tdxhq conn')
                sys.exit()#tmp
        self._hq = _hq

    def conn(self): return self._hq.connect(self.host,self.port)

    def get_security_quotes_80(self, code_a):
        return self._hq.get_security_quotes([get_market(c) for c in code_a])
    
    def get_market_records_80(self, code_a):
        rs = self.get_security_quotes_80(code_a)
        if rs is None: return []
        df = self._hq.to_df(rs)
        if df.empty: return []
        df1=df[['code','market','last_close','price','servertime']]
        #_print(df1)
        dict_a = df1.to_dict(orient='records')
        rt = []
        for _row in dict_a:
            _code = _row.get('code',None)
            if _code is not None:
                if _code.startswith('1') or _code.startswith('5'):# tmp hck ^5... # todo...
                    _row['price'] = round(float(_row['price']/10),2)
                    _row['last_close']=round(float(_row['last_close']/10),2)
            rt.append(_row)
        return rt

    def get_market_records(self, code_a, rt=[]):
        #rt = []
        while True:
            code_a_80 = code_a[0:80]
            if not len(code_a_80)>0: break
            #print(code_a_80)
            rt += self.get_market_records_80(code_a_80)
            code_a = code_a[80:]
        return rt
