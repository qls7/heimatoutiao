import socketio


# 2. 创建服务器对象
sio = socketio.Server(async_mode='eventlet')

# 3. 创建应用
app = socketio.Middleware(sio)