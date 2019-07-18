import random

from flask_sqlalchemy import SignallingSession, get_state


class RoutingSession(SignallingSession):

    def __init__(self, db, autocommit=False, autoflush=True, **options):

        SignallingSession.__init__(self, db, autocommit=autocommit, autoflush=autoflush, **options)
        self.master_keys = db.master_keys if len(db.master_keys) else self.default_key
        self.slave_keys = db.master_keys if len(db.slave_keys) else self.default_key
        self.default_key = db.default_key
        self.bind_key = None

    def get_bind(self, mapper=None, clause=None):
        """获取会话使用的数据库连接engine"""
        state = get_state(self.app)

        if self.bind_key:
            # 指定使用的引擎
            print('Using DB bind: _name={}'.format(self.bind_key))
            return state.db.get_engine(self.app, bind=self.bind_key)
        else:
            # 默认数据库
            print('Using DB bind: _name={}'.format(self.default_key))
            return state.db.get_engine(self.app, bind=self.default_key)

    def set_to_write(self):
        """使用写数据库"""
        self.bind_key = random.choice(self.master_keys)

    def set_to_read(self):
        """使用读数据库"""
        self.bind_key = random.choice(self.slave_keys)


