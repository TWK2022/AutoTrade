import PIL
import time
import yaml
import logging
import pyperclip
import pyautogui
import numpy as np
from ocr import ocr_class


# -------------------------------------------------------------------------------------------------------------------- #
#
# -------------------------------------------------------------------------------------------------------------------- #
class auto_gui_class:
    def __init__(self, yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:  # 配置文件
            self.yaml_dict = yaml.load(f, Loader=yaml.SafeLoader)
        self.w, self.h = pyautogui.size()  # 屏幕大小
        self.ocr = ocr_class()
        # 常量
        self.axis = {'首页': {}, '自选': {}, '分时': {}}  # 中心坐标：{name1:{name2:(x,y)}}
        self.screenshot = {'首页': {}, '自选': {}, '分时': {}}  # 截图坐标：{name1:{name2:(x,y)}}
        # 变量
        self.value = {'涨幅': {}}

    def auto_gui(self):
        logging.info('--------------------auto_gui--------------------')
        # 初始化
        self.init()
        # 获取自选中股票的涨幅
        self.zi_xuan_zhang_fu()
        return

    def init(self):
        # 桌面
        pyautogui.moveTo(1, 1, duration=0)
        pyautogui.hotkey('win', 'd')
        time.sleep(0.2)
        # 打开软件
        x, y = self._find_click(self.yaml_dict['桌面']['同花顺_任务栏'])  # 已存在
        if x is None:  # 不存在，重新打开
            x, y = self._find_click(self.yaml_dict['桌面']['同花顺_桌面'], click=2)
            assert x is not None
            time.sleep(3)
        # 放大页面
        self._find_click(self.yaml_dict['首页']['页面放大'])
        # 首页
        x, y = self.image_location(self.yaml_dict['首页']['自选'])
        self.axis['首页']['自选'] = (x, y)
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=1, interval=0)
        time.sleep(0.2)
        # 自选
        x, y = self.image_location(self.yaml_dict['自选']['涨幅'])
        assert x is not None
        self.axis['自选']['涨幅'] = (x, y)
        # 自选_股票
        for name in ['上证指数', '微盘股', '国债指数', '证券']:
            x, y = self.image_location(self.yaml_dict['股票'][f'{name}'])
            assert x is not None
            self.axis['自选'][f'{name}'] = (x, y)
            a, b, c, d = self.yaml_dict['自选']['涨幅截图']
            self.screenshot['自选'][f'{name}_涨幅'] = (int(self.axis['自选']['涨幅'][0] + a * self.w),
                                                   int(y + b * self.h), int(c * self.w), int(d * self.h))
        # macdfs
        x, y = self.axis['自选']['上证指数']
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=2, interval=0)
        time.sleep(0.2)
        x, y = self.image_location(self.yaml_dict['分时']['macdfs'])
        self.axis['分时']['macdfs'] = (x, y)
        assert x is not None

    def zi_xuan_zhang_fu(self):  # 获取自选中股票的涨幅
        x, y = self.axis['首页']['自选']
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=1, interval=0)
        time.sleep(0.2)
        self.value['涨幅']['上证指数'] = self._zi_xuan_zhang_fu(name='上证指数')  # 上证指数
        self.value['涨幅']['微盘股'] = self._zi_xuan_zhang_fu(name='微盘股')  # 微盘股
        self.value['涨幅']['国债指数'] = self._zi_xuan_zhang_fu(name='国债指数')  # 国债指数
        self.value['涨幅']['证券'] = self._zi_xuan_zhang_fu(name='证券')  # 证券

    def _zi_xuan_zhang_fu(self, name):  # 获取自选中个股的涨幅
        pyautogui.moveTo(self.axis['自选'][f'{name}'][0], self.axis['自选'][f'{name}'][1], duration=0)  # 可视化
        image = pyautogui.screenshot(region=self.screenshot['自选'][f'{name}_涨幅'])
        value = self.ocr.ocr(np.array(image))
        return value

    def _find_click(self, image_path, click=1, retry=3):  # 匹配图片并点击
        x, y = self.image_location(image_path, retry=retry)
        if x is None:
            return None, None
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=click, interval=0)
        time.sleep(0.2)
        return x, y

    @staticmethod
    def image_location(image_path, confidence=0.8, retry=3):  # 匹配图片+得到位置坐标
        def location():
            try:  # 匹配图片
                image = PIL.Image.open(image_path)
                x, y = pyautogui.locateCenterOnScreen(image, confidence=confidence)
                return x, y
            except pyautogui.ImageNotFoundException:
                return None, None

        number = 0
        sleep = 0.2
        while number != retry:
            x, y = location()
            if x is not None:
                break
            time.sleep(sleep)
            sleep += 0.2
            number += 1
        return x, y

    @staticmethod
    def click_delete_input(text, sleep=0.2):  # 点击+清除+输入文本
        pyautogui.click(button='left', clicks=1, interval=0)
        time.sleep(sleep)
        pyautogui.hotkey('ctrl', 'a', interval=0)
        pyautogui.hotkey('ctrl', 'x', interval=0)
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v', interval=0)

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

    @staticmethod
    def draw_image(image):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(20, 20))
        plt.imshow(image)
        plt.show()


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = auto_gui_class(yaml_path='config/auto_gui.yaml')
    model.auto_gui()
    pass
