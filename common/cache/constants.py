import random


class BaseCacheTTL:
    """过期时间基类"""
    TTL = 2 * 60 * 60  # 有效期
    MAX_DELTA = 10 * 60  # 有效期的最大随机值 防止缓存雪崩

    @classmethod
    def get_val(cls):
        return cls.TTL + random.randint(0, cls.MAX_DELTA)


class UserProfileCacheTTL(BaseCacheTTL):
    """用户缓存的过期时间类"""
    pass


class UserNotExistCacheTTL(BaseCacheTTL):
    """用户缓存不存在的过期时间类"""
    TTL = 10 * 60
    MAX_DELTA = 1 * 60


class ArticleCacheTTL(BaseCacheTTL):
    """文章缓存的时间类"""
    TTL = 5 * 60 * 60
    MAX_DELTA = 20 * 60