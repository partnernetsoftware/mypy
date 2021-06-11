# ver 20210508a
import time
_ = {'_':time.time()}

class main:
    def __init__(self, dbstr_file=None, debug=False,
            dbstr='{protocol}://{user}:{password}@{host}:{port}/{db}?charset={charset}',
            db='', protocol='mysql', user='root',password='', host='127.0.0.1', port=3306, charset='utf8mb4'
            ):
        _hash = hash(self)
        _[_hash]={}
        try:
            if dbstr_file:
                with open(dbstr_file, 'r') as file:
                    dbstr = file.read().replace('\n', '')
            from urllib.parse import quote_plus
            _dbstr = dbstr.format(db=db,protocol=protocol,user=user,password=quote_plus(password),host=host,port=port,charset=charset)
            if debug:
                print(_dbstr)
                _[_hash]['_dbstr']=_dbstr
            from sqlalchemy import create_engine
            self.engine = engine = create_engine(_dbstr)
        except Exception as ex:
            print(ex)

    def __del__(self): _.pop(hash(self), None)
    def do(self,sql='',args=None):
        _sql = sql.lower().strip()
        rst = self.engine.execute(_sql);#TODO test with args later
        rows = None
        cols = None
        if _sql.startswith('select') or _sql.startswith('show'):
            rows = rst.fetchall()
            cols = rst.keys()
        return rows, cols, rst

if __name__ == '__main__':
    # test = main(port=3333, password='123456', debug=True)
    test = main(port=3333, password='123456', debug=True, protocol='mysql+pymysql')
    test = main(dbstr_file='db.tmp')
    #rows, cols, rst = test.do('show databases')
    rows, cols, rst = test.do('show variables')
    print(rows,cols)

    # pip install pymsyql sqlalchemy
    # protocol
    ## (windows) pip install mysqlclient

