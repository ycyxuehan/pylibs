#!/usr/bin/python3
###########################################################
# Feature: a lib for db connect and query
# Author : Bing
# Version: 1.0
# Email  : kun1.huang@outlook.com
# Date   : 2016-11-24
###########################################################

from pymysql import Connect as myconnect
from impala.dbapi import connect as impconnect
from pyhs2 import connect as hiveconnect
try:
    import cx_Oracle
except ImportError as ex:
    print(ex)

class MSSQL():
    """
    #nnd
    """
    def __doc__(self):
        pass

    def __init__(self, host, user, passwd, port=2521, db=''):
        if port is None:
            port = 2521
        self.host = "%s:%s" % (host, str(port))
        self.user = user
        self.password = passwd
        self.database = db
        self.conn = None
        self.cur = None
        self.get_conn()


    def get_conn(self):
        """
        get a mssql connection
        """
        if self.host and self.user and self.password:
            try:
                self.conn = msconnect(host=self.host, user=self.user,\
                    password=self.password, database=self.database, charset='utf8')
                self.cur = self.conn.cursor()
            except Exception as ex:
                raise ex


    def query(self, sql):
        """
        execut a sql
        """
        if self.conn and self.cur:
            try:
                self.cur.execute(sql)
                data = []
                if 'SELECT' in sql.upper():
                    data = self.cur.fetchall()
                self.conn.commit()
                return True, data
            except Exception as ex:
                raise ex

    def close_conn(self):
        """
        close the connection
        """
        if self.conn and self.cur:
            try:
                self.cur.close()
                self.conn.close()
            except Exception as ex:
                print(ex)


    def show(self):
        """
        show connection information
        """
        print(
            """
            Host    :%s
            User    :%s
            Password:%s
            DataBase:%s
            """ %(self.host, self.user, self.password, self.database)
        )


    def __del__(self):
        self.close_conn()

class MYSQL():
    """
    #nnd
    """
    def __doc__(self):
        pass

    def __init__(self, host, user, passwd, port=3306, db=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = passwd
        self.database = db
        self.conn = None
        self.cur = None
        self.get_conn()


    def get_conn(self):
        """
        get a mssql connection
        """
        if self.port is None:
            self.port = 3306
        if self.host and self.user and self.password:
            try:
                self.conn = myconnect(host=self.host, port=int(self.port),\
                    user=self.user, password=self.password, database=self.database, charset='utf8')
                self.cur = self.conn.cursor()
            except Exception as ex:
                raise ex


    def query(self, sql):
        """
        execut a sql
        """
        if self.conn and self.cur:
            try:
                self.cur.execute(sql)
                data = self.cur.fetchall()
                self.conn.commit()
                return True, data
            except Exception as ex:
                raise ex

    def close_conn(self):
        """
        close the connection
        """
        if self.conn and self.cur:
            try:
                self.cur.close()
                self.conn.close()
            except Exception as ex:
                print(ex)


    def show(self):
        """
        show connection information
        """
        print(
            """
            Host    :%s
            Port    :%d
            User    :%s
            Password:%s
            DataBase:%s
            """ %(self.host, int(self.port), self.user, self.password, self.database)
        )


    def __del__(self):
        self.close_conn()

class IMPALA():
    """
    #nnd
    """
    def __doc__(self):
        pass

    def __init__(self, host, host_bak=None, port=21050, db=None):
        self.host = host
        self.host_bak = host_bak
        self.port = port
        self.database = db
        self.conn = None
        self.cur = None
        self.get_conn()

    def get_conn(self):
        """
        get a impala connection
        """
        if self.port is None:
            self.port = 21050
        try:
            self.conn = impconnect(self.host, int(self.port), self.database)
            self.cur = self.conn.cursor()
        except Exception as ex:
            if self.host_bak:
                print('connect to server:%s failed, try the backup: %s' %(self.host, self.host_bak))
                try:
                    self.conn = impconnect(self.host_bak, int(self.port), self.database)
                    self.cur = self.conn.cursor()
                except Exception as ex:
                    raise ex
            raise ex

    def query(self, sql):
        """
        execut a sql
        """
        if self.conn and self.cur:
            try:
                self.cur.execute(sql)
                data = self.cur.fetchall()
                self.conn.commit()
                return True, data
            except Exception as ex:
                raise ex

    def close_conn(self):
        """
        close the connection
        """
        if self.conn and self.cur:
            try:
                self.cur.close()
                self.conn.close()
            except Exception as ex:
                print(ex)


    def show(self):
        """
        show connection information
        """
        print(
            """
            Host    :%s
            Port    :%d
            User    :%s
            Password:%s
            DataBase:%s
            """ %(self.host, int(self.port), self.database)
        )


    def __del__(self):
        self.close_conn()

class ORACLE():
    """
    oracle
    """
    def __init__(self, host, port, instance, user, passwd):
        self.host = host
        self.port = port
        self.instance = instance
        self.user = user
        self.password = passwd
        self.conn = None
        self.cur = None
        self.__init_db()

    def __init_db(self):
        self.connect_cmd = "%s/%s@%s:%s/%s" % \
            (self.user, self.password, self.host, int(self.port), self.instance)
        try:
            self._conn = cx_Oracle.connect(self.connect_cmd)
            self._cur = self._conn.cursor()
        except Exception as ex:
            self._cur = None
            self._conn = None
            raise ex

    def query(self, sql):
        """
        query
        """
        if self._conn and self._cur:
            try:
                self._cur.execute(sql)
                data = self._cur.fetchall()
                self._conn.commit()
                return True, data
            except Exception as ex:
                raise ex

    def close(self):
        """
        query
        """
        self._cur.close()
        self._conn.close()

    def __del__(self):
        self.close()

#hive
class HIVE(object):
    def __init__(self, host, user, password, db, port=10000, authMechanism='PLAIN'):
        self.host = host
        self.user = user
        self.password = password
        self.database = db
        self.port = port
        self.authMechanism = authMechanism
        self.conn = hiveconnect(host=self.host, port=self.port,
                                authMechanism=self.authMechanism, user=self.user,
                                password=self.password, database=self.database)
    def query(self, sql):
        if self.conn and sql:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                return True, data



    def __close(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception as ex:
            print('close hive connect failed.')

    def show(self):
        """
        show connection information
        """
        print(
            """
            Host    :%s
            Port    :%d
            User    :%s
            Password:%s
            DataBase:%s
            """ %(self.host, int(self.port), self.user, self.password, self.database)
        )


    def __del__(self):
        self.__close()
