from flask import current_app
from redis import RedisError


class UserArticleCountStorage:
    """
    用户作品数量统计类
    count: user: arts zset [{value: 用户id, score: 作品数}, {}]
    """
    key = 'count:user:arts'  # 设置键

    @classmethod
    def get(cls, user_id):
        """
        获取指定用户的作品数量
        :return: 作品数量
        """
        try:
            count = current_app.redis_slave.zscore(cls.key, user_id)
        except RedisError as e:
            current_app.logger.error(e)
            raise e

        if int(count) > 0:
            return count
        else:
            return 0

    @classmethod
    def incr(cls, user_id):
        """
        更新用户作品数量
        :return: None
        """
        try:
            current_app.redis_master.zincrby(cls.key, user_id)
        except RedisError as e:
            current_app.logger.error(e)
            raise e
