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
import os
import hashlib
import logging


def get_md5(url):
    m = hashlib.md5()
    m.update(url.encode("utf8"))
    print(m.hexdigest()[:9])


def make_url_list(base_url,num):
    """
    制作一个列表页的url_list
    :param base_url: 列表页中的不变的基础url
    :param num: 总页数
    :return: 列表页的url_list
    """
    r = get_redis_connect()

    for i in range(1,num+1):
        if r.sadd("all_url_list",base_url + str(i)):
            r.sadd("url_list",base_url + str(i))


def get_redis_connect():
    r = redis.Redis(host=configs["redis"]["host"], port=configs["redis"]["port"],db=configs["redis"]["db"], decode_responses=True)
    return r


def make_dir(car_name,car_type,pdf_name):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    pdf_path = os.path.join(base_dir,car_name,car_type,pdf_name)
    car_name_dir = os.path.join(base_dir, car_name)
    car_type_dir = os.path.join(car_name_dir, car_type)
    if not os.path.exists(car_name_dir):
        os.mkdir(car_name_dir)
    if not os.path.exists(car_type_dir):
        os.mkdir(car_type_dir)
    return pdf_path

def make_store_html_dir(first_dir = configs["first_dir"],sec_dir = configs["sec_dir"]):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    html_store_path = os.path.join(base_dir,first_dir,sec_dir)
    first_dir_path = os.path.join(base_dir, first_dir)
    sec_dir_path = os.path.join(first_dir_path, sec_dir)
    if not os.path.exists(first_dir_path):
        os.mkdir(first_dir_path)
    if not os.path.exists(sec_dir_path):
        os.mkdir(sec_dir_path)
    return html_store_path

def make_store_detail_html_dir(detail_dir):
    detail_dir_path = os.path.join(make_store_html_dir(), detail_dir)
    if not os.path.exists(detail_dir_path):
        os.mkdir(detail_dir_path)
    return detail_dir_path

def make_all_path(path_list):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    for path in path_list:
        base_dir = os.path.join(base_dir,path)
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
    return base_dir

def change_success_or_fail_num(num):
    r = get_redis_connect()
    if num:
        if r.get("success_num"):
            r.set("success_num",str(int(r.get("success_num"))+1))
        else:
            r.set("success_num",str(1))
    else:
        if r.get("fail_num"):
            r.set("fail_num",str(int(r.get("fail_num"))+1))
        else:
            r.set("fail_num",str(1))


def get_success_and_fail_num():
    r = get_redis_connect()
    success_num =r.get("success_num") if r.get("success_num") else 0
    fail_num = r.get("fail_num") if r.get("fail_num") else 0
    return success_num,fail_num

def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("test.log", "a", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s--%(name)s--%(lineno)d--%(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

if __name__ == '__main__':
    # make_dir("福特","CTYUUU","a.pdf")
    # get_md5("https://sanbaobeian.dpac.org.cn/uploads/AttachmentData/%E6%96%B0%E7%A6%8F%E7%89%B9%E9%94%90%E7%95%8C%E8%BD%A6%E4%B8%BB%E6%89%8B%E5%86%8C.pdf")
    # count_success_or_fault_num(1)
    pass






