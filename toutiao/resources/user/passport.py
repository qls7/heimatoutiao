import logging
import random

from datetime import datetime
from flask import current_app
from flask_restful import Resource, reqparse
from redis import RedisError

from models import db
from models.user import User, UserProfile
from utils import parser
from utils.decorators import set_db_to_write
from . import constants


class SMSVerificationCodeResource(Resource):
    """
    获取短信验证码
    """

    def get(self, mobile):
        # 生成验证码
        code = '{:0>6d}'.format(random.randint(0, 999999))
        # 保存到redis 中
        current_app.redis_master.setex('app:code:{}'.format(mobile), constants.SMS_VERIFICATION_CODE_EXPIRES, code)
        # 使用celery 异步任务 发送短信
        from celery_tasks.sms.tasks import send_verification_code
        send_verification_code.delay(mobile, code)
        return {'mobile': mobile}


class AuthorizationResource(Resource):
    """
    登录认证
    """
    method_decorators = {
        'post': [set_db_to_write]
    }

    def post(self):
        """
        验证登录
        :return:
        """
        # 1. 获取参数
        parser_json = reqparse.RequestParser()
        parser_json.add_argument('mobile', type=parser.mobile, required=True, location='json')
        parser_json.add_argument('code', type=parser.regex(r'^\d{6}$'), required=True, location='json')

        args = parser_json.parse_args()

        mobile = args.get('mobile')
        code = int(args.get('code'))
        key = 'app:code:{}'.format(mobile)
        # 2. 跟redis数据库的进行比较
        try:
            server_code = current_app.redis_slave.get(key)
        except ConnectionError as e:  # 从数据库连接失败, 再到主数据库去查询
            current_app.logger.error(e)  # 记录下日志
            server_code = current_app.redis_master.get(key)

        #  删除验证码
        # try:
            # current_app.redis_master.delete(key)
        # except ConnectionError as e:
        #     current_app.logger.error(e)

        if not server_code or int(server_code) != code:

            return {'message': 'Invalid code.'}, 400
        # 登录成功 查询或保存用户
        user = User.query.filter_by(mobile=mobile).first()
        if user is None:
            # 用户不存在, 注册用户
            user_id = current_app.id_worker.get_id()  # 生成分布式id
            user = User(id=user_id, mobile=mobile, name=mobile, last_login=datetime.now())
            db.session.add(user)
            profile = UserProfile(id=user_id)
            db.session.add(profile)
            db.session.commit()
        # TODO 免密码登录
        return {'message': 'OK'}, 201
        # # 登录成功, 生成access_token 和refresh_token 并返回
        # access_token, refresh_token = genera_token()
        # data = {
        #     'access_token': access_token,
        #     'refresh_token': refresh_token
        # }
        # return data