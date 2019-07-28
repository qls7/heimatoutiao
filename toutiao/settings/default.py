class DefaultConfig(object):
    """
    Flask 默认配置
    """
    # 添加哨兵
    REDIS_SENTINELS = [
        ('127.0.0.1', '26379'),
        ('127.0.0.1', '26378'),
        ('127.0.0.1', '26377'),
    ]
    REDIS_SENTINEL_SERVICE_NAME = 'mymaster'

    # redis 集群
    REDIS_CLUSTER = [
        {'host': '127.0.0.1', 'port': '6380'},
        {'host': '127.0.0.1', 'port': '6381'},
        {'host': '127.0.0.1', 'port': '6382'},
    ]

    # 日志
    LOGGING_LEVEL = 'DEBUG'
    LOGGING_FILE_DIR = '/home/python/logs'
    LOGGING_FILE_MAX_BYTES = 300 * 1024 * 1024
    LOGGING_FILE_BACKUP = 10
    PROPAGATE_EXCEPTIONS = True  # 设置为False, 则flask内置日志会写入文件, 但错误信息将不会显示到网页上

    # sqlalchemy的配置
    # SQLALCHEMY_DATA_URI = 'mysql://root:mysql@127.0.0.1:3306/toutiao'

    SQLALCHEMY_BINDS = {
        'master1': 'mysql://root:mysql@127.0.0.1:3306/toutiao',
        'master2': 'mysql://root:mysql@127.0.0.1:3306/toutiao',
        'slave1': 'mysql://root:mysql@127.0.0.1:8306/toutiao',
        'slave2': 'mysql://root:mysql@127.0.0.1:8306/toutiao',
    }
    SQLALCHEMY_CLUSTER = {
        'masters': ['master1', 'master2'],
        'slaves': ['slave1', 'slave2'],
        'default': 'master1'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追踪数据的修改信号
    SQLALCHEMY_ECHO = False  # 打印底层sql语句

    # Snowflake ID Worker 参数
    DATACENTER_ID = 0
    WORKER_ID = 0
    SEQUENCE = 0

    # jwt
    JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA' #  消息认证的秘钥
    JWT_EXPIRY_HOURS = 2  # 访问token的过期时间
    JWT_REFRESH_DAYS = 14  # 刷新token的过期时间

    # 七牛云
    QINIU_ACCESS_KEY = 'kJ8wVO7lmFGsdvtI5M7eQDEJ1eT3Vrygb4SmR00E'
    QINIU_SECRET_KEY = 'rGwHyAvnlLK7rU4htRpNYzpuz0OHJKzX2O1LWTNl'
    QINIU_BUCKET_NAME = 'sh26'  # 存储空间的名字
    QINIU_DOMAIN = 'http://puk2zync7.bkt.clouddn.com/'  # 存储图片的域名

    # rpc
    class RPC:
        RECOMMEND = '127.0.0.1:8888'
        CHATBOT = '127.0.0.1:9999'

    # 消息队列的连接地址
    RABBITMQ = 'amqp://guest:guest@127.0.0.1:5672'

    # elasticsearch集群服务器的地址
    ES = [
        '127.0.0.1:9200'
    ]


class TestingConfig(DefaultConfig):
    TESTING = True  # 如果进行单元测试, 建议设置为True, 一但开启, 会停用所有flask内部的异常捕获(这样会精确定位到错误位置)
