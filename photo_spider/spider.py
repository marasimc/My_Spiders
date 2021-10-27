import feapder
from lxml import etree
import os
import re

class test(feapder.AirSpider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = {}     # 最大的那个目录

    __custom_setting__ = dict(
        SPIDER_THREAD_COUNT = 1,  # 爬虫并发数
        SPIDER_SLEEP_TIME = [3,6],  # 下载时间间隔 单位秒。 支持随机 如 SPIDER_SLEEP_TIME = [2, 5] 则间隔为 2~5秒之间的随机数，包含2和5
        USE_SESSION = True
    )


    def start_requests(self):
        
        yield feapder.Request('https://www.sketchuptextureclub.com/textures')
    

    def parse(self, request, response):
        '''
        '''
        title = response.xpath('//ul[@id="browser"]/li').extract()

        # print(title)

        for cnt in range(len(title)):
            """爬取一级目录"""
            first_title_content = etree.HTML(title[cnt])
            first_name = first_title_content.xpath("//span/a/text()")[0]
            print(first_name)
            if not os.path.exists(str(first_name)):
                os.mkdir(str(first_name))

            second_title = response.xpath('//ul[@id="browser"]/li['+str(cnt+1)+']/ul/li').extract()
            print(second_title)
            # print('url:', first_title_content.xpath("//span/a/@href")[0])

            if len(second_title)==0:   # 若没有第二级目录则直接爬取并存储
                url = first_title_content.xpath("//span/a/@href")[0]
                yield feapder.Request(url, callback=self.parse_photo, dir_path=first_name)

            else:
                """爬取二级目录"""
                for cnt_1 in range(len(second_title)):
                    second_title_content = etree.HTML(second_title[cnt_1])
                    # second_title_content = second_title[cnt_1]
                    second_name = second_title_content.xpath("//span/a/text()")[0]
                    print(second_name)
                    now_path = first_name + '/' + second_name
                    if not os.path.exists(now_path):
                        os.mkdir(now_path)
                    
                    # third_title = second_title_content.xpath("//ul/li")
                    third_title = response.xpath('//ul[@id="browser"]/li['+str(cnt+1)+']/ul/li['+str(cnt_1+1)+']/ul/li').extract()

                    if len(third_title)==0: # 若没有三级目录则进行存储
                        url = second_title_content.xpath("//span/a/@href")[0]
                        yield feapder.Request(url, callback=self.parse_photo, dir_path=now_path)
                    
                    else:
                        """爬取三级目录"""
                        for cnt_2 in range(len(third_title)):
                            third_title_content = etree.HTML(third_title[cnt_2])
                            # third_title_content = third_title[cnt_2]
                            third_name = third_title_content.xpath("//span/a/text()")[0]
                            now_path = first_name+'/'+second_name+'/'+third_name
                            if not os.path.exists(now_path):
                                os.mkdir(now_path)
                            
                            # fourth_title = third_title_content.xpath("//ul/li")
                            fourth_title = response.xpath('//ul[@id="browser"]/li['+str(cnt+1)+']/ul/li['+str(cnt_1+1)+']/ul/li['+str(cnt_2+1)+']/ul/li').extract()

                            if len(fourth_title)==0:   # 若没有四级目录则进行存储
                                url = third_title_content.xpath("//span/a/@href")[0]
                                yield feapder.Request(url, callback=self.parse_photo, dir_path=now_path)
                            
                            else:
                                """爬取四级目录"""
                                for cnt_3 in range(len(fourth_title)):
                                    fourth_title_content = etree.HTML(fourth_title[cnt_3])
                                    # fourth_title_content = fourth_title[cnt_3]
                                    fourth_name = fourth_title_content.xpath("//span/a/text()")[0]
                                    now_path = first_name+'/'+second_name+'/'+third_name+'/'+fourth_name
                                    if not os.path.exists(now_path):
                                        os.mkdir(now_path)
                                    
                                    url = fourth_title_content.xpath("//span/a/@href")[0]
                                    yield feapder.Request(url, callback=self.parse_photo, dir_path=now_path)





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
            # img_src = img_content.xpath("//img[1]/@src")[0]
            img_src = re.sub(r'public/texture', r'public/texture_m', img_src)

            img_name = dir_path + '/' + str(img_name)+'.jpg'

            img_src = str(img_src)
            
            # print(img_src)

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
    test(thread_count = 1).start()
