import socketio

# JWT 秘钥
JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'

# 创建消息队列地址
RABBITMQ = 'amqp://guest:guest@127.0.0.1:5672'

# 创建消息队列管理器
mgr = socketio.KombuManager(RABBITMQ)

# 2. 创建服务器对象 设置client_manage参数后, im服务器就会从消息队列中取出消息, 发给指定的房间
sio = socketio.Server(async_mode='eventlet', client_manager=mgr)

# 3. 创建应用
app = socketio.Middleware(sio)