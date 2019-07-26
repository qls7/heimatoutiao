from server import sio


# 1. 监听聊天事件
@sio.on('chat')
def message(sid, data):
    """
    聊天事件
    :param sid: 建立连接的唯一识别码, 每个连接对应一个socket_id
    :param data: 聊天的数据
    :return:
    """
    print(data)
    # TODO 将客户端的消息发送给AI聊天机器人, 并将响应数据返回给IM客户端 RPC
    response = '机器人的回复: xxxx'

    # 2. 给指定的客户端发送消息
    sio.emit('chat', response, room=sid)
