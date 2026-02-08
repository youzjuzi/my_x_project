# 数据库引用部分
import sys
import time

import pymysql
from dbutils.pooled_db import PooledDB
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH


# 数据库配置模块
class Config(object):
    # DEBUG = True
    # SECRET_KEY = "umsuldfsdflskjdf"
    # PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)
    # SESSION_REFRESH_EACH_REQUEST = True
    # SESSION_TYPE = "redis"
    PYMYSQL_POOL = PooledDB(
        creator=pymysql,  # 使用链接数据库的模块
        maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
        mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
        maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
        maxshared=3,
        # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
        blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
        maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
        setsession=[],  # 开始会话前执行的命令列表。
        ping=0,
        # ping MySQL服务端，检查是否服务可用。
        host='127.0.0.1',
        port=3306,
        user='root',
        password='123456',  # 自己的密码
        database='test',  # 提前建好库
        charset='utf8'
    )


# 数据库操作类
class SQLHelper(object):
    @staticmethod
    def open(cursor):
        POOL = Config.PYMYSQL_POOL
        conn = POOL.connection()
        cursor = conn.cursor(cursor=cursor)
        return conn, cursor

    @staticmethod
    def close(conn, cursor):
        conn.commit()
        cursor.close()
        conn.close()

    @classmethod
    def fetch_one(cls, sql, args, cursor=pymysql.cursors.DictCursor):
        conn, cursor = cls.open(cursor)
        cursor.execute(sql, args)
        obj = cursor.fetchone()
        cls.close(conn, cursor)
        return obj

    @classmethod
    def fetch_all(cls, sql, args, cursor=pymysql.cursors.DictCursor):
        conn, cursor = cls.open(cursor)
        cursor.execute(sql, args)
        obj = cursor.fetchall()
        cls.close(conn, cursor)
        return