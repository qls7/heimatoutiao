from flask import g
from flask_restful import Resource, reqparse, inputs
from flask_restful.inputs import positive

from cache.article import ArticleInfoCache
from utils import parser
from utils.logging import write_trace_log


class ArticleResource(Resource):
    """
    获取文章接口
    """

    def get(self, article_id):
        """
        获取文章详情
        :param article_id: 文章id int
        :return:
        """
        qs_parser = reqparse.RequestParser()
        #  对埋点进行获取, 埋点存放在请求头中
        qs_parser.add_argument('Trace', type=inputs.regex(r'^.+$'), required=False, location='headers')
        args = qs_parser.parse_args()

        # 缓存中获取数据进行返回
        article_cache = ArticleInfoCache(article_id)
        if not article_cache.exist():
            return {'message': 'Invalid article_id'}, 400

        trace = args.get('Trace')
        # 获取埋点数据, 如果有,把埋点数据写进日志中
        if trace:
            write_trace_log(trace)

        # TODO 从缓存层中查询 文章内容/关注/评论/点赞情况

        # TODO 用过RPC向推荐系统索取相关文章数据

        # TODO 使用持久化工具类 写入阅读历史

        return article_cache.get()


class ArticleListResource(Resource):
    """
    获取文章列表数据
    """
    def get(self):
        """
        获取首页推荐的文章
        :return:
        """
        qs_parser = reqparse.RequestParser()
        qs_parser.add_argument('channel_id', type=parser.channel_id, required=True, loaction='args')
        qs_parser.add_argument('time_stamp', type=positive, required=True, loaction='args')
        args = qs_parser.parse_args()

        channel_id = args.channel_id
        time_stamp = args.time_stamp
        user_id = g.user_id

        # TODO 远程调用推荐系统的函数

        ret = {'articles': []}
        return ret