from flask import Flask

from utils import limiter
from utils.converters import register_converters
from utils.logging import create_logger


def create_flask_app(config, enable_config_file=False):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config)
    if enable_config_file:
        from utils import constants
        # 加载隐私配置
        app.config.from_envvar(constants.GLOBAL_SETTING_ENV_NAME, slient=True)

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
    register_converters(app)

    # TODO 创建redis哨兵

    # 配置日志
    create_logger(app)

    # 限流器
    limiter.limiter.init_app(app)

