# -*- coding: utf-8 -*-
import scrapy
from sunning.items import SunningItem
import re
from copy import deepcopy


class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['suning.com']
    start_urls = ['http://book.suning.com/']

    def parse(self, response):
        div_list = response.xpath('//div[@class="menu-list"]/div')
        for div in div_list:
            item = {}
            item["class_big_title"] = div.xpath('.//dt//a/text()').extract_first()
            a_list = div.xpath('.//dd/a')
            for a in a_list:
                item["class_small_title"] = a.xpath('./text()').extract_first()

                item["class_small_href"] = a.xpath('./@href').extract_first()

                if item["class_small_href"] is not None:
                    yield scrapy.Request(
                        item["class_small_href"],
                        callback=self.parse_book_list,
                        meta={"item":deepcopy(item)}
                    )
    #小分类详情页
    def parse_book_list(self,response):

        item = response.meta["item"]
        book_list = response.xpath('//div[@id="filter-results"]//li')
        for book in book_list:
            item["book_href"] = book.xpath('.//a[1]/@href').extract_first()

            item["book_href"] = item["book_href"] if 'https:' in item["book_href"] else (
                        'https:' + item["book_href"])
            yield scrapy.Request(
                item["book_href"],
                callback=self.parse_book_detail,
                meta={"item":deepcopy(item)}
            )
        #翻页
        current_page = int(re.findall('\"currentPage\":\"(.*?)\"',response.body.decode("utf-8"))[0])
        pageNumbers = int(re.findall('\"pageNumbers\":\"(.*?)\"',response.body.decode("utf-8"))[0])

        if current_page < pageNumbers:
            next_url = "https://list.suning.com/1-502320-{}.html".format(current_page+1)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={"item":deepcopy(item)}
            )
        #书详情页
    def parse_book_detail(self,response):
        item = response.meta["item"]
        item["book_title"] = response.xpath('//div[@class="proinfo-title"]/h1/text()').extract_first().strip()

        yield item



