# 创建蓝图对象
from flask import Blueprint
from flask_restful import Api

from toutiao.resources.news.article import ArticleResource, ArticleListResource
from utils.output import output_json

news_bp = Blueprint('news', __name__)
# 创建api对象
news_api = Api(news_bp)
# 指定自定义的json返回格式
news_api.representation('application/json')(output_json)

# 注册蓝图
news_api.add_resource(ArticleResource, '/v1_0/article/<int(min=1):article_id>', endpoint='Article')

# 注册蓝图
news_api.add_resource(ArticleListResource, '/v1_0/articles', endpoint='Articles')