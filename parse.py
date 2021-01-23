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
from tools import get_logger
import traceback

logger = get_logger()


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
        # return int(re.search(pattern, all_str, re.M | re.I).group(1))
        return 4

    def parse_main_page_get_detail_page_url(self,url,html,r):
        """
        用于获取详情页的url
        :param html: 下载下来的网页页面的数据
        :return: 详情页面的detial_url_list
        """
        soup = BeautifulSoup(html, "lxml")
        tr_list = soup.select("#mytable tr")[1:]
        new_url_list = []
        try:
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
                if r.sadd("all_detail_url_list",new_url):
                    r.sadd("detail_url_list",new_url)
        except:
            logger.info(url + " 解析失败" + traceback.format_exc().replace("\n", " "))
        finally:
            return r

    def parse_detail_page_get_url(self,url,html,r):
        """
        获取详情页的三包页面的url
        :param html: 详情页的html
        :return: 三包页面的url
        """
        soup = BeautifulSoup(html, "lxml")
        base_url = "https://www.qcsanbao.cn/webqcba/"
        try:
            td = soup.select(".tdBg")[0].select("td")[7].select("a")[0].get("target")
            new_url = base_url + td
            if r.sadd("all_sanbao_info_url_list", new_url):
                r.sadd("sanbao_info_url_list", new_url)
        except:
            logger.info(url + " 解析失败" + traceback.format_exc().replace("\n", " "))
        finally:
            return r


    def parse_detail_page_get_pdf_url(self,url,html,r):
        """
        解析三包详情页面最后获得pdf的下载url列表
        :param html: 三包详情页的地址
        :return: pdf的下载url的列表
        """
        soup = BeautifulSoup(html, "lxml")
        tr_list = soup.select(".formTable tr")[6:10]
        tr_car_name = soup.select(".formTable tr")[2].select("td")[1].get_text()
        tr_car_type = soup.select(".formTable tr")[2].select("td")[3].get_text()
        html_base_url = "https://www.qcsanbao.cn/webqcba/ThreeServlet?method=getFiles&urls="
        pdf_base_url = "https://sanbaobeian.dpac.org.cn"
        for tr in tr_list:
            try:
                href = tr.select("a")[0].get("href").split("'")[1]
                pdf_url = pdf_base_url + href
                html_url = html_base_url + href
                info = tr.select("a")[0].get_text().strip()
                pdf_url_info = tr_car_name + "#@#" + tr_car_type + "#@#" + info +"#@#" + html_url
                if r.sadd("all_pdf_download_page_url_list",pdf_url_info):
                    r.sadd("pdf_download_page_url_list",pdf_url_info)
                if r.sadd("all_pdf_url_list", pdf_url):
                    r.sadd("pdf_url_list", pdf_url)
            except:
                logger.info(url + " 解析失败" + traceback.format_exc().replace("\n", " "))
        return r

if __name__ == '__main__':
    import tools
    from download import Download
    r = tools.get_redis_connect()
    par = Parse()
    url ="https://www.qcsanbao.cn/webqcba/ThreeServlet?method=getThree&author=11e3-0fee-3b082796-9506-b9174d954819&qualityClauseName=GZQCJTCYC质量担保条款20191205002&brand=传祺&vehiceSeries=传祺GS8&typename=390T AT 两驱 豪华智联（纵擎版）&typecode=GAC6480J2P6B"
    dl = Download()
    par.parse_detail_page_get_pdf_url(url,dl.download_first_page(url),r)




