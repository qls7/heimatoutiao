from flask import request, g

from .jwt_util import verify_jwt


def jwt_authentication():
    """认证jwt"""
    # 钩子函数只做取值操作, 逻辑交给视图处理
    # 取出token
    header = request.headers.get('Authorization')
    # 使用上下文变量进行记录用户登录的id 和刷新令牌
    g.user_id = None
    g.is_refresh = False
    if header and header.startswith('Bearer '):
        # 如果格式正确进行截取 获取token的值
        token = header[7:]
        # 认证token
        payload = verify_jwt(token)
        if payload:
            g.user_id = payload.get('payload')
            g.is_refresh = payload.get('is_refresh')