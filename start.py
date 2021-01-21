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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', "--url", type=str, default='https://www.qcsanbao.cn/webqcba/DVMProducerServlet?method=getWhereList&p=1', help="要爬取的网站")
    args = parser.parse_args()
    url = args.url
    base_url = "https://www.qcsanbao.cn/webqcba/DVMProducerServlet?method=getWhereList&p="
    dl = Download()
    par = Parse()
    detail_url_list = []
    url_list = make_url_list(base_url,par.parse_main_page_get_total_pagenum(dl.download_first_page(url)))
    for url in url_list[:3]:
        detail_url_list.extend(par.parse_main_page_get_detail_page_url(dl.download_first_page(url)))

    sanbao_detail_url_list = []
    for detail_url in detail_url_list:
        sanbao_detail_url_list.append(par.parse_detail_page_get_url(dl.download_first_page(detail_url)))

    pdf_url_list = []
    for sanbao_detail_url in sanbao_detail_url_list:
        pdf_url_list.extend(par.parse_detail_page_get_pdf_url(dl.download_first_page(sanbao_detail_url)))

    pdf_url_list = list(set(pdf_url_list))
    print("开始下载pdf")
    for pdf_url in pdf_url_list:
        dl.down_pdf_with_tqdm(pdf_url)
        print(pdf_url,"已经下载完成")



