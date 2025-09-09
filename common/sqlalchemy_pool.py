from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from common.config_loader import GLOBAL_CONFIG

global sqlalchemy_pool, SQLAlchemySessionLocal, SQLAlchemyBase


class SQLAlchemyPool:
    _instance = None
    _initialized = False
    engine = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SQLAlchemyPool, cls).__new__(cls)
        return cls._instance

    def __init__(self, database_url=None, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800,
                 pool_pre_ping=True):
        if self._initialized:
            return

        # 创建引擎并配置连接池
        self.engine = create_engine(
            database_url,
            pool_size=pool_size,  # 连接池的大小
            max_overflow=max_overflow,  # 连接池中可以溢出的连接数量
            pool_timeout=pool_timeout,  # 等待连接池中连接的超时时间（秒）
            pool_recycle=pool_recycle,  # 连接池中连接的回收时间（秒）
            pool_pre_ping=pool_pre_ping  # 启用连接池的预检测功能
        )

        self._initialized = True


def init_sqlalchemy_pool():
    params = GLOBAL_CONFIG['mysql']
    db_url = f"mysql+pymysql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['db']}"
    global sqlalchemy_pool, SQLAlchemySessionLocal, SQLAlchemyBase
    sqlalchemy_pool = SQLAlchemyPool(database_url=db_url, pool_size=params['max_connections'])
    # 创建数据库会话
    SQLAlchemySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlalchemy_pool.engine)
    SQLAlchemyBase = declarative_base()
