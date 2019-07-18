import random

from datetime import datetime, timedelta
from flask import current_app, g
from flask_restful import Resource, reqparse

from models import db
from models.user import User, UserProfile
from utils import parser
from utils.decorators import set_db_to_write, login_required
from utils.jwt_util import generate_jwt
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
        'post': [set_db_to_write],
        'get': [login_required],
    }

    def _generate_token(self, user_id, is_refresh=True):
        """
        生成JWT
        :param user_id: 用户id
        :return: token
        """
        # 生成访问token
        # 构建数据
        payload = {'payload': user_id, 'is_refresh': False}
        # 设置过期时间
        expiry = datetime.utcnow() + timedelta(current_app.config['JWT_EXPIRY_HOURS'])
        access_token = generate_jwt(payload, expiry)

        if is_refresh:
            # 生成刷新token
            payload = {'payload': user_id, 'is_refresh': True}
            # 设置过期时间
            expiry = datetime.utcnow() + timedelta(current_app.config['JWT_REFRESH_DAYS'])
            refresh_token = generate_jwt(payload, expiry)
        else:
            refresh_token = None

        return access_token, refresh_token

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
        else:
            user_id = user.id
        # 免密码登录
        # 登录成功, 生成access_token 和refresh_token 并返回
        access_token, refresh_token = self._generate_token(user_id)
        return {
                   'access_token': access_token,
                   'refresh_token': refresh_token
               }, 201

    def get(self):
        """测试认证权限"""
        return {'user_id': g.user_id, 'is_refresh': g.is_refresh}

    def put(self):
        """访问token过期, 生成访问token"""
        if g.user_id and g.is_refresh:
            access_token, refresh_token = self._generate_token(g.user_id, is_refresh=False)
            # 返回访问token
            return {'access_token': access_token}
        else:
            return {'message': 'Invalid jwt'}, 401  # 返回401 未认证
