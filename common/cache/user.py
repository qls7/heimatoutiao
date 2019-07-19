class UserProfileCache(object):
    """
    用户基本信息缓存类,每个缓存对象,对应一套用户缓存数据
    """
    def __init__(self, user_id):
        self.user_id = user_id  # 用户id
        self.key = 'user:{}:profile'.format(self.user_id)  # redis中存储的键

    def get(self):
        """获取缓存数据"""
        pass

    def clear(self):
        """清空缓存"""
        pass
