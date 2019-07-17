from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm

from models.db_routing.session import RoutingSession


class RoutingSQLAlchemy(SQLAlchemy):
    """自定义可以读写分离的sqlalchemy"""

    def init_app(self, app):
        config_binds = app.config.get('SQLALCHEMY_BINDS')
        if not config_binds:
            raise RuntimeError('Missing SQLALCHEMY_BINDS config')

        cluster = app.config.get('SQLALCHEMY_CLUSTER')
        if not cluster:
            raise RuntimeError('Missing SQLALCHEMY_CLUSTER config')

        default_key = cluster.get('default')
        if not default_key:
            raise KeyError('deafult is not in SQLALCHEMY_CLUSTER')

        # 生成并保存数据库引擎
        self.master_keys = cluster.get('masters') or []
        self.slave_keys = cluster.get('slaves') or []
        self.default_key = default_key
        # 调用父类的init_app
        super(RoutingSQLAlchemy, self).init_app(app)

    def create_session(self, options):
        return orm.sessionmaker(class_=RoutingSession, db=self, **options)
