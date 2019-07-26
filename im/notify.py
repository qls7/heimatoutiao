from flask import Request

from server import sio, JWT_SECRET
from utils.jwt_util import verify_jwt


def check_token(token):
    """
    校验token的值
    :param token:
    :return:
    """
    payload = verify_jwt(token, secret=JWT_SECRET)
    if payload:
        return payload.get('payload')
    else:
        return


@sio.on('connect')
def connect(sid, environ):
    request = Request(environ)
    token = request.args.get('token')
    # 解析token
    user_id = check_token(token)
    # 一但建立连接, 让其进入指定user_id 的房间
    sio.enter_room(sid, room=user_id)


@sio.on('disconnect')
def connect(sid):
    # 一单断开连接, 马上退出当前所在的所有房间
    rooms = sio.rooms()
    # 关闭所有的房间, 并离开
    for room in rooms:
        sio.leave_room(sid, room)
        sio.close_room(room)


@sio.on('message')
def message(sid, data):
    """
    监听message事件, 一单有通知就往房间里面发送
    :param sid:
    :param data:
    :return:
    """
    pass
