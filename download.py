#!user/bin/env python3
# -*- coding: UTF-8 -*-

"""
汽车三包项目
@Time : 2021/1/21 11:14
@File : download.py
@Software: PyCharm
@author: 王伟 A21036

         download功能。
        说明：
        1、下载网页
        2、下载三包相关的pdf
"""
import requests
import os
from tqdm import tqdm
from tools import change_success_or_fail_num,get_success_and_fail_num,get_logger,make_store_html_dir,make_store_detail_html_dir
import traceback
from bs4 import BeautifulSoup
from parse import Parse
import re
from config import configs

logger = get_logger()

class Download(object):
    def __init__(self):
        self.headers =  {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            'Connection': 'close'
        }

    def download_first_page(self,url):
        """
        下载页面，获取html文本
        :param url: 想要下载的html页面数据的url
        :return: 返回html文本
        """

        try:
            html = requests.get(url, headers=self.headers)
            num = 1
            logger.info(url+" 已经成功爬取")
            return html.text
        except Exception as e:
            num = 0
            logger.info(url + " 爬取失败" + traceback.format_exc().replace("\n"," "))
        finally:
            change_success_or_fail_num(num)
            s_num, f_num = get_success_and_fail_num()
            print(f"爬取成功了{s_num}个数据,失败了{f_num}条数据")


    def write_file(self,html_store_dir,file_name,html_str):
        """
        将获取的html的文本写入到.html文件中
        :param html_store_dir: html的存放路径
        :param file_name: 文件的名称
        :param html_str: html的文本
        :return: None
        """
        file_path = os.path.join(html_store_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_str)
        logger.info(file_name + " 已经下载完成")


    def download_list_page_html(self,url):
        """
        下载列表页的html文件，主要在这个地方需要做一件事：完成存储在同一级目录下的文件之间可以完成首页、上页、下页、末页的切换的功能
        :param url: 列表页的url
        :return: None
        """
        html = requests.get(url, headers=self.headers)
        num_str = url.split("&")[-1].split("=")[-1]
        html_text = html.text
        par = Parse()
        total_page = str(par.parse_main_page_get_total_pagenum(html.text,configs["test"]))

        pattern_fpage = "id=\"fpage\" href=\"(.+?)\""
        pattern_upage = "id=\"upage\" href=\"(.+?)\""
        pattern_npage = "id=\"npage\" href=\"(.+?)\""
        pattern_epage = "id=\"epage\" href=\"(.+?)\""

        fapge_str = re.search(pattern_fpage, html_text).group(1)
        upage_str = re.search(pattern_upage, html_text).group(1)
        npage_str = re.search(pattern_npage, html_text).group(1)
        epage_str = re.search(pattern_epage, html_text).group(1)
        if num_str == "1":
            html_text = html_text.replace(fapge_str, "#")
            html_text = html_text.replace(upage_str, "#")
            html_text = html_text.replace(npage_str, "./page"+ str(int(num_str)+1).zfill(4)+".html")
            html_text = html_text.replace(epage_str, "./page"+ total_page.zfill(4)+".html")
        elif num_str == total_page:
            html_text = html_text.replace(fapge_str, "./page0001.html")
            html_text = html_text.replace(upage_str, "./page" + str(int(num_str) - 1).zfill(4) + ".html")
            html_text = html_text.replace(npage_str, "#")
            html_text = html_text.replace(epage_str, "#")
        else:
            html_text = html_text.replace(fapge_str, "./page0001.html")
            html_text = html_text.replace(upage_str, "./page" + str(int(num_str) - 1).zfill(4) + ".html")
            html_text = html_text.replace(npage_str, "./page"+ str(int(num_str)+1).zfill(4)+".html")
            html_text = html_text.replace(epage_str, "./page"+ total_page.zfill(4)+".html")
        file_name = "page" + num_str.zfill(4) + ".html"
        html_store_dir = make_store_html_dir()
        self.write_file(html_store_dir,file_name,html_text)


    def get_typename_and_codename(self,url):
        """
        辅助函数，用于获取url中的code和name
        :param url: code详情页的url
        :return: 返回url中的code和name
        """
        name_pattern = "&typeName=(.+?)&"
        type_name = re.search(name_pattern, url,re.I).group(1)
        code_pattern = "&typecode=(.+)"
        code_name = re.search(code_pattern, url).group(1)
        return type_name,code_name

    def get_typename(self,url):
        """
        辅助函数，用于获取url中的name
        :param url: name详情页的url
        :return: 返回url中的name
        """
        name_pattern = "&typeName=(.+)"
        type_name = re.search(name_pattern, url,re.I).group(1)
        return type_name

    def download_code_page(self,url):
        """
        下载code详情页的html文件
        :param url: code详情页的url
        :return: None
        """
        html = requests.get(url, headers=self.headers)
        type_name,code_name = self.get_typename_and_codename(url)
        file_name = type_name + "_" + code_name + ".html"
        html_store_dir = make_store_html_dir()
        self.write_file(html_store_dir,file_name,html.text)

    def download_brand_page(self,url):
        """
        下载name详情页的html文件
        :param url: name详情页的url
        :return: None
        """
        html = requests.get(url, headers=self.headers)
        type_name= self.get_typename(url)
        file_name = type_name + ".html"
        html_store_dir = make_store_html_dir()
        self.write_file(html_store_dir,file_name,html.text)

    def download_sanbao_detail_page(self,url):
        """
        下载三包详情页的html文件
        :param url: 三包详情页的url
        :return: None
        """
        html = requests.get(url, headers=self.headers)
        type_name, code_name = self.get_typename_and_codename(url)
        file_name = type_name + "_" + code_name + "_detail.html"
        html_store_dir = make_store_detail_html_dir(type_name + "_" + code_name)
        self.write_file(html_store_dir, file_name, html.text)



    def download_sanbao_pdf_detail_page(self, pdf_url):
        """
        下载三包pdf下载详情页的html文件
        :param url: pdf下载详情页的url
        :return: None
        """
        type_name, code_name, info, url = pdf_url.split("#@#")
        html = requests.get(url, headers=self.headers)
        file_name = type_name + "_" + code_name + "_detail_" + info + ".html"
        html_store_dir = make_store_detail_html_dir(type_name + "_" + code_name)
        self.write_file(html_store_dir, file_name, html.text)

    def download_pdf_without_tqdm(self,url):
        """
        下载pdf,没有进度条的方式
        :param url: pdf的下载的url地址
        :return: None
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            'Connection': 'close'
        }
        html = requests.get(url, headers=headers, stream="TRUE")
        pdf_name = url.split("/")[-1]
        with open(pdf_name, 'wb') as file:
            for data in html.iter_content():
                file.write(data)

    def down_pdf_with_tqdm(self,url,dst):
        """
        下载pdf,带有进度条的方式
        :param url: pdf的下载的url地址
        :return: 返回文件是否下载完成
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            'Connection': 'close'
        }
        response = requests.get(url, headers=headers, stream="TRUE")
        file_size = int(response.headers['content-length'])
        if os.path.exists(dst):
            first_byte = os.path.getsize(dst)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return file_size

        header = {"Range": f"bytes={first_byte}-{file_size}"}

        pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=dst)
        req = requests.get(url, headers=header, stream=True)
        with open(dst, 'ab') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)
        pbar.close()
        logger.info(url + " 文件已经下载完成")
        return True






