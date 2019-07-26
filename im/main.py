import os
import sys

# 获取项目的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 添加common文件夹到查询路径
sys.path.insert(0, os.path.join(BASE_DIR, 'im'))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))

from eventlet import monkey_patch
import eventlet.wsgi  # eventlet是一个协程库, 其中提供了服务器, 而且该服务器支持websocket协议

from server import app
from chat import *  # 注意一定要把监听事件关联, 不然不会有监听事件的发生
from notify import *

# 1. monkey_patch()  # 打补丁, 把所有的io操作进行了重写, 把默认的同步处理改为异步任务
monkey_patch()

if len(sys.argv) < 2:
    print('Usage: python main.py [port]')
    exit(1)

port = int(sys.argv[1])

# 4. 监听端口
socket = eventlet.listen(('', port))

# 5. 启动服务器
eventlet.wsgi.server(socket, app)
