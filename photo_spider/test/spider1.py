import feapder
from lxml import etree
import os

class test(feapder.AirSpider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = {}     # 最大的那个目录


    def start_requests(self):
        # yield feapder.Request('https://www.sketchuptextureclub.com/textures/architecture/bricks/colored-bricks/rustic')
        yield feapder.Request('https://www.sketchuptextureclub.com/textures/free-pbr-textures', name='FREE PBR TEXTURES')
    

    # def parse(self, request, response):
    #     all_img = response.xpath("//div[@id='pagtexture']/div[@class='textu']/div").extract()
        
    #     for img in all_img:
    #         img_content = etree.HTML(img)

    #         img_name = img_content.xpath("//a[1]/@title")
    #         img_src = img_content.xpath("//a[1]/@data-fancybox-href")

    #         print(img_name, img_src)

    def parse(self, request, response):
        '''
            爬取二级目录
        '''
        self.title[request.name] = {}

        title = response.xpath('//ul[@id="browser"]/li/ul/li').extract()

        print(title)

        if len(title)==0:   # 若没有下一级目录，则创建目录并将图片爬取下来
            if not os.path.exists(str(request.name)):
                os.mkdir(str(request.name))

            yield feapder.Request(request.url, callback=self.parse_photo, dir_path = str(request.name))
    

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
    test().start()
