import logging
import logging.handlers
import os

from datetime import datetime
from flask import request


class RequestFormatter(logging.Formatter):
    def format(self, record):
        """
        自定义格式化参数
        :param record: 日志信息
        :return:
        """
        record.url = request.url # 定义格式化参数url
        record.remote_addr = request.remote_addr # 定义格式花参数remote_addr
        return super().format(record)


def create_logger(app):
    """
    设置日志
    :param app: flask app 对象
    :return:
    """
    # 获取配置
    logging_file_dir = app.config['LOGGING_FILE_DIR']  # 日志文件目录
    logging_file_max_bytes = app.config['LOGGING_FILE_MAX_BYTES']  # 日志文件大小
    logging_file_backup = app.config['LOGGING_FILE_BACKUP']  # 日志文件数量
    logging_level = app.config['LOGGING_LEVEL']  # 日志级别

    # 自定义flask.app日志器
    flask_logger = logging.getLogger('flask.app')
    # 修改日志级别 默认是warning
    flask_logger.setLevel(logging_level)

    # 设置控制台输出处理器
    flask_console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('-' * 100 + '\n%(levelname)s %(pathname)s, %(lineno)d: %(message)s\n' + '-' * 100)
    flask_console_handler.setFormatter(console_formatter)

    # 设置文件输出处理器
    flask_file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(logging_file_dir, 'flask.log'),
        maxBytes=logging_file_max_bytes,
        backupCount=logging_file_backup
    )

    file_formatter = RequestFormatter('[%(asctime)s] %(remote_addr)s requested %(url)s\n'
                                      '%(levelname)s   in %(pathname)s, %(lineno)d: %(message)s')

    flask_file_handler.setFormatter(file_formatter)
    flask_file_handler.setLevel(logging.ERROR)

    """限流日志"""
    # 设置限流日志器 flask-limiter组件会自动使用名为flask-limiter日志器进行日志输出
    limit_logger = logging.getLogger('flask-limiter')
    limit_logger.setLevel(logging_level)

    # 设置限流日志-文件输出处理器
    limit_file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(logging_file_dir, 'limit.log'),
        maxBytes=logging_file_max_bytes,
        backupCount=logging_file_backup
    )
    limit_file_handler.setFormatter(file_formatter)

    # 添加处理器
    flask_logger.addHandler(flask_file_handler)
    limit_logger.addHandler(limit_file_handler)

    # 埋点日志
    trace_file_handler = logging.FileHandler(
        os.path.join(logging_file_dir, 'userClick.log')
    )
    trace_file_handler.setFormatter(logging.Formatter('%(message)s'))
    log_trace = logging.getLogger('trace')
    log_trace.addHandler(trace_file_handler)
    log_trace.setLevel(logging.INFO)

    if app.debug:
        flask_logger.addHandler(flask_console_handler)
        limit_logger.addHandler(flask_console_handler)


def write_trace_log(param):
    """
    写埋点日志
    :param param: 埋点参数
    :return:
    """
    logger = logging.getLogger('trace')
    message = '{"readTime": "%s", "param": %s}' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), param)
    logger.info(message)