import os
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
        self.axis = {}  # 中心坐标：{name1:{name2:(x,y)}}
        self.screenshot = {}  # 截图坐标：{name1:{name2:(x1,y1,w,h)}}
        self.regex = self.yaml_dict.pop('regex')  # 提取数字的正则表达式
        for key in os.listdir('match_image'):
            self.axis[key] = {}
            self.screenshot[key] = {}
        for key in self.regex.keys():
            self.regex[key] = re.compile(self.regex[key])
        # 结果
        self.result = {}

    def auto_gui(self):
        logging.info('--------------------auto_gui--------------------')
        # 初始化
        self._init()
        time.sleep(1)
        for i in range(100):
            # 获取监测股票的信息
            self._monitor_data()
            # 分析股票信息
            self._analysis()
            # 间隔
            time.sleep(5)

    def _init(self):
        # 回到桌面
        pyautogui.moveTo(1, 1, duration=0)
        pyautogui.hotkey('win', 'd')
        time.sleep(0.5)
        # 打开软件
        try:  # 已存在，直接打开
            self._find_and_click(self.yaml_dict['桌面']['同花顺_任务栏'], click=1)
        except:  # 不存在，重新打开
            self._find_and_click(self.yaml_dict['桌面']['同花顺_桌面'], click=2)
            time.sleep(3)  # 首次打开可能比较慢
            x, y, w, h = self.image_location(self.yaml_dict['首页']['自选'], retry=30)  # 检测是否打开
            assert x is not None
        # 记录任务栏位置
        x, y, w, h = self.image_location(self.yaml_dict['桌面']['同花顺_任务栏'])
        self.axis['桌面']['同花顺_任务栏'] = (x, y)
        # 放大页面
        try:
            self._find_and_click(self.yaml_dict['首页']['页面放大'], click=1, retry=2)
        except:
            pass
        # 收起推荐
        try:
            self._find_and_click(self.yaml_dict['首页']['收起推荐'], click=1, retry=2)
        except:
            pass
        # 自选
        x, y, w, h = self._find_and_click(self.yaml_dict['首页']['自选'], click=1)
        self.axis['首页']['自选'] = (x, y)
        # 我的板块
        x, y, w, h = self._find_and_click(self.yaml_dict['自选']['我的板块'], click=1)
        self.axis['自选']['我的板块'] = (x, y)
        # 滚动鼠标
        pyautogui.moveTo(x, int(y + 0.1 * self.h), duration=0)
        for i in range(10):
            time.sleep(0.1)
            pyautogui.scroll(200)
        # 监测
        x, y, w, h = self._find_and_click(self.yaml_dict['自选']['监测'], click=1)
        self.axis['自选']['监测'] = (x, y)

    def _monitor_data(self, number=20):  # 获取监测股票的信息
        x1_scale = 0.27  # 截图左上角x坐标
        y1_scale = 0.13  # 截图左上角y坐标
        w_scale = 0.3  # 截图w长度
        h_scale = 0.025  # 每个数据的截图h长度
        image = pyautogui.screenshot(region=(int(x1_scale * self.w), int(y1_scale * self.h),
                                             int(w_scale * self.w), int(number * h_scale * self.h)))
        image = np.array(image)
        # self.draw_image(image)
        h, w, _ = image.shape
        for i in range(number):
            str_ = self.ocr.ocr(image[i * h // number:(i + 1) * h // number])
            value = self.regex['监测'].search(str_)
            if value is None:
                break
            name = value.group(1)
            if self.result.get(name) is None:
                self.result[name] = {'状态': '上涨', '涨幅': [], 'diff': [], 'dea': []}
                self.result[name]['状态'] = '上涨' if self.str_to_int(value.group(2)) >= 0 else '下降'
            self.result[name]['涨幅'].append(self.str_to_int(value.group(2)))
            self.result[name]['diff'].append(self.str_to_int(value.group(3)))
            self.result[name]['dea'].append(self.str_to_int(value.group(4)))

    def _analysis(self):
        macdfs_scale = 0.9  # 在满足条件前一点就触发监测
        message = ''  # 监测信息
        for name in self.result.keys():
            if len(self.result[name]['涨幅']) < 3:  # 数据太少跳过
                continue
            # 涨幅
            value = self.result[name]['涨幅']
            state = self.result[name]['状态']
            if state == '上涨' and value[-3] > value[-2] > value[-1]:  # 回落
                self.result[name]['状态'] = '下降'  # 更新状态
                message += f'\n{name}：下降'
            elif state == '下降' and value[-3] < value[-2] < value[-1]:
                self.result[name]['状态'] = '上涨'  # 更新状态
                message += f'\n{name}：上涨'
            # macdfs
            diff = self.result[name]['diff']
            dea = self.result[name]['dea']
            if diff[-2] < macdfs_scale * dea[-2] and diff[-1] > macdfs_scale * dea[-1]:  # macdfs变红
                message += f'\n{name}：macdfs变红'
            elif diff[-2] > macdfs_scale * dea[-2] and diff[-1] < macdfs_scale * dea[-1]:  # macdfs变绿
                message += f'\n{name}：macdfs绿'
        if message:  # 需要发消息
            # 复制
            pyperclip.copy(f'监测信息：{message}')
            # 打开微信
            x, y, w, h = self.image_location(self.yaml_dict['微信']['微信_任务栏'])
            assert x is not None
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0)
            time.sleep(0.2)
            # 粘贴
            pyautogui.hotkey('ctrl', 'v', interval=0)
            pyautogui.press('enter')  # 发送
            # 回到同花顺
            x, y = self.axis['桌面']['同花顺_任务栏']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0)
            time.sleep(0.2)

    def _find_and_click(self, image, click=1, retry=10):
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
    def str_to_int(str_):
        if '-' in str_:
            float_ = -float(str_[1:])
        else:
            float_ = float(str_[1:])
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


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = auto_gui_class(yaml_path='config/auto_gui.yaml')
    model.auto_gui()
    pass
