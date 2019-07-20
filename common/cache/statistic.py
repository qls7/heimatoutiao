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
        pass

    @classmethod
    def incr(cls, user_id):
        """
        更新用户作品数量
        :return:
        """
        pass
