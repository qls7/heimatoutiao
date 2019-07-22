from flask import current_app
from cache.statistic import UserArticleCountStorage, UserFollowingsCountStorage, UserFansCountStorage
from utils.decorators import set_db_to_read


def __fix_statistic(cls):
    try:
        # 先得到查询集
        ret = cls.get_query()
        # 校正数据
        cls.reset(ret)
    except BaseException as e:
        current_app.logger.error(e)
        raise e


def fix_statistic(app):
    """
    修正统计数据
    :param app: 把app应用传过来
    :return: None
    """
    # 使用with语句 引入上下文变量current_app
    with app.app_context():

        # 校正所有的用户作品数量
        __fix_statistic(UserArticleCountStorage)
        # 校正所用用户的关注数量
        __fix_statistic(UserFollowingsCountStorage)
        # 校正所有用户的粉丝数量
        __fix_statistic(UserFansCountStorage)
