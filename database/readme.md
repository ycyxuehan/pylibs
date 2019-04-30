database
=====================
- 简介

    database是一个数据库管理库的集合

- dbmanager

    dbmanager 目前支持Oracle(需要客户端支持)，impala， SQL server， MySQL四种数据库

    使用方法：

        创建对象： mysql = MySQL(host, port, user, passwd, database)
        执行SQL： res, data = mysql.query(sql)
                 res表示查询是否成功，data为查询结果。

        创建对象： mssql = MSSQL(host, port, user, passwd, database)
        执行SQL： res, data = mssql.query(sql)
                 res表示查询是否成功，data为查询结果。

        创建对象： oracle = ORACLE(host, port, user, passwd, database)
        执行SQL： res, data = oracle.query(sql)
                 res表示查询是否成功，data为查询结果。

        创建对象： impala = IMPALA(host, backuphost, port, database)
        执行SQL： res, data = impala.query(sql)
                 res表示查询是否成功，data为查询结果。
     
