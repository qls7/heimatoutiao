import socketio

# JWT 秘钥
JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'

# 2. 创建服务器对象
sio = socketio.Server(async_mode='eventlet')

# 3. 创建应用
app = socketio.Middleware(sio)