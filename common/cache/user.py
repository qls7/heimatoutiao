import pickle

from flask import current_app, g
from redis import RedisError
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import load_only

from cache import constants
from cache.constants import UserNotExistCacheTTL, UserProfileCacheTTL
from cache.statistic import UserFollowingsCountStorage
from models.user import User, Relation


class UserProfileCache(object):
    """
    用户基本信息缓存类,每个缓存对象,对应一套用户缓存数据
    'user:user_id:profile' '{'name': 'zs', 'photo': '图片地址', ....}'
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
            return self.save()

    def clear(self):
        """清空缓存"""
        try:
            self.cluster.delete(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            raise e

    def exist(self):
        """判断数据是否存在"""
        try:
            user_data = self.cluster.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            user_data = None

        if user_data:
            if user_data == b'-1':
                return False
            else:
                return True
        else:
            user_dict = self.save()
            if user_dict:
                return True
            else:
                return False

    def save(self):
        """不存在的情况下去数据库查询, 并保存到缓存"""
        # 未击中缓存,去mysql数据库查询
        # 使用悲观锁实现缓存更新的问题, 查之前先进行判断是否有人在更新
        # 使用乐观锁进行判断是否有在更新的数据
        lock_key = 'user:{}:profile:update'.format(g.user_id)
        while True:
            # lock = self.cluster.setnx(lock_key, 1)
            lock = self.cluster.get(lock_key)
            if lock == 0:
                # self.cluster.expire(lock_key, 1)
                try:
                    user = User.query.options(load_only(User.name, User.mobile,
                                                        User.profile_photo, User.certificate,
                                                        User.introduction)).filter(User.id == self.user_id).first()
                except DatabaseError as e:
                    current_app.logger.error(e)
                    # self.cluster.delete(lock_key)
                    raise e
                # 防止缓存穿透
                if not user:
                    try:
                        self.cluster.setex(self.key, UserNotExistCacheTTL.get_val(), -1)
                    except RecursionError as e:
                        current_app.logger.error(e)
                    # self.cluster.delete(lock_key)
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
                # self.cluster.delete(lock_key)
                return user_dict


class UserFollowingCache(object):
    """
    获取用户的关注列表
    'user:user_id:following' [{target_id1, score}, {target_id2, score}, ...]
    """
    def __init__(self, user_id):
        self.user_id = user_id  # 用户id
        self.key = 'user:{}:following'.format(self.user_id)
        self.rc = current_app.redis_cluster

    def get(self):
        """获取缓存数据"""
        try:
            target_id_list = self.rc.zrange(self.key, 0, -1)  # 返回的是target_id是一个列表
        except RedisError as e:
            current_app.logger.error(e)
            target_id_list = None

        if target_id_list:
            return [int(uid) for uid in target_id_list]  # 把列表中的二进制进行转换成整型

        target_id_count = UserFollowingsCountStorage.get(self.user_id)  # 判断redis持久化中是否有关注的, 如果为0, 就直接
        if target_id_count == 0:
            return []
        # 数据库中查询要的缓存数据
        ret = Relation.query.options(load_only(Relation.target_user_id, Relation.utime)).\
            filter(Relation.relation == Relation.RELATION.FOLLOW, Relation.user_id == self.user_id).\
            order_by(Relation.utime.desc()).all()
        target_id_list = []
        cache = []  # 列表中的值直接就是要插入zset的顺序, 直接进行解包进行输入
        # 将缓存数据存储到redis集群中
        for target_id in ret:
            target_id_list.append(target_id.target_user_id)  # 将user_target_id存到id列表中
            cache.append(target_id.utime.timestamp())
            cache.append(target_id.target_user_id)
        if cache:
            try:
                pl = self.rc.pipeline()
                pl.zadd(self.key, *cache)  # 直接进行解包进行添加zset的值
                pl.expire(self.key, constants.UserFollowingsCacheTTL.get_val())
                results = pl.execute()  # 返回的类型 result:[3, True]
                if results[0] and not results[1]:  # 如果返回的数据失败就直接删除缓存
                    self.rc.delete(self.key)
            except RedisError as e:
                current_app.logger.error(e)

        return target_id_list  # 返回用户的关注列表

