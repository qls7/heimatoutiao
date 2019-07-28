import json
import unittest

from toutiao import create_app
from toutiao.settings.default import TestingConfig

flask_app = create_app(TestingConfig)


# 1. 定义测试用例类 继承unittest.TestCase
# 2. 在测试用例类中 定义测试方法 实现具体的测试
class SuggestionCase(unittest.TestCase):
    """
    文章建议测试单元
    """
    def setUp(self) -> None:
        """
        每次测试方法运行前会执行
        :return:
        """
        # 创建测试客户端
        self.client = flask_app.test_client()

    def tearDown(self) -> None:
        """
        每次测试方法运行后执行
        :return:
        """
        print('测试完成, 主要用于测试的收尾工作')

    def test_request_normal(self):
        """
        测试 正常访问接口
        :return:
        """
        # 发请求
        # 1> 使用普通的请求模块 urllib request
        # 2> 使用web应用提供的测试请求方法 flask_app.test() 优点:不是发真的请求, 是模拟请求, 执行效率比较高, 提高自动化测试的效率
        resp = self.client.get('/v1_0/suggestion?q=pthoyn%20web')

        # 使用断言进行判断请求的响应结果是否符合预期
        self.assertEqual(resp.status_code, 200)
        resp_str = resp.data  # json字符串
        resp_dict = json.loads(resp_str)
        self.assertIn('message', resp_dict)
        self.assertIn('data', resp_dict)
        self.assertIn('option', resp_dict['data'])

    def test_request_param_q_error(self):
        """
        测试请求参数 q 错误
        :return:
        """
        resp = self.client.get('/v1_0/suggestion?p=pthoyn%20web')
        self.assertEqual(resp.status_code, 400)

    def test_request_param_q_length_error(self):
        """
        测试请求参数 q 长度错误
        :return:
        """
        resp = self.client.get('/v1_0/suggestion?q={}'.format('*' * 51))
        self.assertEqual(resp.status_code, 400)


class SearchCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
