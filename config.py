#!user/bin/env python3
# -*- coding: UTF-8 -*-

"""
汽车三包项目
@Time : 2021/1/21 18:10
@File : config.py
@Software: PyCharm
@author: 王伟 A21036

         配置文件。
        说明：
        1、基本的redis的连接配置
        2、base_url的配置
        3.html的固定存放目录：第一级目录，第二级目录
"""


configs = {
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 15
    },
    "basic_url":"https://www.qcsanbao.cn/webqcba/DVMProducerServlet?method=getWhereList&p=",
    "first_dir":"www.qcsanbao.cn",
    "sec_dir":"webqcba",
    "thrid_dir":"data",
    "test": 4,
    # "test":1270,
    "thread_num": 8,
}
