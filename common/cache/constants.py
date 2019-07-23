import random

# 用户搜索历史每人保存数目
SEARCHING_HISTORY_COUNT_PER_USER = 4

# 全部频道缓存有效期，　秒
ALL_CHANNELS_CACHE_TTL = 24 * 60 * 60


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


class UserFansCacheTTL(BaseCacheTTL):
    """
    用户粉丝列表缓存时间, 秒
    """
    TTL = 30 * 60


class UserFollowingsCacheTTL(BaseCacheTTL):
    """
    用户关注列表缓存时间, 秒
    """
    TTL = 30 * 60


class ArticleInfoCacheTTL(BaseCacheTTL):
    """
    文章信息缓存时间, 秒
    """
    TTL = 30 * 60


class ArticleNotExistsCacheTTL(BaseCacheTTL):
    """
    文章不存在结果缓存
    为解决缓存击穿, 有效期不宜过长
    """
    TTL = 30 * 60
    MAX_DELTA = 60

