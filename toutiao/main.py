import os
import sys

from flask import jsonify

from .settings.default import DefaultConfig
from . import create_app


# 获取项目的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 添加common文件夹到查询路径
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))

# 创建flask应用
app = create_app(DefaultConfig, enable_config_file=True)


@app.route('/')
def route_map():
    """
    主视图
    :return:
    """
    rules_iterator = app.url_map.iter_rules()
    return jsonify({rule.endpoint: rule.rule for rule in rules_iterator if rule.endpoint not in ('route_map', 'static')})
