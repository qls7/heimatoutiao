import random

from flask import current_app
from flask_restful import Resource

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
