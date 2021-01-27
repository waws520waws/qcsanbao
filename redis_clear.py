#!user/bin/env python3
# -*- coding: UTF-8 -*-

"""
汽车三包项目
@Time : 2021/1/27 9:44
@File : redis_clear.py
@Software: PyCharm
@author: 王伟 A21036

         redis数据库清除功能功能。
        说明：
        1、想要重新从头开始下载项目，需要清理redis中存在的数据
"""
from tools import get_redis_connect
r = get_redis_connect()
r.flushdb()
print("redis-15清理成功")
