from flask_sqlalchemy import SQLAlchemy

# 创建数据库连接对象
# db = SQLAlchemy()
# 使用自己创建的sqlalchemy
from .db_routing.routing_sqlalchemy import RoutingSQLAlchemy

db = RoutingSQLAlchemy()