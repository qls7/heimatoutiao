import time

from flask import g, current_app
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError

from cache import user, statistic
from models import db
from models.user import Relation
from utils.decorators import login_required, set_db_to_write


class FollowingListResource(Resource):
    """
    关注用户的api
    """
    method_decorators = {
        'post': [login_required, set_db_to_write]
    }

    def post(self):
        """
        关注用户
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('target', required=True, location='json', type=int)
        args = parser.parse_args()

        target_id = args.get('target')
        if target_id == g.user_id:
            return {'message': 'User  cannot following self'}, 400
        ret = 1

        # 先存mysql
        try:
            follow = Relation(user_id=g.user_id, target_user_id=target_id, relation=Relation.RELATION.FOLLOW)
            db.session.add(follow)
            db.session.commit() # 如果添加失败, 说明已经有关注的记录了, 应该进行修改
        except IntegrityError:
            db.session.rollback()
            ret = Relation.query.filter(Relation.user_id == g.user_id, Relation.target_user_id == target_id,
                                        Relation.relation != Relation.RELATION.FOLLOW)\
                .update({'relation': Relation.RELATION.FOLLOW})  # 直接查出这条记录, 进行修改状态
            db.session.commit()
        # 再存缓存中
        if ret > 0:  # ret的值大于0 说明修改成功
            timestamp = time.time()
            # 用户关注列表缓存中添加数据
            user.UserFollowingCache(g.user_id).update(target_id, timestamp)
            # 用户粉丝列表缓存中添加数据
            user.UserFansCache(target_id).update(g.user_id, timestamp)
            # 统计数据持久化存储
            statistic.UserFollowingsCountStorage.incr(g.user_id)
            statistic.UserFansCountStorage.incr(target_id)

        # 最后再添加到消息队列
        _user = user.UserProfileCache(g.user_id).get()
        _data = {
            'user_id': g.user_id,
            'user_name': _user.get('name'),
            'user_photo': _user.get('photo'),
            'timestamp': int(time.time())
        }
        # TDO 需要将"张三关注李四的通知" 放如消息队列
        current_app.siomgr.emit('following notify', _data, room=target_id)

        # 返回关注成功
        return {'target': target_id}, 201
