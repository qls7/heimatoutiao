import os
import sys

# 获取项目的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 添加common文件夹到查询路径
sys.path.insert(0, os.path.join(BASE_DIR, 'im'))