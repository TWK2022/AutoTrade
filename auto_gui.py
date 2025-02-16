import os
import re
import PIL
import time
import yaml
import logging
import datetime
import pyperclip
import pyautogui
import numpy as np
from PIL import Image
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
        # 所有鼠标操作后的时间间隔
        self.interval = 0
        # 特定时间
        date = datetime.datetime.now().date()
        self.time_start = datetime.datetime.combine(date, datetime.time(9, 15, 00))  # 集合竞价时间
        self.time_morning_open = datetime.datetime.combine(date, datetime.time(9, 30, 00))  # 早上开盘时间
        self.time_morning_close = datetime.datetime.combine(date, datetime.time(11, 30, 00))  # 早上收盘时间
        self.time_afternoon_open = datetime.datetime.combine(date, datetime.time(13, 00, 00))  # 下午开盘时间
        self.time_afternoon_close = datetime.datetime.combine(date, datetime.time(15, 00, 00))  # 下午收盘时间
        self.ocr = ocr_class()
        # 提取数据的正则表达式
        self.regex = self.yaml_dict.pop('regex')
        for key in self.regex.keys():
            self.regex[key] = re.compile(self.regex[key])
        # 中心坐标
        self.axis = {}  # 中心坐标：{name1:{name2:(x,y)}}
        # 截图坐标
        self.screenshot = {}  # 截图坐标：{name1:{name2:(x1,y1,w,h)}}
        for key in os.listdir('match_image'):
            self.axis[key] = {}
            self.screenshot[key] = {}
        # 文字检测模型
        # 结果
        self.result = {}

    def auto_gui(self, time_interval=3, interval=0.1):
        '''
            time_interval: 获取和监测数据的最小时间间隔(系统运行需要一定时间)
            interval: 所有鼠标操作后的时间间隔
        '''
        logging.info('--------------------auto_gui--------------------')
        # 初始化
        self.interval = interval
        self._init()
        # 执行任务
        while True:
            time_now = datetime.datetime.now()  # 当前时间
            # 交易时间
            if self.time_start < time_now < self.time_morning_close or \
                    self.time_afternoon_open < time_now < self.time_afternoon_close:
                start_time = time.time()
                # 获取监测股票的信息
                self._monitor_data()
                # 分析股票信息
                self._analysis()
                # 移动鼠标防止息屏
                pyautogui.moveTo(int(np.random.randint(1, 5, 1)), int(np.random.randint(1, 7, 1)))
                # 间隔
                end_time = time.time()
                # print(f'|时间：{end_time - start_time:.4f}|')
                time.sleep(max(time_interval - (end_time - start_time), 0))
            #  非交易时间
            elif time_now < self.time_start:  # 早上前
                time.sleep((self.time_start - time_now).total_seconds())
            elif time_now < self.time_afternoon_open:  # 中午前
                time.sleep((self.time_afternoon_open - time_now).total_seconds())
            else:  # 收盘后
                print('! 结束:已收盘 !')
                break

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
            x, y, w, h = self.image_location(self.yaml_dict['首页']['自选'], retry=50)  # 检测是否打开
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
        # 微信
        x, y, w, h = self.image_location(self.yaml_dict['微信']['微信_任务栏'])
        assert x is not None
        self.axis['微信']['微信_任务栏'] = (x, y)

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
        for index in range(number):
            str_ = self.ocr.ocr(image[index * h // number:(index + 1) * h // number])
            value = self.regex['监测'].search(str_)
            if value is None:
                if index == 0:
                    print('! 未检测到任何数据 !')
                break
            name = value.group(1)
            if self.result.get(name) is None:
                self.result[name] = {'状态': '', '涨幅': [], 'diff': [], 'dea': []}
                self.result[name]['状态'] = '上涨' if self.str_to_int(value.group(2)) >= 0 else '下降'
            self.result[name]['涨幅'].append(self.str_to_int(value.group(2)))
            self.result[name]['diff'].append(self.str_to_int(value.group(3)))
            self.result[name]['dea'].append(self.str_to_int(value.group(4)))

    def _analysis(self):
        macdfs_scale = 0.99  # 在满足条件前一点就触发监测
        message = ''  # 监测信息
        for name in self.result.keys():
            if len(self.result[name]['涨幅']) < 3:  # 数据太少跳过
                continue
            # 涨幅
            value = self.result[name]['涨幅']
            state = self.result[name]['状态']
            if state != '涨停' and value[-1] > 9.99:
                self.result[name]['状态'] = '涨停'
                message += f'{name}：涨停\n'
            elif state == '涨停' and value[-1] < value[-2]:
                self.result[name]['状态'] = '炸板'
                message += f'{name}：炸板\n'
            # macdfs
            diff = self.result[name]['diff']
            dea = self.result[name]['dea']
            if diff[-2] < macdfs_scale * dea[-2] and diff[-1] > macdfs_scale * dea[-1]:  # macdfs变红
                message += f'{name}：macdfs变红\n'
            elif diff[-2] > macdfs_scale * dea[-2] and diff[-1] < macdfs_scale * dea[-1]:  # macdfs变绿
                message += f'{name}：macdfs变绿\n'
        if message:  # 需要发消息
            # 复制
            pyperclip.copy(message.strip())
            # 打开微信
            x, y = self.axis['微信']['微信_任务栏']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=self.interval)
            # 粘贴
            pyautogui.hotkey('ctrl', 'v', interval=self.interval)
            pyautogui.press('enter')  # 发送
            # 回到同花顺
            x, y = self.axis['桌面']['同花顺_任务栏']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=self.interval)

    def _find_and_click(self, image, click=1, retry=20):
        x, y, w, h = self.image_location(image, retry=retry)
        assert x is not None
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=click, interval=self.interval)
        return x, y, w, h

    @staticmethod
    def image_location(image_path, confidence=0.8, retry=20):  # 匹配图片+得到位置坐标
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
        return x, y, w, h

    @staticmethod
    def click_delete_input(text, sleep=0.1):  # 点击+清除+输入文本
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
