import pickle

from flask import current_app
from redis import RedisError
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import load_only

from cache import constants
from models.news import Channel


class AllChannelsCache(object):
    """
    全部频道的缓存
    'channel:all' '[{'id':1, 'name':'金融'},{}]'  -----结构化字符串进行存储
    """
    key = 'channel:all'

    @classmethod
    def get(cls):
        """
        获取所有的频道
        :return:
        """
        try:
            channels = current_app.redis_cluster.get(cls.key)
        except RedisError as e:
            current_app.logger.error(e)
            channels = None

        if channels:
            if channels == b'-1':
                return None
            else:
                return pickle.loads(channels)  # loads 下载, 将json存储结构转换成对象结构, dumps 抛弃, 将对象格式转为json

        else:
            # 数据库查询
            channel_list = []
            try:
                channels = Channel.query.option(load_only(Channel.name, Channel.id)).\
                    filter(Channel.is_visible == True).order_by(Channel.sequence, Channel.id).all()
            except DatabaseError as e:
                current_app.logger.error(e)
                raise e
            if channels:
                for channel in channels:
                    channel_list.append({
                        'id': channel.id,
                        'name': channel.name
                    })
                # 写入缓存
                try:
                    current_app.redis_cluster.setex(cls.key, constants.ALL_CHANNELS_CACHE_TTL, pickle.dumps(channel_list))
                except RedisError as e:
                    current_app.logger.error(e)

            else:
                # 防止缓存穿透
                current_app.redis_cluster.setex(cls.key, constants.UserNotExistCacheTTL, -1)

            return channel_list

    @classmethod
    def exist(cls, channel_id):
        """
        判断channel_id是否存在
        :param channel_id: 频道id
        :return: bool
        """
        channel_list = cls.get()

        if channel_list and channel_list != b'-1':
            for channel in channel_list:
                if channel_id in channel:
                    return True
            return False
        else:
            return False



