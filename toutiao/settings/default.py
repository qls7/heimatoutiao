class DefaultConfig(object):
    """
    Flask 默认配置
    """
    # TODO redis 哨兵

    # 日志
    LOGGING_LEVEL = 'DEBUG'
    LOGGING_FILE_DIR = '/home/python/logs'
    LOGGING_FILE_MAX_BYTES = 300 * 1024 * 1024
    LOGGING_FILE_BACKUP = 10
    PROPAGATE_EXCEPTIONS = True # 设置为False, 则flask内置日志会写入文件, 但错误信息将不会显示到网页上
