from flask import current_app
from qiniu import Auth, put_data


def upload_file(data):
    """
    七牛云文件上传
    :param data: 文件的二进制数据
    :return: 七牛云存储的文件按名
    """
    # 需要填写你的AK 和 SK
    access_key = current_app.config['QINIU_ACCESS_KEY']
    secret_key = current_app.config['QINIU_SECRET_KEY']

    # 构建鉴权对象
    auth = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = current_app.config['QINIU_BUCKET_NAME']

    # 上传后保存的文件名, 如果设置为None, 就会生成随机名称
    key = None

    # 生成上传 Token, 可以指定过期时间等, 注意这里的过期时间是token的过期时间
    token = auth.upload_token(bucket_name, key, 3600 * 1000)

    # 上传二进制数据到七牛云
    ret, info = put_data(token, key, data) # ret 是一个字典 info 是一个ResponseInfo对象
    if info.status_code == 200:  # 注意这里状态码是 int
        return ret.get('key')  # 上传成功, 返回七牛云存储的图片名
    else:
        raise Exception(info.status_code)  # 上传失败, 抛出异常, 获取具体的错误信息状态码


if __name__ == '__main__':
    with open('/home/python/Desktop/123.jpg', 'rb') as f:
        data = f.read()
        name = upload_file(data)
        print(f)