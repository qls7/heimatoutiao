from functools import wraps

from flask import g

from models import db


def set_db_to_read(func):
    """设置使用读数据库"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        db.session().set_to_read()
        return func(*args, **kwargs)

    return wrapper


def set_db_to_write(func):
    """设置使用写数据库"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        db.session().set_to_write()
        return func(*args, **kwargs)

    return wrapper


def login_required(f):
    """判断用户是否登录"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        # 如果用户已经登录, 并且发送的是访问token, 允许访问视图
        if g.user_id and g.is_refresh == False:
            return f(*args, **kwargs)
        else:  # 返回状态码401 说明未认证
            return {'message': 'Invalid jwt'}, 401

    return wrapper
