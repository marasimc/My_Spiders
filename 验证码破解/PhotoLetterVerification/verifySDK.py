from ocr import ddddocr
from PIL import Image
import cv2
import numpy as np


class verify():
    def __init__(self):
        self.sdk = ddddocr.DdddOcr(show_ad=False)

    def binarizing(self, img, threshold):
        """ 
            传入 image 对象进行灰度、二值处理 
        """
        # 1. ddddocr处理图片前会将图片高度转换为64，因此这里先将图片高度转换为64
        scale = img.shape[0] * 1.0 / 64
        w = img.shape[1] / scale
        w = int(w)
        img = cv2.resize(img,(w, 64), interpolation=cv2.INTER_LANCZOS4)   ## 基于8*8像素邻域的Lanczos差值法
        img = np.array(img, dtype=np.uint8)
        
        # 2. 取出噪声
        # img = cv2.GaussianBlur(img, (3, 3), 0)  # 高斯滤波函数
        # img = cv2.medianBlur(img, 3)  # 中值滤波函数
        img = cv2.bilateralFilter(img, 3, 560, 560)  # 双边滤波函数
        
        img = Image.fromarray(img)
        
        # 3. 将图片转换为灰度图
        img = img.convert("L") # 转灰度
        pixdata = img.load()
        w, h = img.size
        # 遍历所有像素，大于阈值的为黑色
        for y in range(h):
            for x in range(w):
                if pixdata[x, y] < threshold:
                    pixdata[x, y] = 0
                else:
                    pixdata[x, y] = 255
        return img

    def photo2result(self, img_path):
        '''
            对图片进行ocr得到结果
            @param:  img_path -> 图片路径
            @return: result / None
        '''
        img = cv2.imread(img_path)
        imag = self.binarizing(img, 180)
        result = self.sdk.classification(imag)
        result = str(result).upper()
        
        # 若result长度不为4，说明识别出错
        if len(result) != 4:
            return None
        # 若result中含有数字，判定为识别出错
        for item in result:
            if item.isdigit(): 
                return None
        
        return result
        




if __name__ == '__main__':
    photo2result_sdk = verify()
    
    for i in range(1, 13):
        img_path = 'verify.png'

        result = photo2result_sdk.photo2result(img_path)
        print(result)

