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
from tools import get_redis_connect,download_page,download_and_parse_page,download_pdf_file
import os
from threading import Thread,Lock
import time
lock = Lock()

if __name__ == '__main__':
    time1 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', "--url", type=str, default='https://www.qcsanbao.cn/webqcba/DVMProducerServlet?method=getWhereList&p=1', help="要爬取的网站")
    args = parser.parse_args()
    url = args.url
    base_url = configs["basic_url"]
    r = get_redis_connect()
    dl = Download()
    par = Parse()

    # 制作列表页的url_list
    make_url_list(base_url,par.parse_main_page_get_total_pagenum(dl.download_first_page(url)))

    threading_list = []

    threading_list.extend([Thread(target=download_and_parse_page,args=("url_list",r,par.parse_main_page_get_detail_page_url,dl.download_first_page,dl.download_list_page_html,lock)) for _ in  range(2)])
    threading_list.extend([Thread(target=download_and_parse_page,args=("detail_url_list",r,par.parse_detail_page_get_url,dl.download_first_page,dl.download_code_page,lock)) for _ in  range(8)])

    threading_list.extend([Thread(target=download_page, args=("brand_url_list", r, dl.download_brand_page, lock)) for _ in range(8)])

    threading_list.extend([Thread(target=download_and_parse_page, args=("sanbao_info_url_list", r, par.parse_detail_page_get_pdf_url, dl.download_first_page,dl.download_sanbao_detail_page, lock)) for _ in range(8)])


    threading_list.extend([Thread(target=download_page, args=("pdf_download_page_url_list",r,dl.download_sanbao_pdf_detail_page,lock)) for _ in range(8)])

    threading_list.extend([Thread(target=download_pdf_file, args=("pdf_url_list",r,dl.down_pdf_with_tqdm,lock)) for _ in range(8)])

    for thread in threading_list:
        thread.start()

    for thread in threading_list:
        thread.join()

    print("哈哈")


