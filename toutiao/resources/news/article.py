from flask import g, current_app
from flask_restful import Resource, reqparse, inputs
from flask_restful.inputs import positive

from cache.article import ArticleInfoCache
from rpc import reco_pb2_grpc, reco_pb2
from rpc.constants import USER_RECOMMENDS_COUNT
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
    def __get_article_recommends(self, channel_id, timestamp, article_num):
        """
        获取推荐的文章的方法
        1. 创建rpc连接对象 app.rpc_reco = grpc.insecure_channel('127.0.0.0:8888')
        2. 根据rpc连接对象创建rpc解析助手 stub= reco_pb2_grpc.RecoServiceStub(rpc连接对象)
        2. 创建rpc请求对象 request = reco_pb2.RecoRequest()
        3. 包装rpc请求数据
        4. 根据解析助手调用rpc远程服务接口的函数 stub.article_commend(request)
       :param channel_id:
       :param timestamp:
       :param article_num:
       :return:
       """
        #  创建解析助手 , 需要先创建rpc连接
        stub = reco_pb2_grpc.RecoServiceStub(current_app.rpc_reco)
        # 包装请求数据
        request = reco_pb2.RecoRequest()  # 创建reco 请求对象
        request.user_id = str(g.user_id) if g.user_id else 'anomy'  # 包装请求数据
        request.channel = channel_id
        request.time_stamp = timestamp
        request.article_num = article_num
        # 调用远程的函数
        return stub.article_recommend(request)

    def get(self):
        """
        获取首页推荐的文章
        :return:
        """
        qs_parser = reqparse.RequestParser()
        qs_parser.add_argument('channel_id', type=parser.channel_id, required=True, location='args')
        qs_parser.add_argument('time_stamp', type=positive, required=True, location='args')
        args = qs_parser.parse_args()

        channel_id = args.channel_id
        time_stamp = args.time_stamp

        # TOD 远程调用推荐系统的函数
        resp = self.__get_article_recommends(channel_id, time_stamp, USER_RECOMMENDS_COUNT)
        articles = []
        for article in resp.articles:
            article_dict = dict()
            article_id = article.article_id
            article_dict['article_id'] = article_id

            # 从缓存层中读取数据
            article_basic_dict = ArticleInfoCache(article_id).get()
            article_dict.update(article_basic_dict)  # 把缓存中返回的字典 直接添加到文章字典中
            article_dict['track'] = dict()  # 创建存储埋点的字典
            article_dict['track']['click'] = article.track.click  # 增加埋点数据
            article_dict['track']['read'] = article.track.read
            article_dict['track']['collect'] = article.track.collect
            articles.append(article_dict)

        ret = {'articles': articles, 'pre_time_stamp': resp.pre_time_stamp}  # 返回指定的格式
        return ret