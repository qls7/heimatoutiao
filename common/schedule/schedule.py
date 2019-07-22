from flask import current_app
from sqlalchemy import func
from sqlalchemy.exc import DatabaseError

from models import db
from models.news import Article
from utils.decorators import set_db_to_read


@set_db_to_read
def fix_statistic(app):
    """
    修正统计数据
    :param app: 把app应用传过来
    :return: None
    """
    # 使用with语句 引入上下文变量current_app
    with app.app_context():
        # 查询数据库库中对应的值
        try:
            article_count = db.session.query(Article.user_id, func.count(Article.id)).filter(
                Article.status == Article.STATUS.APPROVED) \
                .group_by(Article.user_id).all()
        except DatabaseError as e:
            current_app.logger.error(e)
            raise e

        # 删除redis中的值
        pipe = current_app.redis_master.pipeline(transaction=False)
        key = 'count:user:arts'
        pipe.delete(key)
        # 重新写入redis
        for user_id, count in article_count:

            pipe.zadd(key, count, user_id)

        pipe.execute()
