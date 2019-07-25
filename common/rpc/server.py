import time
from concurrent.futures import ThreadPoolExecutor

import grpc

from rpc import reco_pb2_grpc, reco_pb2


# 1.  现实远程调用的函数 继承自动生成的系统, 然后重写方法
class RecoServiceService(reco_pb2_grpc.RecoServiceServicer):
    """
    继承reco_pb2_grpc 重写被调用的方法
    """
    def article_recommend(self, request, context=None):
        """
        远程调用的函数
        :param request: 请求数据
        :param context: 包含请求的相关信息
        :return: 远程函数返回的响应数据
        """
        print(request.age)  # 获取请求数据

        # 模拟构建响应对象 从 reco_pb2 中构建
        resp = reco_pb2.RecoResponse()
        articles_list = []
        article = reco_pb2.Article()
        article.article_id = 1
        article.track.click = 'user:1:article:1:click'
        article.track.read = 'user:1:article:1:read'
        article.track.collect = 'user:1:article:1:collect'
        articles_list.append(article)
        resp.pre_time_stamp = 1564060850

        resp.articles.extend(articles_list)

        return resp

        return resp


# 2. 配置服务器
def server():
    """
    启动服务器
    :return:
    """
    executor = ThreadPoolExecutor(max_workers=10)
    # 创建服务器对象
    server = grpc.server(executor)
    # 注册远程调用的函数
    reco_pb2_grpc.add_RecoServiceServicer_to_server(RecoServiceService, server)
    # 监听端口
    server.add_insecure_port('127.0.0.1:8888')
    # 启动服务器
    server.start()
    while True:  # 服务器非阻塞, 代码执行完就会自动停止
        time.sleep(60 * 60 * 24)