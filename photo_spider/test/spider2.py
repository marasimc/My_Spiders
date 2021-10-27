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
            
        '''     
        """爬取一级目录"""
        title = response.xpath('//ul[@id="browser"]/li').extract()
        # print(len(title))
        for cnt in range(1, len(title)+1):
            each_response = etree.HTML(title[cnt])
            name = each_response.xpath("//span/a/text()")[0]
            url = each_response.xpath("//span/a/@href")[0]

            """爬取二级目录"""
            second_title = response.xpath('//ul[@id="browser"]/li/ul/li').extract()

            if len(second_title)==0:   # 若没有下一级目录，则创建目录并将图片爬取下来
                if not os.path.exists(str(request.name)):
                    os.mkdir(str(request.name))

                yield feapder.Request(request.url, callback=self.parse_photo, dir_path = str(request.name))

            else:
                for each_title in second_title:
                    each_response = etree.HTML(each_title)

                    name = each_response.xpath("//span/a/text()")[0]
                    url = each_response.xpath("//span/a/@href")[0]

                    self.title[request.name][name] = url





            yield feapder.Request(url, callback=self.parse_second_title, name = name)



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

            img_name = str(img_name)+'.jpg'

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