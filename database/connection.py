#
#
class DBConnection(object):
    """
        Class DBConnection:
            connect db
    """
    MYSQL = 1
    MSSQL = 2
    IMPALA = 3
    ORACLE = 4
    HIVE = 5
    ES = 6
    def __init__(self, **kwargs):
        """

        """
        self.host = kwargs.get('host', 'localhost')
        self.database = kwargs.get('database')
        self.engine = kwargs.get('engine', self.MYSQL)
        self.conn = None
        if self.engine is None or self.engine == self.MYSQL:
            self.user = kwargs.get('user')
            self.password = kwargs.get('password')
            self.charset = kwargs.get('charset', 'utf8')
            self.port = kwargs.get('port', 3306)
            if self.user and self.password:
                from pymysql import connect
                self.conn = connect(host=self.host, port=int(self.port),
                                    user=self.user, password=self.password,
                                    database=self.database, charset=self.charset)
        elif self.engine == self.MSSQL:
            self.user = kwargs.get('user')
            self.password = kwargs.get('password')
            self.charset = kwargs.get('charset', 'utf8')
            self.port = kwargs.get('port', 2521)
            if self.user and self.password:
                from pymssql import connect
                if not self.port:
                    self.port = 2521
                self.conn = connect(host=self.host, user=self.user,
                                    password=self.password, database=self.database,
                                    charset=self.charset)
        elif self.engine == self.IMPALA:
            self.backup_host = kwargs.get('backup')
            self.port = kwargs.get('port', 21050)
            if self.host:
                if not self.port:
                    self.port = 21050
                from impala.dbapi import connect
                try:
                    self.conn = connect(self.host, int(self.port), self.database)
                except Exception as ex:
                    if self.backup_host:
                        print('connect to server:%s failed, try the backup: %s' %(
                            self.host, self.backup_host))
                        try:
                            self.conn = connect(self.backup_host, int(self.port), self.database)
                        except Exception as ex:
                            raise ex
        elif self.engine == self.ORACLE:
            # self.user = kwargs.get('user')
            # self.password = kwargs.get('password')
            # self.charset = kwargs.get('charset', 'utf8')
            # self.instance = kwargs.get('instance')
            # self.port = kwargs.get('port', 1125)
            # from cx_Oracle import connect
            # self.connect_cmd = "%s/%s@%s:%s/%s" %(
            #     self.user,
            #     self.password,
            #     self.host,
            #     int(self.port),
            #     self.instance)
            # self.conn = connect(self.connect_cmd)
            pass
        elif self.engine == self.HIVE:
            # self.port = kwargs.get('port', 10000)
            # self.authMechanism = kwargs.get('authMechanism', 'PLAIN')
            # self.user = kwargs.get('user')
            # self.password = kwargs.get('password')
            # self.conn = connect(host=self.host, port=self.port,
            #                     authMechanism=self.authMechanism, user=self.user,
            #                     password=self.password, database=self.database)
            pass
        elif self.engine == self.ES:
            self.port = kwargs.get('port', 10000)
            from elasticsearch import Elasticsearch
            self.conn = Elasticsearch([{'host':self.host, 'port':self.port}])
        else:
            self.conn = None

    def query(self, sql):
        if sql and self.conn:
            try:
                data = None
                with self.conn.cursor() as cursor:
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    import re
                    if re.findall(r'[insert|update|delete]', sql.lower()):
                        self.conn.commit()
                return True, data
            except Exception as ex:
                raise ex
    def __del__(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception as ex:
                print(ex)
