import feapder
from feapder.db.mongodb import MongoDB
import datetime
from lxml import etree
import re
import time
from copy import deepcopy
import os



class photo_Spider(feapder.AirSpider):
    '''
        图片爬取,最多有四级目录
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = {}     # 最大的那个目录



    def start_requests(self):
        '''
            爬取首页目录
        '''
        yield feapder.Request('https://www.sketchuptextureclub.com/textures')

    
    def parse(self, request, response):
        '''
            爬取一级目录
        '''     
        title = response.xpath('//ul[@id="browser"]/li').extract()
        # print(len(title))
        for each_title in title:
            each_response = etree.HTML(each_title)
            name = each_response.xpath("//span/a/text()")[0]
            url = each_response.xpath("//span/a/@href")[0]

            yield feapder.Request(url, callback=self.parse_second_title, name = name)
        
    

    def parse_second_title(self, request, response):
        '''
            爬取二级目录
        '''
        self.title[request.name] = {}

        title = response.xpath('//ul[@id="browser"]/li/ul/li').extract()

        if len(title)==0:   # 若没有下一级目录，则创建目录并将图片爬取下来
            if not os.path.exists(str(request.name)):
                os.mkdir(str(request.name))

            yield feapder.Request(request.url, callback=self.parse_photo, dir_path = str(request.name))

        else:
            for each_title in title:
                each_response = etree.HTML(each_title)

                name = each_response.xpath("//span/a/text()")[0]
                url = each_response.xpath("//span/a/@href")[0]

                self.title[request.name][name] = url

                yield feapder.Request(url, callback=self.parse_third_title, first_title = request.name, second_title = name)

            print(self.title)


    def parse_third_title(self, request, response):
        '''
            爬取三级目录
        '''
        self.title[request.first_title][request.second_title] = {}

        title = response.xpath('//ul[@id="browser"]/li/ul/li/ul/li').extract()

        if len(title)==0:   # 若没有下一级目录，则创建目录并将图片爬取下来
            now_path = str(request.first_title) + '/' + str(request.second_name)
            if not os.path.exists(str(request.first_title)):
                os.mkdir(str(request.first_title))
            if not os.path.exists(now_path):
                os.mkdir(now_path)

            yield feapder.Request(request.url, callback=self.parse_photo, dir_path = now_path)

        else:
            for each_title in title:
                each_response = etree.HTML(each_title)

                name = each_response.xpath("//span/a/text()")[0]
                url = each_response.xpath("//span/a/@href")[0]

                self.title[request.first_title][request.second_title][name] = url

                yield feapder.Request(url, callback=self.parse_fourth_title, first_title = request.first_title, second_title = request.second_title, third_title = name)

            print(self.title)


    def parse_fourth_title(self, request, response):
        '''
            爬取四级目录
        '''
        self.title[request.first_title][request.second_title][request.third_title] = {}

        title = response.xpath('//ul[@id="browser"]/li/ul/li/ul/li/ul/li').extract()

        if len(title)==0:
            now_path = str(request.first_title) + '/' + str(request.second_title) + '/' + str(request.third_title)
            if not os.path.exists(str(request.first_title)):
                os.mkdir(str(request.first_title))
            if not os.path.exists(str(request.first_title) + '/' + str(request.second_title)):
                os.mkdir(str(request.first_title) + '/' + str(request.second_title))
            if not os.path.exists(now_path):
                os.mkdir(now_path)

            yield feapder.Request(request.url, callback=self.parse_photo, dir_path = now_path)
        
        else:
            for each_title in title:
                each_response = etree.HTML(each_title)

                name = each_response.xpath("//span/a/text()")[0]
                url = each_response.xpath("//span/a/@href")[0]

                self.title[request.first_title][request.second_title][request.third_title][name] = url

                now_path = str(request.first_title) + '/' + str(request.second_title) + '/' + str(request.third_title) + '/' + name
                if not os.path.exists(str(request.first_title)):
                    os.mkdir(str(request.first_title))
                if not os.path.exists(str(request.first_title) + '/' + str(request.second_title)):
                    os.mkdir(str(request.first_title) + '/' + str(request.second_title))
                if not os.path.exists(str(request.first_title) + '/' + str(request.second_title) + '/' + str(request.third_title)):
                    os.mkdir(str(request.first_title) + '/' + str(request.second_title) + '/' + str(request.third_title))
                if not os.path.exists(now_path):
                    os.mkdir(now_path)

                yield feapder.Request(url, callback=self.parse_photo, dir_path = now_path)

            print(self.title)


    def parse_photo(self, request, response):
        '''
            爬取图片并存储
        '''
        dir_path = request.dir_path    ## 图片存储路径

        all_img = response.xpath("//div[@id='pagtexture']/div[@class='textu']/div").extract()
        
        for img in all_img:
            img_content = etree.HTML(img)

            img_name = img_content.xpath("//a[1]/@title")[0]
            img_src = img_content.xpath("//a[1]/@data-fancybox-href")[0]

            img_name = dir_path +'/' + str(img_name)+'.jpg'

            img_src = str(img_src)

            yield feapder.Request(img_src, callback=self.parse_one_photo, img_path = img_name)
            
        
    def parse_one_photo(self, request, response):
        '''
            根据单个图片的链接爬取图片
        '''
        img_path = request.img_path
        img = response.content

        with open(img_path, 'wb') as f:
            f.write(img)


if __name__=='__main__':
    photo_Spider(thread_count = 5).start()