from flask import current_app, g
from flask_restful import Resource, reqparse, inputs

from cache import user
from cache.article import ArticleInfoCache


class SearchResource(Resource):
    """
    搜索结果
    """
    def get(self):
        """
        获取搜索结果
        :return:
        """
        # 解析参数
        qs_parser = reqparse.RequestParser()
        qs_parser.add_argument('q', type=inputs.regex(r'^.{1,50}$'), required=True, location='args')
        qs_parser.add_argument('page', type=inputs.positive, default=1, required=False, location='args')
        qs_parser.add_argument('per_page', type=int, default=10, required=False, location='args')
        args = qs_parser.parse_args()

        q = args.q
        page = args.page
        per_page = args.per_page

        body = {
            '_source': False,  # 设置返回的字段, False不返回任何字段, 只返回文章id
            'from': (page-1) * per_page,  # 每页的起始页码
            'size': per_page,  # 每页显示的个数
            'query': {  # 表示查询
                'bool': {  # 多个查询需要用bool
                    'must': {  # 逻辑与运算
                        'match': {  # 高级查询全文检索
                            '_all': q  # 表示查询所有标记为_all_include的字段
                        }
                    },
                    'filter': {  # 逻辑查询过滤, 查询结果不会进行排序
                        'term': {  # 高级查询精确查找, 不会进行分词
                            'status': 2  # 查询状态为2 的文章数据
                        }
                    }
                }
            }
        }

        # 进行ES查询
        ret = current_app.es.search(index='articles', doc_type='article', body=body)
        articles = ret['hits']['hits']

        total_count = ret['hits']['total']

        results = []
        for article in articles:
            # 根据id查询基础数据库
            article_dict = ArticleInfoCache(article['_id']).get()
            results.append(article_dict)

        # 存储搜索历史 在redis中进行持久化
        if g.uer_id and page == 1:
            user.UserSearchingHistoryStorage(g.user_id).save(q)

        # 包装为json返回
        resp = {
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'results': results
        }
        return resp


class SuggestionResource(Resource):
    """
    联想建议
    """
    def get(self):
        """
        获取联想建议
        :return:
        """
        # 解析参数
        qs_parse = reqparse.RequestParser()
        qs_parse.add_argument('q', type=inputs.regex(r'.{1,500}$'), required=True, location='args')
        args = qs_parse.parse_args()

        q = args.q

        # 先尝试自动补全建议查询
        query = {
            'from': 0,
            'size': 10,
            '_source': False,
            'suggest': {
                'word-completion': {
                    'prefix': q,
                    'completion': {
                        'field': 'suggest'
                    }
                }
            }
        }
        ret = current_app.es.search(index='completions', body=query)
        options = ret['suggest']['word-completion'][0]['options']

        # 如果没得到查询结果, 进行纠错建议查询
        if not options:
            query = {
                'from': 0,
                'size': 10,
                '_source': False,
                'suggest': {
                    'text': q,  # 输入的内容
                    'word-phrase': {  # 自定义字段名, 推荐结果会包含在该字段中
                        'phrase': {  # 返回短语形式, 还可以使用 term
                            'field': '_all',  # 指定在哪些字段中获取推荐词
                            'size': 1  # 返回的推荐词数量
                        }
                    }
                }
            }
            ret = current_app.es.search(index='articles', doc_type='article', body=query)
            options = ret['suggest']['word-phrase'][0]['options']

        results = []
        for option in options:
            if option['text'] not in results:
                results.append(option['text'])

        return {'options': results}