import pymysql
from dbutils.pooled_db import PooledDB

from common.config_loader import GLOBAL_CONFIG

global mysql_pool


class MySQLPool:
    _instance = None
    _initialized = False
    pool = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MySQLPool, cls).__new__(cls)
        return cls._instance

    def __init__(self, creator=pymysql, host='localhost', port=3306, user='root', password=None, database=None,
                 max_connections=100, blocking=True, ping=0, autocommit=True):
        if self._initialized:
            return

        self.pool = PooledDB(
            creator=creator,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            maxconnections=max_connections,
            blocking=blocking,
            ping=ping,
            autocommit=autocommit
        )
        self._initialized = True

    def execute(self, sql):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor()
            result = cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            conn.rollback()
            print(f"execute db error: {repr(e)}")

    def execute_with_params(self, sql, params):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor()
            result = cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            conn.rollback()
            print(f"execute db error: {repr(e)}")

    def insert(self, sql):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor()
            result = cursor.execute(sql)
            last_id = cursor.connection.insert_id()
            conn.commit()
            cursor.close()
            conn.close()
            return result, last_id
        except Exception as e:
            conn.rollback()
            print(f"insert db error: {repr(e)}")

    def insert_with_params(self, sql, params):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor()
            result = cursor.execute(sql, params)
            last_id = cursor.connection.insert_id()
            conn.commit()
            cursor.close()
            conn.close()
            return result, last_id
        except Exception as e:
            conn.rollback()
            print(f"insert db error: {repr(e)}")
    
    async def insert_many_with_params(self, sql, params):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor()
            result = cursor.executemany(sql, params)
            last_id = cursor.connection.insert_id()
            conn.commit()
            cursor.close()
            conn.close()
            return result, last_id
        except Exception as e:
            conn.rollback()
            print(f"insert db error: {repr(e)}")
            return None, None
        
    def query(self, sql):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            return cursor.fetchall()
        except pymysql.Error as e:
            conn.rollback()
            print(f"query db error: {repr(e)}")

    def query_with_params(self, sql, params):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            conn.close()
            return cursor.fetchall()  # 返回二维元组
        except pymysql.Error as e:
            conn.rollback()
            print(f"query db error: {repr(e)}")

    def query_with_params_return_dict(self, sql, params):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            conn.close()
            return cursor.fetchall()
        except pymysql.Error as e:
            conn.rollback()
            print(f"query db error: {repr(e)}")

    def query_one_with_params_return_dict(self, sql, params):
        conn = self.pool.connection()
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            conn.close()
            return cursor.fetchone()
        except pymysql.Error as e:
            conn.rollback()
            print(f"query db error: {repr(e)}")


def init_pymysql_pool():
    params = GLOBAL_CONFIG['mysql']
    global mysql_pool
    mysql_pool = MySQLPool(host=params['host'], port=params['port'], user=params['user'], password=params['password'],
                           database=params['db'], max_connections=params['max_connections'])


def get_mysql_client():
    return mysql_pool
