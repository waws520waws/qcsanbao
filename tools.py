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
from threading import Thread
import pymysql
from threading import Lock
import time
import traceback

def get_md5(url):
    """
    原本相对文件的路径进行md5加密，用于构建pdf的存放的路径，后期存放规则变化，弃用
    :param url: 传入的pdf的url链接
    :return: MD5加密后的16进制字符串的前8位
    """
    m = hashlib.md5()
    m.update(url.encode("utf8"))
    return m.hexdigest()[:9]


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
            r.rpush("url_list",base_url + str(i))


def get_redis_connect():
    """
    获取redis的链接对象
    :return: redis链接对象
    """
    r = redis.Redis(host=configs["redis"]["host"], port=configs["redis"]["port"],db=configs["redis"]["db"], decode_responses=True)
    return r


def make_dir(car_name,car_type,pdf_name):
    """
    制作车辆名称/车辆code的爬虫的目录/xxxx.pdf，最后返回pdf的完整路径，需要现在已经弃用
    :param car_name: 车辆名称
    :param car_type: 车辆code
    :param pdf_name: pdf的文件名称
    :return: pdf存放的完整路径
    """
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
    """
    主要用于构建固定的二级目录 www.qcsanbao.cn/webqcba
    :param first_dir: 第一级目录
    :param sec_dir: 第二级目录
    :return: 完整的路径
    """
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
    """
    在上面的二级目录的基础上完成第三级目录的创建
    :param detail_dir: 第三级的目录
    :return: 第三级目录的详细的地址
    """
    detail_dir_path = os.path.join(make_store_html_dir(), detail_dir)
    if not os.path.exists(detail_dir_path):
        os.mkdir(detail_dir_path)
    return detail_dir_path


def make_all_path(path_list):
    """
    循环创建不定级别的目录
    :param path_list: 目录的列表
    :return: 返回对应的列表的级别的目录体系
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    for path in path_list:
        base_dir = os.path.join(base_dir,path)
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
    return base_dir


def change_success_or_fail_num(num):
    """
    改变成功和失败的爬虫的个数
    :param num: 判断是成功还是失败
    :return: None
    """
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
    """
    获取爬取成功，和失败的爬虫的数量
    :return: 成功爬虫数量，失败的爬虫的数量
    """
    r = get_redis_connect()
    success_num =r.get("success_num") if r.get("success_num") else 0
    fail_num = r.get("fail_num") if r.get("fail_num") else 0
    return success_num,fail_num

def get_logger():
    """
    获取日志对象
    :return: 日志对象
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("test.log", "a", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s--%(name)s--%(lineno)d--%(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def get_mysql_connect():
    """
    获取mysqld的链接对象，弃用
    :return: mysql的链接的游标对象
    """
    db = pymysql.connect(host=configs["host"], user=configs["user"], passwd=configs["passwd"], db=configs["db"],port=configs["port"])
    cursor = db.cursor()
    return cursor


def download_and_parse_page(url_list,r,func1,func2,func3,lock):
    """
    根据指定链接，解析并下载对应的html文件，并且将相关的url链接存储到redis中
    :param url_list: 字符串，待爬取的redis中存储的url_list
    :param r: redis对象
    :param func1: 处理对应url的方法处理方法1
    :param func2: 处理对应url的方法处理方法2
    :param func3: 处理对应url的方法处理方法3
    :param lock: 锁
    :return: 无返回
    """
    try:
        while True:
            count = 0
            lock.acquire()
            url = r.lpop(url_list)
            lock.release()
            if not url:
                """
               这个部分主要是判断一个redis的存储，是不是空，不是空，直接去取数据，应用下面的方法进行处理即可，当为空时，让整个线程进行等待，不断的扫描
               可能再次解析到的数据，还会存储到当前的url_list中，扫描到数据继续进行处理，假设5分钟都没有扫描到数据吧，说明这个部分已经全部爬取完成，直接rerturn
               让当前线程直接结束即可。
               """
                while count < 30:
                    time.sleep(10)
                    count += 1
                    url = r.lpop(url_list)
                    if url:
                        break
                else:
                    logger = get_logger()
                    logger.info(url_list + " 已经爬取完毕###")
                    return
            func1(url, func2(url), r)
            func3(url)
            time.sleep(0.5)
    except Exception as e:
        logger = get_logger()
        logger.info("解析失败" + traceback.format_exc().replace("\n", " "))
        download_and_parse_page(url_list, r, func1, func2, func3, lock)



def download_page(url_list,r,func1,lock):
    """
    根据指定链接，下载对应的html文件
    :param url_list: 字符串，待爬取的redis中存储的url_list
    :param r: redis对象
    :param func1: 处理对应url的方法
    :param lock: 锁
    :return: 无
    """
    try:
        while True:
            count = 0
            lock.acquire()
            url = r.lpop(url_list)
            lock.release()
            if url is None:
                while count < 30:
                    time.sleep(10)
                    count += 1
                    url = r.lpop(url_list)
                    if url:
                        break
                else:
                    logger = get_logger()
                    logger.info(url_list + " 已经爬取完毕###")
                    return
            func1(url)
            time.sleep(0.5)
    except Exception as e:
        logger = get_logger()
        logger.info("解析失败" + traceback.format_exc().replace("\n", " "))
        download_page(url_list, r, func1, lock)



def download_pdf_file(url_list,r,func1,lock):
    """
    根据指定链接，下载pdf文件
    :param url_list: 字符串，待爬取的redis中存储的url_list
    :param r: redis的链接对象
    :param func1: 对于拿到的pdf_url的处理方法
    :param lock: 锁
    :return: 没有返回
    """
    try:
        while True:
            count = 0
            lock.acquire()
            pdf_url = r.lpop(url_list)
            lock.release()
            if pdf_url is None:
                while count < 30:
                    time.sleep(10)
                    count += 1
                    pdf_url = r.lpop(url_list)
                    if pdf_url:
                        break
                else:
                    logger = get_logger()
                    logger.info(url_list + " 已经爬取完毕###")
                    return
            pdf_url_path = pdf_url[8:]
            pdf_path_dirs = pdf_url_path.split("/")
            dir = make_all_path(pdf_path_dirs[:-1])
            dst = os.path.join(dir, pdf_path_dirs[-1])
            func1(pdf_url,dst)
            change_success_or_fail_num(1)
            time.sleep(0.5)
            s_num, f_num = get_success_and_fail_num()
            logger = get_logger()
            logger.info("爬取成功了"+str(s_num) + "个数据,失败了"+ str(f_num) + "条数据")
    except Exception as e:
        logger = get_logger()
        logger.info("解析失败" + traceback.format_exc().replace("\n", " "))
        change_success_or_fail_num(0)
        download_pdf_file(url_list, r, func1, lock)










