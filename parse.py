#!user/bin/env python3
# -*- coding: UTF-8 -*-

"""
汽车三包项目
@Time : 2021/1/21 11:15
@File : parse.py
@Software: PyCharm
@author: 王伟 A21036

         parse功能。
        说明：
        1、完成页面的解析工作
            1.1 主页面的总页数的解析
            1.2 主页面三包信息首页的解析，获取三包首页信息url的列表
            1.3 三包首页信息具体某个url的解析
            1.4 解析三包详情页最后获取pdf的链接
"""
from bs4 import BeautifulSoup
import re


class Parse(object):
    def parse_main_page_get_total_pagenum(self,html):
        """
        获取首页的总页数，用于构建url_list
        :param html: 首页的下载的数据
        :return: 总页数
        """
        soup = BeautifulSoup(html, "lxml")
        pattern = r"第1/(\d+)页"
        all_str = str(soup.select(".dateTable")[2].select("td")[0])
        return int(re.search(pattern, all_str, re.M | re.I).group(1))

    def parse_main_page_get_detail_page_url(self,html):
        """
        用于获取详情页的url
        :param html: 下载下来的网页页面的数据
        :return: 详情页面的detial_url_list
        """
        soup = BeautifulSoup(html, "lxml")
        tr_list = soup.select("#mytable tr")[1:]
        new_url_list = []
        for tr in tr_list:
            href_list = tr.select("[name=\"tpc\"]")[0]["href"]
            if href_list.count("(") != 1:
                pattern = r"totesttpc\((.+)\)"
                href_list = re.search(pattern,href_list).group(1).split(",")
            else:
                href_list = href_list.split("(")[1].replace(")", "").split(",")

            href_list[0] = "author=" + href_list[0].replace("'", "")
            href_list[1] = "brand=" + href_list[1].replace("'", "")
            href_list[2] = "vehiceSeries=" + href_list[2].replace("'", "")
            href_list[3] = "typeName=" + href_list[3].replace("'", "")
            href_list[4] = "typecode=" + href_list[4].replace("'", "")
            href_list.insert(0, "https://www.qcsanbao.cn/webqcba/CarModelsServlet?method=getCarModels")
            new_url = "&".join(href_list)
            new_url_list.append(new_url)
        return new_url_list

    def parse_detail_page_get_url(self,html):
        """
        获取详情页的三包页面的url
        :param html: 详情页的html
        :return: 三包页面的url
        """
        soup = BeautifulSoup(html, "lxml")
        base_url = "https://www.qcsanbao.cn/webqcba/"
        td = soup.select(".tdBg")[0].select("td")[7].select("a")[0].get("target")
        new_url = base_url + td
        return new_url

    def parse_detail_page_get_pdf_url(self,html):
        """
        解析三包详情页面最后获得pdf的下载url列表
        :param html: 三包详情页的地址
        :return: pdf的下载url的列表
        """
        soup = BeautifulSoup(html, "lxml")
        tr_list = soup.select(".formTable tr")[6:10]
        base_url = "https://sanbaobeian.dpac.org.cn"
        pdf_url_list = []
        for tr in tr_list:
            try:
                href = tr.select("a")[0].get("href").split("'")[1]
                pdf_url = base_url + href
                pdf_url_list.append(pdf_url)
            except:
                href = ""
        return pdf_url_list



