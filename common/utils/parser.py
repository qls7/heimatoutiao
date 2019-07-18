import base64
import imghdr
import re

from datetime import datetime


def mobile(mobile_str):
    """
    检验手机号格式
    :param mobile_str: 被检验字符串
    :return: mobile_str
    """
    if re.match(r'^1[3-9]\d{9}$', mobile_str):
        return mobile_str
    else:
        raise ValueError('{} is not a valid mobile'.format(mobile_str))


def email(email_str):
    """
    检验邮箱格式
    :param email_str: 被检验字符串
    :return: email_str
    """
    if re.match(r'^([A-Za-z0-9_\-\.\u4e00-\u9fa5])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,8})$', email_str):
        return email_str
    else:
        raise ValueError('{} is not a valid email'.format(email_str))


def regex(pattern):
    """
    正则校验
    :param pattern: str 正则表达式
    :return: 校验函数
    """
    def validate(value_str):
        """
        检验字符串格式
        :param value_str: 被检验字符串
        :return: bool 检验是否通过
        """
        if re.match(pattern, value_str):
            return value_str
        else:
            raise ValueError('Invalid params.')

    return validate


def date(value):
    """
    检验是否是合法日期
    :param value: 被检验的值
    :return: date
    """
    try:
        if not value:
            return None
        _date = datetime.strptime(value, '%Y-%m-%d')
    except Exception:
        raise ValueError('Invalid date param.')
    else:
        return _date


def date_time(value):
    """
    检验是否是合法日期时间
    :param value: 被检验的值
    :return: _date_time
    """
    try:
        if not value:
            return None
        _date_time = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except Exception:
        raise ValueError('Invalid date param.')
    else:
        return _date_time


def image_base64(value):
    """
    检验是否是base64图片文件
    :param value: 被检验的值
    :return: photo
    """
    try:
        photo = base64.b64decode(value)
        file_header = photo[:32]
        file_type = imghdr.what(None, file_header)  # 获取文件的类型
    except Exception:
        raise ValueError('Invalid image.')
    else:
        if not file_type:
            raise ValueError('Invalid image.')
        else:
            return photo


def image_file(value):
    """
    检查是否是图片文件
    :param value:
    :return:
    """
    try:
        file_type = imghdr.what(value)  # 获取文件的类型
    except Exception:
        raise ValueError('Invalid image.')
    else:
        if not file_type:
            raise ValueError('Invalid image.')
        else:
            return value


def id_number(value):
    """
    检查是否为身份证号
    :param value:
    :return:
    """
    id_number_pattern = r'(^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$)|(^[1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{2}$)'
    if re.match(id_number_pattern, value):
        return value.upper()
    else:
        raise ValueError('Invalid id number.')


# def channel_id(value):
#     """
#     检查是否是频道ID
#     :param value:  被检查的值
#     :return: channel_id
#     """
#     try:
#         _channel_id = int(value)
#     except Exception:
#         raise ValueError('Invalid channel id.')
#     else:
#         if _channel_id < 0:
#             raise ValueError('Invalid channel id.')
#         if _channel_id == 0:
#             #  Recommendation channel
#             return _channel_id
#         else:
#             ret = cache_channel.AllChannelsCache.exists(_channel_id)
#             if ret:
#                 return _channel_id
#             else:
#                 raise ValueError('Invalid channel id.')
