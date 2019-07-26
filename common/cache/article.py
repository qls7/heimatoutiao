import pickle

from flask import current_app
from flask_restful import fields, marshal
from redis import RedisError
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import load_only

from cache import constants, statistic
from cache.user import UserProfileCache
from models.news import Article


class ArticleInfoCache(object):
    """
    文章基本信息缓存
    'art:文章id:info' '{'title': 'xx', 'create_time': xx , ...}'
    """

    # 定义需要序列化的字段
    article_info_fields_db = {
        'title': fields.String(attribute='title'),
        'aut_id': fields.Integer(attribute='user_id'),
        'pubdate': fields.DateTime(attribute='ctime', dt_format='iso8601'),
        'ch_id': fields.Integer(attribute='channel_id')
    }

    def __init__(self, article_id):
        self.key = 'art:{}:info'.format(article_id)
        self.article_id = article_id
        self.rc = current_app.redis_cluster

    def save(self):
        """
        数据库中查询数据, 保存缓存层, 并返回
        :return:
        """
        try:
            article = Article.query.options(load_only(Article.id, Article.title, Article.user_id, Article.channel_id,
                                        Article.cover, Article.ctime)).filter(Article.status == Article.STATUS.APPROVED,
                                                                              Article.id == self.article_id).first()
        except DatabaseError as e:
            current_app.logger.error(e)
            raise e
        if article:
            # 先序列化 再进行写入到缓存
            article_dict = marshal(article, self.article_info_fields_db)
            article_dict['cover'] = article.cover
            try:
                self.rc.setex(self.key, constants.ArticleInfoCacheTTL.get_val(), pickle.dumps(article_dict))
            except RedisError as e:
                current_app.loggeNr.error(e)
            return article_dict
        else:
            # 防止缓存穿透, 设置默认值
            self.rc.setex(self.key, constants.ArticleNotExistsCacheTTL.get_val(), -1)
            return None

    def _fill_fields(self, article_dict):
        """
        补充字段
        :param article_dict:
        :return:
        """
        article_dict['art_id'] = self.article_id  # 文章id
        # 获取作者名
        author = UserProfileCache(article_dict['art_id']).get()
        article_dict['aut_name'] = author.get('name')
        article_dict['comm_count'] = statistic.ArticleCommentCountStorage.get(article_dict['art_id'])
        return article_dict

    def get(self):
        """
        从缓存中获取文章基本信息
        :return: {}
        """
        try:
            article_info = self.rc.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            article_info = None

        if article_info:
            if article_info == b'-1':
                return None
            else:
                return pickle.loads(article_info)

        # 数据库进行查询
        article_dict = self.save()
        if not article_dict:
            return None
        article_dict = self._fill_fields(article_dict)
        # del article_dict['allow_comm']

        return article_dict

    def exist(self):
        """
        判断文章详情信息是否存在
        :return: bool
        """
        # 此处可以使用的键有三种选择 user:{}:profile 或 user:{}:status 或新建
        # status主要为当前登录用户, 而profile不仅仅是登录用户, 覆盖范围更大, 所以使用profile
        try:
            article_info = self.rc.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            article_info = None

        if article_info:
            if article_info == b'-1':
                return False
            else:
                return True

        # 数据库进行查询
        if self.save():
            return True
        else:
            return False

    def clear(self):
        """
        清空缓存
        :return:
        """
        try:
            self.rc.delete(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            raise e