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
from tools import get_redis_connect,download_page,download_and_parse_page,download_pdf_file,get_success_and_fail_num
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
    make_url_list(base_url,par.parse_main_page_get_total_pagenum(dl.download_first_page(url),configs["test"]))

    threading_list = []

    # 列表页的解析详情页的数据url,存放在redis中，并且下载列表页html
    threading_list.extend([Thread(target=download_and_parse_page,args=("url_list",r,par.parse_main_page_get_detail_page_url,dl.download_first_page,dl.download_list_page_html,lock)) for _ in  range(configs["thread_num"])])

    # 解析详情页的code和name数据url,存放在redis中，并且下载详情页html
    threading_list.extend([Thread(target=download_and_parse_page,args=("detail_url_list",r,par.parse_detail_page_get_url,dl.download_first_page,dl.download_code_page,lock)) for _ in  range(configs["thread_num"])])

    # 利用上面解析的name数据，下载品牌页html
    threading_list.extend([Thread(target=download_page, args=("brand_url_list", r, dl.download_brand_page, lock)) for _ in range(configs["thread_num"])])

    # 解析code页的数据获取pdf_url和pdf_download_url,存放在redis中，并且下载三包详情页html
    threading_list.extend([Thread(target=download_and_parse_page, args=("sanbao_info_url_list", r, par.parse_detail_page_get_pdf_url, dl.download_first_page,dl.download_sanbao_detail_page, lock)) for _ in range(configs["thread_num"])])

    # 利用上面解析的pdf_download_html_url数据，下载三包信息pdf下载页html
    threading_list.extend([Thread(target=download_page, args=("pdf_download_page_url_list",r,dl.download_sanbao_pdf_detail_page,lock)) for _ in range(configs["thread_num"])])

    # 利用上面解析的pdf_url数据，下载pdf
    threading_list.extend([Thread(target=download_pdf_file, args=("pdf_url_list",r,dl.down_pdf_with_tqdm,lock)) for _ in range(configs["thread_num"])])

    success_num, fail_num = get_success_and_fail_num()


    print("爬虫进行中请稍等")
    for thread in threading_list:
        thread.start()
        if int(success_num) + int(fail_num) == 0:
            time.sleep(1)

    for thread in threading_list:
        thread.join()

    success_num,fail_num = get_success_and_fail_num()
    print("爬取完成，一共%s条数据，成功了%s条，失败了%s条" %(str(int(success_num)+int(fail_num)),str(success_num),str(fail_num)))


