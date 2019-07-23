from flask import current_app
from redis import RedisError
from sqlalchemy import func

from models import db
from models.news import Article, Comment
from models.user import Relation


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

    @classmethod
    def reset(cls, db_query_ret):
        """
        重置对应的数据集
        :data: 数据集合
        :return:
        """
        # 删除redis中的值
        pipe = current_app.redis_master.pipeline(transaction=False)
        pipe.delete(cls.key)
        # 重新写入redis
        for user_id, count in db_query_ret:
            pipe.zadd(cls.key, count, user_id)

        pipe.execute()


class UserArticleCountStorage(BaseCountStorage):
    """
    用户作品数量统计类

    count: user: arts zset [{value: 用户id, score: 作品数}, {}]
    """

    key = 'count:user:arts'

    @classmethod
    def get_query(cls):
        """
        获取需要操作的数据集合
        :return: 数据集合
        """
        # 查询数据库库中对应的值
        return db.session.query(Article.user_id, func.count(Article.id)).\
            filter(Article.status == Article.STATUS.APPROVED).group_by(Article.user_id).all()


class UserFollowingsCountStorage(BaseCountStorage):
    """
    用户关注数量统计类

    count: user: followings zset [{value: 用户id, score: 关注数}, {}]
    """

    key = 'count:user:followings'

    @classmethod
    def get_query(cls):
        """
        获取需要操作的数据集合
        :return: 数据集合
        """
        # 查询数据库库中对应的值
        return db.session.query(Relation.user_id, func.count(Relation.id)).\
            filter(Relation.relation == Relation.RELATION.FOLLOW).group_by(Relation.user_id).all()


class UserFansCountStorage(BaseCountStorage):
    """
    用户粉丝数量统计类

    count: user: fans zset [{value: 用户id, score: 粉丝数}, {}]
    """

    key = 'count:user:fans'

    @classmethod
    def get_query(cls):
        """
        获取需要操作的数据集合
        :return: 数据集合
        """
        # 查询数据库库中对应的值
        return db.session.query(Relation.target_user_id, func.count(Relation.id)).\
            filter(Relation.relation == Relation.RELATION.FOLLOW).group_by(Relation.target_user_id).all()


class ArticleCommentCountStorage(BaseCountStorage):
    """
    文章评论数量
    """
    key = 'count:art:comm'

    @staticmethod
    def db_query():
        return db.session.query(Comment.article_id, func.count(Comment.id)).\
            filter(Comment.status == Comment.STATUS.APPROVED).group_by(Comment.article_id).all()