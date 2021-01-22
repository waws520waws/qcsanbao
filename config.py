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
        3、
        4、日志记录在log文件夹
"""


configs = {
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 15
    },
    "basic_url":"https://www.qcsanbao.cn/webqcba/DVMProducerServlet?method=getWhereList&p="
}
