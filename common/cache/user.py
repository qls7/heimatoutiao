import pickle

from flask import current_app
from redis import RedisError
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import load_only

from cache.constants import UserNotExistCacheTTL, UserProfileCacheTTL
from models.user import User


class UserProfileCache(object):
    """
    用户基本信息缓存类,每个缓存对象,对应一套用户缓存数据
    """
    def __init__(self, user_id):
        self.user_id = user_id  # 用户id
        self.key = 'user:{}:profile'.format(self.user_id)  # redis中存储的键
        self.cluster = current_app.redis_cluster

    def get(self):
        """获取缓存数据"""
        # 先进行获取缓存数据
        try:
            user_data = self.cluster.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            user_data = None

        if user_data:
            # 如果有数据进行判断是不是-1 防止缓存穿透设置的
            if user_data == b'-1':
                return None
            else:
                # 如果不是-1 直接进行返回
                return pickle.loads(user_data)
        else:
            # 未击中缓存,去mysql数据库查询
            try:
                user = User.query.options(load_only(User.name, User.mobile,
                                                User.profile_photo, User.certificate,
                                                User.introduction)).filter(id=self.user_id).first()
            except DatabaseError as e:
                current_app.logger.error(e)
                raise e
            # 防止缓存穿透
            if not user:
                try:
                    self.cluster.setex(self.key, UserNotExistCacheTTL.get_val(), -1)
                except RecursionError as e:
                    current_app.logger.error(e)
                return None

            user_dict = {
                'name': user.name,
                'mobile': user.mobile,
                'profile_photo': user.profile_photo,
                'certificate': user.certificate,
                'introduction': user.introduction,
            }
            user_str = pickle.dumps(user_dict)
            # 保存到缓存
            try:
                self.cluster.setex(self.key, UserProfileCacheTTL.get_val(), user_str)
            except RecursionError as e:
                current_app.logger.error(e)

            # 进行返回
            return user_dict

    def clear(self):
        """清空缓存"""
        try:
            self.cluster.delete(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            raise e
