from flask import current_app
from redis import RedisError


class BaseCountStorage:
    """数据统计的基类"""

    key = ''  # 设置键

    @classmethod
    def get(cls, user_id):
        """
        获取指定用户的统计量
        :return: 数量
        """
        try:
            count = current_app.redis_slave.zscore(cls.key, user_id)
        except RedisError as e:
            current_app.logger.error(e)
            raise e

        if count:
            return int(count) if int(count) > 0 else 0  # 防止count值为负数
        else:
            return 0

    @classmethod
    def incr(cls, user_id):
        """
        更新用户指定的统计量
        :return: None
        """
        try:
            current_app.redis_master.zincrby(cls.key, user_id)
        except RedisError as e:
            current_app.logger.error(e)
            raise e


class UserArticleCountStorage(BaseCountStorage):
    """
    用户作品数量统计类

    count: user: arts zset [{value: 用户id, score: 作品数}, {}]
    """

    key = 'count:user:arts'


class UserFollowingsCountStorage(BaseCountStorage):
    """
    用户关注数量统计类

    count: user: followings zset [{value: 用户id, score: 作品数}, {}]
    """

    key = 'count:user:followings'


class UserFansCountStorage(BaseCountStorage):
    """
    用户粉丝数量统计类

    count: user: fans zset [{value: 用户id, score: 作品数}, {}]
    """

    key = 'count:user:fans'

