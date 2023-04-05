import numpy as np
import random

import requests
from selenium.webdriver import ActionChains
import time
from selenium import webdriver
from PIL import Image
import os
from selenium.webdriver.support.ui import WebDriverWait
import cv2
import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片
import torch
from torch.utils.data import DataLoader
from torch.autograd import Variable

from detector.datasets import pad_to_square,resize
from detector.models import Darknet
from detector.config import Config as DetectorConfig
from detector.utils import non_max_suppression, rescale_boxes
import torchvision.transforms as transforms

#测试次数,仅为了保存测试图片，正式使用时可以删除
TEST_COUNT = 100
#模型不大，直接在cpu上跑，也可以试试跑gpu
os.environ['CUDA_VISIBLE_DEVICES']=""

class Login(object):
    """
    腾讯防水墙滑动验证码破解
    使用OpenCV库
    https://open.captcha.qq.com/online.html
    python + seleniuum + cv2
    """
    def __init__(self, driver, url):
        # 如果是实际应用中，可在此处账号和密码
        # self.url = 'http://activity.10jqka.com.cn/acmake/cache/304.html?sessionId=221%2E4%2E34%2E152&info=&groupId=website_basic&isPc=true&reqType=&returnUrl=https%3A%2F%2Fgitee%2Ecom%2Fsmart%2Dfinance%2Fcrawler%2Fwikis%2F%25E7%2588%25AC%25E8%2599%25AB%25E9%259C%2580%25E6%25B1%2582%3Fsort%5Fid%3D4255492&acHost=%2F%2Fbasic%2E10jqka%2Ecom%2Ecn&sessionId=221%2E4%2E34%2E152&info=&groupId=website_basic&isPc=true&reqType=&returnUrl=https%3A%2F%2Fgitee%2Ecom%2Fsmart%2Dfinance%2Fcrawler%2Fwikis%2F%25E7%2588%25AC%25E8%2599%25AB%25E9%259C%2580%25E6%25B1%2582%3Fsort%5Fid%3D4255492&acHost=%2F%2Fbasic%2E10jqka%2Ecom%2Ecn'
        self.url = url
        self.driver = webdriver.Chrome()
        self.driver = driver
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = Darknet(DetectorConfig.model_def, img_size=DetectorConfig.img_size).to(self.device)
        if DetectorConfig.weights_path.endswith(".weights"):
            # Load darknet weights
            model.load_darknet_weights(DetectorConfig.weights_path)
        else:
            # Load checkpoint weights
            # model.load_state_dict(torch.load(opt.weights_path))
            model.load_state_dict(
                torch.load(DetectorConfig.weights_path, map_location="cuda" if torch.cuda.is_available() else "cpu"))
        model.eval()  # Set in evaluation mode
        self.model=model

    @staticmethod
    def show(name):
        cv2.imshow('Show', name)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def webdriverwait_send_keys(dri, element, value):
        """
        显示等待输入
        :param dri: driver
        :param element:
        :param value:
        :return:
        """
        WebDriverWait(dri, 10, 5).until(lambda dr: element).send_keys(value)

    @staticmethod
    def webdriverwait_click(dri, element):
        """
        显示等待 click
        :param dri: driver
        :param element:
        :return:
        """
        WebDriverWait(dri, 10, 5).until(lambda dr: element).click()

    def get_postion(self,chunk, canves):
        """
        判断缺口位置
        :param chunk: 缺口图片是原图
        :param canves:
        :return: distance:需要拉动的x轴像素距离
        """
        otemp = chunk #全图
        oblk = canves #缺口图
        img = transforms.ToTensor()(Image.open(otemp).convert('RGB'))

        # Pad to square resolution
        # img, _ = pad_to_square(img, 0)
        # Resize
        img = resize(img,(DetectorConfig.img_size,DetectorConfig.img_size))
        tensor = img.reshape((1, 3, DetectorConfig.img_size, DetectorConfig.img_size))
        tensor = tensor.to(self.device)
        # print(np.array(image).shape)
        with torch.no_grad():
            detections = self.model(tensor)
            detections = non_max_suppression(detections, DetectorConfig.conf_thres, DetectorConfig.nms_thres)
        detections=detections[0]
        if detections is None:
            template = cv2.imread(otemp)
            cv2.imwrite("image/detect_result_{}.jpg".format(TEST_COUNT), template)
            return 0,200
        detections=detections.cpu()
        img = np.array(Image.open(otemp))
        detections = rescale_boxes(detections, DetectorConfig.img_size, img.shape[:2])
        detections=detections.numpy()
        detections=detections[detections[:,4].argsort()]
        x1,y1,x2,y2=detections[-1].astype(int)[:4]
        template = cv2.imread(otemp)
        cv2.rectangle(template, (x1, y1), (x2, y2), (7, 249, 151), 2)
        #检测结果
        cv2.imwrite("image/detect_result_{}.jpg".format(TEST_COUNT), template)
        return y1,x1

    @staticmethod
    def get_track(distance):
        """
        模拟轨迹 假装是人在操作
        :param distance:
        :return:
        """
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.5
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8

        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(5, 10)  # 加速运动
            else:
                a = -random.randint(4, 6)  # 减速运动

            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            if current > distance:
                tracks.append(round(distance-(current-s)+2))
                break
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # 反着滑动到大概准确位置
        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 2))
        tracks.append(random.uniform(-1,1))
        return tracks

    @staticmethod
    def urllib_download(imgurl, imgsavepath):
        """
        下载图片
        :param imgurl: 图片url
        :param imgsavepath: 存放地址
        :return:
        """
        from urllib.request import urlretrieve
        urlretrieve(imgurl, imgsavepath)

    def after_quit(self):
        """
        关闭浏览器
        :return:
        """
        self.driver.quit()

    def login_main(self):
        # ssl._create_default_https_context = ssl._create_unverified_context
        driver = self.driver
        driver.maximize_window()
        driver.get(self.url)

        # click_keyi_username = driver.find_element_by_xpath("//div[@class='wp-onb-tit']/a[text()='可疑用户']")
        # self.webdriverwait_click(driver, click_keyi_username)

        # login_button = driver.find_element_by_id('code')
        # self.webdriverwait_click(driver, login_button)
        # time.sleep(1)

        # driver.switch_to.frame(driver.find_element_by_id('tcaptcha_iframe'))  # switch 到 滑块frame
        # time.sleep(0.5)
        bk_block = driver.find_element_by_id('slicaptcha-img')  # 大图
        web_image_width = bk_block.size
        web_image_width = web_image_width['width']
        bk_block_x = bk_block.location['x']

        slide_block = driver.find_element_by_id('slicaptcha-block')  # 小滑块
        slide_block_x = slide_block.location['x']

        bk_block = driver.find_element_by_id('slicaptcha-img').get_attribute('src')       # 大图 url
        slide_block = driver.find_element_by_id('slicaptcha-block').get_attribute('src')  # 小滑块 图片url
        slid_ing = driver.find_element_by_id('slider')  # 滑块

        os.makedirs('./image/', exist_ok=True)
        self.urllib_download(bk_block, 'image/bkBlock.png')
        self.urllib_download(slide_block, 'image/slideBlock.png')
        time.sleep(0.5)
        img_bkblock = Image.open('image/bkBlock.png')
        real_width = img_bkblock.size[0]
        width_scale = float(real_width) / float(web_image_width)
        position = self.get_postion('image/bkBlock.png', 'image/slideBlock.png')
        real_position = position[1] / width_scale
        real_position = real_position - (slide_block_x - bk_block_x)
        track_list = self.get_track(real_position + 4)

        ActionChains(driver).click_and_hold(on_element=slid_ing).perform()  # 点击鼠标左键，按住不放
        time.sleep(0.2)
        # print('第二步,拖动元素')
        for track in track_list:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
            time.sleep(0.002)
        # ActionChains(driver).move_by_offset(xoffset=-random.randint(0, 1), yoffset=0).perform()   # 微调，根据实际情况微调
        time.sleep(0.5)
        # print('第三步,释放鼠标')
        ActionChains(driver).release(on_element=slid_ing).perform()
        time.sleep(0.5)

        if self.url!=driver.current_url:
            #登录成功，跳转到指定页面
            return True
        else:
            #否则他会跳回原来的页面
            return False

option = webdriver.ChromeOptions()
#是否显示浏览器 如果想显示浏览器，请把这两行注释掉
# option.add_argument('--headless')
# option.add_argument('--disable-gpu')
# option.add_argument('--headless')
# option.add_argument('--no-sandbox')
# option.add_argument('--disable-dev-shm-usage')
option.add_experimental_option("excludeSwitches",["enable-logging"])
option.add_argument('ignore-certificate-errors')
option.add_argument("--ignore-certificate-error")
option.add_argument("--ignore-ssl-errors")


def Verify():
    global TEST_COUNT
    url = 'http://activity.10jqka.com.cn/acmake/cache/304.html?sessionId=221%2E4%2E34%2E152&info=&groupId=website_basic&isPc=true&reqType=&returnUrl=https%3A%2F%2Fgitee%2Ecom%2Fsmart%2Dfinance%2Fcrawler%2Fwikis%2F%25E7%2588%25AC%25E8%2599%25AB%25E9%259C%2580%25E6%25B1%2582%3Fsort%5Fid%3D4255492&acHost=%2F%2Fbasic%2E10jqka%2Ecom%2Ecn&sessionId=221%2E4%2E34%2E152&info=&groupId=website_basic&isPc=true&reqType=&returnUrl=https%3A%2F%2Fgitee%2Ecom%2Fsmart%2Dfinance%2Fcrawler%2Fwikis%2F%25E7%2588%25AC%25E8%2599%25AB%25E9%259C%2580%25E6%25B1%2582%3Fsort%5Fid%3D4255492&acHost=%2F%2Fbasic%2E10jqka%2Ecom%2Ecn'
    driver = webdriver.Chrome(options=option)
    # driver.get(url)
    login = Login(driver, url)
    # print(content)
    success_times=0
    test_time=TEST_COUNT
    for i in range(test_time):
        print('第{}次:'.format(i+1),end='\t')
        if login.login_main():
            success="success"
            success_times+=1
        else:
            success="fail"
        print(success)
        TEST_COUNT-=1
        img=mpimg.imread('image/detect_result_{}.jpg'.format(TEST_COUNT+1))
        plt.imshow(img)
        plt.title(success)
        plt.show()
    print("成功次数：{}".format(success_times))
    # while True:
    #     try:
    #         conven_concepts = driver.find_element_by_xpath("//div[@id='concept']//table[@class='gnContent']/tbody/tr")
    #         print(conven_concepts)
    #         driver.quit()
    #         print('ok')
    #         return
    #
    #     except Exception:
    #         login.login_main()
    #
    #     time.sleep(1)
    

if __name__=='__main__':
    Verify()