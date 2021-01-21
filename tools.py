#!user/bin/env python3
# -*- coding: UTF-8 -*-

"""
汽车三包项目
@Time : 2021/1/21 11:43
@File : tools.py
@Software: PyCharm
@author: 王伟 A21036

         工具包功能。
        说明：
        1、一些工具的存放
"""
import redis
from config import configs


def make_url_list(base_url,num):
    """
    制作一个列表页的url_list
    :param base_url: 列表页中的不变的基础url
    :param num: 总页数
    :return: 列表页的url_list
    """
    url_list = []
    for i in range(1,num+1):
        url_list.append(base_url + str(i))
    return url_list


def get_redis_connect():
    r = redis.Redis(host=configs["redis"]["host"], port=configs["redis"]["port"],db=configs["redis"]["db"], decode_responses=True)
    return r








