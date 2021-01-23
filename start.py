#!user/bin/env python3
# -*- coding: UTF-8 -*-

"""
汽车三包项目
@Time : 2021/1/21 11:20
@File : start.py
@Software: PyCharm
@author: 王伟 A21036

         项目的启动功能。
        说明：
        1、启动项目
        2、明确参数
"""

import argparse
from download import Download
from parse import Parse
from tools import make_url_list
from config import configs
from tools import get_redis_connect,make_dir,make_all_path
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', "--url", type=str, default='https://www.qcsanbao.cn/webqcba/DVMProducerServlet?method=getWhereList&p=1', help="要爬取的网站")
    args = parser.parse_args()
    url = args.url
    base_url = configs["basic_url"]
    r = get_redis_connect()
    dl = Download()
    par = Parse()
    make_url_list(base_url,par.parse_main_page_get_total_pagenum(dl.download_first_page(url)))
    for url in r.smembers("url_list"):
        r = par.parse_main_page_get_detail_page_url(url,dl.download_first_page(url),r)
        dl.download_list_page_html(url)
        r.srem("url_list",url)

    for detail_url in r.smembers("detail_url_list"):
        par.parse_detail_page_get_url(detail_url,dl.download_first_page(detail_url),r)
        dl.download_code_page(detail_url)
        r.srem("detail_url_list", detail_url)

    for sanbao_detail_url in r.smembers("sanbao_info_url_list"):
        par.parse_detail_page_get_pdf_url(sanbao_detail_url,dl.download_first_page(sanbao_detail_url),r)
        dl.download_sanbao_detail_page(sanbao_detail_url)
        r.srem("sanbao_info_url_list", sanbao_detail_url)


    for pdf_download_html_url in r.smembers("pdf_download_page_url_list"):
        car_name,car_type,info,pdf_real_url = pdf_download_html_url.split("#@#")
        dl.download_sanbao_pdf_detail_page(pdf_download_html_url)
        r.srem("pdf_download_page_url_list", pdf_download_html_url)

    print("开始下载pdf")
    for pdf_url in r.smembers("pdf_url_list"):
        pdf_url_path = pdf_url[8:]
        pdf_path_dirs = pdf_url_path.split("/")
        dir = make_all_path(pdf_path_dirs[:-1])
        dst = os.path.join(dir,pdf_path_dirs[-1])
        dl.down_pdf_with_tqdm(pdf_url,dst)
        r.srem("pdf_url_list", pdf_url)


