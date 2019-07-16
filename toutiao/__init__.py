from flask import Flask


def create_flask_app(config, enable_config_file=False):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config)
    if enable_config_file:
        from utils import constants
        # 加载隐私配置
        app.config.from_envvar(constants.GLOBAL_SETTING_ENV_NAME, silent=True)

    return app


def create_app(config, enable_config_file=False):
    """
    创建flask应用 并初始化各组件
    :param config: 配置类
    :param enable_config_file: 是否允许运行环境变量
    :return: flask应用
    """
    app = create_flask_app(config, enable_config_file)

    # 添加自定义正则转换器
    from utils.converters import register_converters
    register_converters(app)

    # 创建redis哨兵
    from redis.sentinel import Sentinel
    _sentinel = Sentinel(app.config['REDIS_SENTINELS'])
    # 获取redis主从连接对象
    app.redis_master = _sentinel.master_for(app.config['REDIS_SENTINEL_SERVICE_NAME'])
    app.redis_slave = _sentinel.slave_for(app.config['REDIS_SENTINEL_SERVICE_NAME'])

    # 配置mysql数据库
    from models import db
    db.init_app(app)

    # 配置日志
    from utils.logging import create_logger
    create_logger(app)

    # 限流器
    from utils import limiter
    limiter.limiter.init_app(app)

    # 注册用户蓝图模块
    from .resources.user import user_bp
    app.register_blueprint(user_bp)

    # 注册搜索模块蓝图
    from .resources.search import search_bp
    app.register_blueprint(search_bp)

    return app
