from scrapy import Spider, Request
from tele.items import TeleItem
import re
import math
import numpy as np

class TeleSpider(Spider):
    name = "Telespider"
    allowed_urls = ['https://www.bestbuy.com/']
    #start_urls = ['https://www.bestbuy.com/site/tvs/all-flat-screen-tvs/']
    start_urls = ['https://www.bestbuy.com/site/tvs/all-flat-screen-tvs/abcat0101001.c?id=abcat0101001']    
    def parse(self, response):
        # Find the total number of pages in the result so that we can decide how many urls to scrape next
        text = response.xpath('//div[@class="left-side"]/span/text()').extract_first()
        num_per_page, total_number = [int(x) for x in re.findall('\d+', text)][1:]
        #number_pages = total // per_page
        total_pages = math.ceil(total_number / num_per_page)


         # List comprehension to construct all the urls
        result_urls = ['https://www.bestbuy.com/site/tvs/all-flat-screen-tvs/abcat0101001.c?cp={}&id=abcat0101001'.format(x) for x in range(1, total_pages)]

        for url in result_urls:
            yield Request(url=url, callback=self.parse_result_page)

    def parse_result_page(self,response):
        #response.xpath('//div[@class="sku-title"]/h4/a/@href').extract()
        #why do I get the same results from both of these
        product_urls =  response.xpath('//h4[@class="sku-header"]/a/@href').extract()
        product_urls = ['https://www.bestbuy.com' + s for s in product_urls]
        #print(len(product_urls))
        #print('=' * 50)

        for url in product_urls:
            yield Request(url=url, callback=self.parse_product_page)

    def parse_product_page(self,response):


        price = response.xpath('//div[@class="priceView-hero-price priceView-customer-price"]/span/text()').extract()[1]

        avgrating = response.xpath('//span[@class="c-review-average"]/text()').extract()[0]

        title = response.xpath('//h1[@class="heading-5 v-fw-regular"]/text()').extract_first()

        brand = title.split("-")[0].strip()
        size = title.split("-")[1].strip()[0:2]

        #re.findall('\d+', avgrating)
        #this gets the 2 numbers from avg rating so for example if its 4.8 would print['4', '8']
        #In [40]: int(re.findall('\d+', avgrating)[1])    Out[40]: 8
        item = TeleItem()
        item['brand'] = brand
        item['size'] = size 
        item['avgrating'] = avgrating
        item['price'] = price

        yield item