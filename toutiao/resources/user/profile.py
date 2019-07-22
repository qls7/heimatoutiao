from flask import current_app, g, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import DatabaseError
from werkzeug.datastructures import FileStorage

from cache.statistic import UserArticleCountStorage, UserFollowingsCountStorage, UserFansCountStorage
from cache.user import UserProfileCache
from models import db
from models.user import User
from utils import parser, storage
from utils.decorators import login_required, set_db_to_write, set_db_to_read


class PhotoResource(Resource):
    """
    头像上传接口
    """
    method_decorators = [login_required, set_db_to_write]

    def patch(self):
        """
        头像上传使用patch方法
        :return: json
        """
        parser_json = reqparse.RequestParser()
        parser_json.add_argument('photo', type=parser.image_file, required=True, location='files')
        args = parser_json.parse_args()
        # 获取上传的二进制数据
        # f = request.files.get('photo')  # type: FileStorage
        # f.read()  # f.save()

        f = args.get('photo')

        # 解析出来的是文件的对象
        img_bytes = f.read()  # 获取图片的二进制
        try:
            key = storage.upload_file(img_bytes)
        except BaseException as e:
            current_app.logger.error(e)
            return {'message': 'image upload fail'}, 500

        photo_url = current_app.config['QINIU_DOMAIN'] + key

        # 把key存储到数据库中
        user_id = g.user_id
        lock_key = 'user:{}:profile:update'.format(user_id)
        # 1.使用悲观锁进行保证缓存更新一致的问题, 但完全是串行, 影响效率
        # 2.使用乐观锁保证缓存更新一致, 可以支持并发, 但不能完全保证一致
        current_app.redis_cluster.incr(lock_key)

        try:
            User.query.filter(User.id == user_id).update({'profile_photo': key})
            db.session.commit()
        except DatabaseError as e:
            current_app.logger.error(e)
            current_app.redis_cluster.decr(lock_key, -1)
            return {'message': 'Database Error'}, 500

        UserProfileCache(user_id).clear()  # 删除该数据对象对应的缓存
        current_app.redis_cluster.decr(lock_key, -1)

        return {'photo_url': photo_url}, 201
        # while True:
        #     lock = current_app.redis_cluster.setnx(lock_key, 1)
        #     if lock:
        #         current_app.redis_cluster.expire(lock_key, 1)
        #         try:
        #             User.query.filter(User.id == user_id).update({'profile_photo': key})
        #             db.session.commit()
        #         except DatabaseError as e:
        #             current_app.logger.error(e)
        #             # current_app.redis_cluster.delete(lock_key)
        #             return {'message': 'Database Error'}, 500
        #         UserProfileCache(user_id).clear()  # 删除该数据对象对应的缓存
        #         # current_app.redis_cluster.delete(lock_key)
        #         return {'photo_url': photo_url}, 201


class CurrentUserProfileResource(Resource):
    """
    个人中心-获取用户信息
    """
    method_decorators = [login_required, set_db_to_read]

    def get(self):
        """
        获取用户信息
        :return:
        """
        user_id = g.user_id
        # 先进行判断user_id是否存在
        user_cache = UserProfileCache(user_id)

        if user_cache.exist():
            # 获取用户信息
            try:
                user_dict = user_cache.get()
                user_dict['art_count'] = UserArticleCountStorage.get(user_id)
                user_dict['followings_count'] = UserFollowingsCountStorage.get(user_id)
                user_dict['fans_count'] = UserFansCountStorage.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)
                return {'message': 'Server Error'}, 500

            return user_dict
        else:
            return {'message': 'Invalid User'}, 400
