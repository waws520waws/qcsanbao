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
from urllib.request import urlretrieve
import os
from tqdm import tqdm


class Download(object):
    def download_first_page(self,url):
        """
        下载页面，获取html文本
        :param url: 想要下载的html页面数据的url
        :return: 返回html文本
        """
        headers = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
                    'Connection': 'close'
                    }
        html = requests.get(url, headers=headers)
        return html.text


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

    def down_pdf_with_tqdm(self,url):
        """
        下载pdf,带有进度条的方式
        :param url: pdf的下载的url地址
        :return: 返回文件的总大小，不重要
        """
        dst = url.split("/")[-1]
        response = requests.get(url, stream=True)
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
        return file_size








