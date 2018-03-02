import scrapy
from bs4 import BeautifulSoup
import re
import os
import json


class XywySpider(scrapy.Spider):
    name = "xywy"
    start_urls = ["http://zzk.xywy.com/"]


    def parse(self, response):

        soup = BeautifulSoup(response.body, 'lxml')
        ks = soup.find_all('ul', class_="illness-list clearfix")[0]

        clean_ks = [x for x in ks.get_text().split('\n') if x != '']

        place_holder = ''
        sub_place_holder = ''
        ks_dic = {}

        for e in clean_ks:
            if '>' in e:
                place_holder = e.strip('>')
            elif '|' in e:
                sub_place_holder = e.strip('|')
            else:
                ks_dic[e] = [place_holder, sub_place_holder]

        print(len(ks_dic))
        for href in response.xpath('//ul[@class = " illness-ks-list fr clearfix"]//a'):
            if href is not None:
                next_link = href.xpath('@href').extract()[0]
                next_page = response.urljoin(next_link)
                phenom = href.xpath('text()').extract()[0]
                yield scrapy.Request(next_page, callback=self.parse_illness, meta={'ks_1': ks_dic[phenom][0], 'ks_2': ks_dic[phenom][1]})

    def parse_jieshao(self, response):
        phenom = response.xpath('//div[@class="jb-name fYaHei gre"]/text()').extract_first()
        ver_name = response.meta.get('ver_name')
        jieshao_name = response.meta.get('file_name')
        dir_path = response.meta.get('dir')
        if phenom != ver_name:
            print("Found unmatched web page!!")
            return

        curret_href = response.xpath('//li[@class="current"]/a/@href').extract()[0]

        tags = response.xpath('//ul[@class="zz-nav-list clearfix"]/li/a').extract()

        output = {}

        for tag in tags:
            soup = BeautifulSoup(tag, "lxml")

            link = soup.find('a', href=True)['href']
            file_name = os.path.join(dir_path, re.split('.html',link)[0].strip('/') + '.txt')

            output[soup.get_text().strip()] = file_name

            next_page = re.sub(curret_href, link, response.url)
            yield scrapy.Request(next_page, callback=self.parse_subpage, meta={'ver_name':phenom, 'file_name': file_name})

        with open(jieshao_name, 'w+', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False)



    def parse_subpage(self, response):
        phenom = response.xpath('//div[@class="jb-name fYaHei gre"]/text()').extract_first()
        ver_name = response.meta.get('ver_name')
        file_name = response.meta.get('file_name')
        if phenom != ver_name:
            print("Found unmatched web page!!")
            return

        soup = BeautifulSoup(response.body, "lxml")

        output = [p.get_text().strip() for p in soup.find_all('p')]

        with open(file_name, 'w+', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False)



    def parse_illness(self, response):
        phenom = response.xpath('//div[@class="jb-name fYaHei gre"]/text()').extract_first()
        phen_val = []
        ks_1 = response.meta.get('ks_1')
        ks_2 = response.meta.get('ks_2')
        ks = [ks_1, ks_2]
        hrefs = response.xpath('//ul[@class="dep-nav f14 clearfix"]/li/a/@href').extract()

        dir_name = re.split('_', hrefs[0])[0]

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        jieshao = response.xpath('//ul[@class="dep-nav f14 clearfix"]/li/a/text()').extract()[1]
        yao = response.xpath('//ul[@class="dep-nav f14 clearfix"]/li/a/text()').extract()[4]

        jieshao_name = os.path.join(dir_name, re.split('.html',hrefs[1])[0] + '.json')
        yao_name = os.path.join(dir_name, re.split('.html',hrefs[4])[0] + '.txt')

        for ill in response.xpath('//li[@class="loop-tag-name mr20"]/a/text()'):
            ill_name = ill.extract()
            if ill_name is not None:
                phen_val.append(ill_name)
        yield{
            phenom: phen_val,
            jieshao: jieshao_name,
            yao: yao_name,
            '科室': ks
        }

        curret_href = response.xpath('//li[@class="current"]/a/@href').extract()[0]
        if curret_href in hrefs:
            jieshao_page = re.sub(curret_href, hrefs[1], response.url)
            yao_page = re.sub(curret_href, hrefs[4], response.url)

            yield scrapy.Request(jieshao_page, callback=self.parse_jieshao, meta={'ver_name': phenom, 'file_name': jieshao_name, 'dir': dir_name})
            yield scrapy.Request(yao_page, callback=self.parse_subpage, meta={'ver_name': phenom, 'file_name': yao_name})

