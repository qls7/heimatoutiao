import os
import sys

# 获取项目的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 添加common文件夹到查询路径
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))

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

    # 创建redis集群
    from rediscluster import StrictRedisCluster
    app.redis_cluster = StrictRedisCluster(startup_nodes=app.config['REDIS_CLUSTER'])

    # 配置mysql数据库
    from models import db
    db.init_app(app)

    # 配置日志
    from utils.logging import create_logger
    create_logger(app)

    # 限流器
    from utils import limiter
    limiter.limiter.init_app(app)

    # 创建snowflake ID worker
    from utils.snowflake.id_worker import IdWorker
    app.id_worker = IdWorker(app.config['DATACENTER_ID'],
                             app.config['WORKER_ID'],
                             app.config['SEQUENCE'])

    # 添加定时任务
    from apscheduler.executors.pool import ThreadPoolExecutor
    from apscheduler.schedulers.background import BackgroundScheduler
    executor = ThreadPoolExecutor(max_workers=3)
    executors = {
        'default': executor
    }
    app.scheduler = BackgroundScheduler(executors=executors)
    # 添加任务 每天3点校正数据
    from schedule.schedule import fix_statistic
    # app.scheduler.add_job(fix_statistic, 'cron', hour=3, args=[app])
    # date 只用于测试
    app.scheduler.add_job(fix_statistic, 'date', args=[app])
    app.scheduler.start()

    # 创建推荐系统的rpc连接
    import grpc
    app.rpc_reco = grpc.insecure_channel(app.config['RPC'].RECOMMEND)

    # 创建请求钩子
    from utils.middlewares import jwt_authentication
    app.before_request(jwt_authentication)

    # 注册用户蓝图模块
    from .resources.user import user_bp
    app.register_blueprint(user_bp)

    # 注册搜索模块蓝图
    from .resources.search import search_bp
    app.register_blueprint(search_bp)

    # 注册文章蓝图
    from toutiao.resources.news import news_bp
    app.register_blueprint(news_bp)

    return app
