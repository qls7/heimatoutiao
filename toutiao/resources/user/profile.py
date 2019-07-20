from flask import current_app, g, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import DatabaseError
from werkzeug.datastructures import FileStorage

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
            print(e)
            return {'message': 'image upload fail'}, 500

        photo_url = current_app.config['QINIU_DOMAIN'] + key

        # 把key存储到数据库中
        user_id = g.user_id
        try:
            User.query.filter(User.id == user_id).update({'profile_photo': key})
            db.session.commit()
        except DatabaseError as e:
            current_app.logger.error(e)

        return {'photo_url': photo_url}, 201


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
            except BaseException as e:
                current_app.logger.error(e)
                return {'message': 'Server Error'}, 500

            return user_dict
        else:
            return {'message': 'Invalid User'}, 400
