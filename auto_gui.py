import re
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
        # 屏幕大小
        self.w, self.h = pyautogui.size()
        # 截图文字检测
        self.ocr = ocr_class()
        # 常量
        self.axis = {'桌面': {}, '首页': {}, '自选': {}, '分时': {}}  # 中心坐标：{name1:{name2:(x,y)}}
        self.screenshot = {'桌面': {}, '首页': {}, '自选': {}, '分时': {}}  # 截图坐标：{name1:{name2:(x1,y1,w,h)}}
        self.regex = {'桌面': {}, '首页': {}, '自选': {}, '分时': {}}  # 提取数字的正则表达式
        for key in self.yaml_dict.keys():
            for name in self.yaml_dict[key].keys():
                if 'regex' in name:
                    self.regex[key][name] = re.compile(self.yaml_dict[key][name])
        # 变量
        self.result = {}
        # 监测股票
        self.name_list = ['上证指数', '国债指数']

    def auto_gui(self, name_list=None):
        logging.info('--------------------auto_gui--------------------')
        # 初始化
        self.init()
        # 获取监测股票的信息
        self._monitor_data()
        return

    def init(self):
        # 回到桌面
        pyautogui.moveTo(1, 1, duration=0)
        pyautogui.hotkey('win', 'd')
        time.sleep(0.2)
        # 打开软件
        try:  # 已存在，直接打开
            self._find_click(self.yaml_dict['桌面']['同花顺_任务栏'], click=1)
        except:  # 不存在，重新打开
            self._find_click(self.yaml_dict['桌面']['同花顺_桌面'], click=2)
            time.sleep(3)  # 首次打开可能比较慢
            x, y, w, h = self.image_location(self.yaml_dict['首页']['自选'], retry=30)  # 检测是否打开
            assert x is not None
        # 放大页面
        try:
            self._find_click(self.yaml_dict['首页']['页面放大'], click=1, retry=2)
        except:
            pass
        # 收起推荐
        try:
            self._find_click(self.yaml_dict['首页']['收起推荐'], click=1, retry=2)
        except:
            pass
        # 自选
        x, y, w, h = self._find_click(self.yaml_dict['首页']['自选'], click=1)
        self.axis['首页']['自选'] = (x, y)
        # 我的板块
        x, y, w, h = self._find_click(self.yaml_dict['自选']['我的板块'], click=1)
        self.axis['自选']['我的板块'] = (x, y)
        # 滚动鼠标
        pyautogui.moveTo(x, int(y + 0.1 * self.h), duration=0)
        for i in range(10):
            time.sleep(0.1)
            pyautogui.scroll(200)
        # 监测
        x, y, w, h = self._find_click(self.yaml_dict['自选']['监测'], click=1)
        self.axis['自选']['监测'] = (x, y)

    def _monitor_data(self):  # 获取监测股票的信息
        number = 10
        image = pyautogui.screenshot(region=(int(0.27 * self.w), int(0.13 * self.h),
                                             int(0.3 * self.w), int(number * 0.025 * self.h)))
        image = np.array(image)
        h, w, _ = image.shape
        for i in range(number):
            str_ = self.ocr.ocr(image[i * h // 10:(i + 1) * h // 10])
            print(str_)
        # self.draw_image(image)

    def _analysis(self):
        message = ''
        for name in self.name_list:
            # macdfs
            diff = self.result[name]['diff']
            dea = self.result[name]['dea']
            if diff[-2] < dea[-2] and diff[-1] > dea[-1]:  # macdfs变红
                message += f'{name}：macdfs变红'
            elif diff[-2] > dea[-2] and diff[-1] < dea[-1]:  # macdfs变绿
                message += f'{name}：macdfs绿'
        if message:
            # 复制
            pyperclip.copy(message)
            # 打开微信
            x, y, w, h = self.image_location(self.yaml_dict['微信']['微信_任务栏'])
            assert x is not None
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0)
            time.sleep(0.2)
            # 粘贴
            pyautogui.hotkey('ctrl', 'v', interval=0)
            pyautogui.press('enter')  # 发送
            # 打开同花顺
            x, y = self.axis['桌面']['同花顺_任务栏']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0)
            time.sleep(0.2)

    def _find_click(self, image, click=1, retry=10):
        x, y, w, h = self.image_location(image, retry=retry)
        assert x is not None
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=click, interval=0)
        time.sleep(0.2)
        return x, y, w, h

    @staticmethod
    def image_location(image_path, confidence=0.8, retry=10):  # 匹配图片+得到位置坐标
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
            time.sleep(0.2)
        return x, y, w, h

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
        plt.imshow(np.array(image))
        plt.show()

    @staticmethod
    def str_deal(str_):
        str_ = str_.replace('%', '')
        if '-' in str_:
            float_ = -float(str_[1:])
        else:
            float_ = float(str_[1:])
        return float_


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = auto_gui_class(yaml_path='config/auto_gui.yaml')
    model.auto_gui()
    pass
