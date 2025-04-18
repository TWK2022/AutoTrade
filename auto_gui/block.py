import os
import re
import PIL
import yaml
import pyautogui
import numpy as np
from PIL import Image

# -------------------------------------------------------------------------------------------------------------------- #
# 复用模块
# -------------------------------------------------------------------------------------------------------------------- #
yaml_path_default = os.path.dirname(__file__) + '/config.yaml'  # 配置文件位置


class block_class:
    def __init__(self, yaml_path=yaml_path_default):
        with open(yaml_path, 'r', encoding='utf-8') as f:  # 配置文件
            self.image_dict = yaml.load(f, Loader=yaml.SafeLoader)
        # 提取数据的正则表达式
        self.regex = self.image_dict.pop('regex')
        for key in self.regex.keys():
            self.regex[key] = re.compile(self.regex[key])
        # 相对路径转为绝对路径
        dir_path = os.path.dirname(__file__)
        for key in self.image_dict:
            for name in self.image_dict[key]:
                self.image_dict[key][name] = dir_path + '/' + self.image_dict[key][name]
        # 屏幕大小
        self.w, self.h = pyautogui.size()
        # 坐标
        self.position = {}  # 中心坐标:{name1:{name2:(x,y)}}
        self.screenshot = {}  # 截图坐标:{name1:{name2:(x1,y1,w,h)}}
        for key in os.listdir(f'{dir_path}/match_image'):
            self.position[key] = {}
            self.screenshot[key] = {}

    def find_and_click(self, image, click=1, retry=20):
        x, y, w, h = self.image_location(image, retry=retry, assert_=True)
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=click, interval=0.1)
        return x, y, w, h

    @staticmethod
    def image_location(image_path, confidence=0.8, retry=20, assert_=False):  # 匹配图片+得到位置坐标
        def location():
            try:  # 匹配图片
                x, y = pyautogui.locateCenterOnScreen(image, confidence=confidence)
                return x, y
            except pyautogui.ImageNotFoundException:
                return None, None

        image = PIL.Image.open(image_path)
        w, h = image.size
        number = 0
        while True:
            x, y = location()
            number += 1
            if x is not None or number >= retry:
                break
        if assert_:
            assert x is not None
        return x, y, w, h

    @staticmethod
    def click_delete_input(text):  # 点击+清除+输入文本
        pyautogui.click(button='left', clicks=1, interval=0.1)
        pyautogui.hotkey('ctrl', 'a', interval=0)
        pyautogui.hotkey('ctrl', 'x', interval=0)
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v', interval=0)

    @staticmethod
    def str_to_float(str_):
        if '-' in str_:
            float_ = -float(str_[1:])
        elif '+' in str_:
            float_ = float(str_[1:])
        else:
            float_ = float(str_)
        return float_

    @staticmethod
    def draw_image(image):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(20, 20))
        plt.imshow(np.array(image))
        plt.show()

    @staticmethod
    def screenshot_measure():  # 截图+测量距离
        import matplotlib.pyplot as plt
        from matplotlib.pyplot import MultipleLocator
        image = pyautogui.screenshot()
        image = image.resize((1000, 1000))
        plt.figure(figsize=(20, 20))
        plt.imshow(image)
        plt.grid()
        plt.gca().xaxis.set_major_locator(MultipleLocator(20))
        plt.gca().yaxis.set_major_locator(MultipleLocator(20))
        plt.show()
