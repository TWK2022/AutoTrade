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
        # 监测股票
        self.name_list = name_list if name_list else self.name_list
        # 初始化
        self.init()
        # 获取自选中股票分时的macdfs
        self._fenshi_macdfs()
        # 获取自选中股票的涨幅
        self._zixuan_zhangfu()
        # 分析
        self._analysis()
        return

    def init(self):
        # 初始值
        for name in self.name_list:
            self.result[name] = {'diff': [0], 'dea': [0], 'macdfs': [0], '涨幅': [0]}
        # 桌面
        pyautogui.moveTo(1, 1, duration=0)
        pyautogui.hotkey('win', 'd')
        time.sleep(0.2)
        # 打开软件
        x, y, w, h = self.image_location(self.yaml_dict['桌面']['同花顺_任务栏'])
        if x is not None:  # 已存在，直接打开
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=2, interval=0)
            time.sleep(0.2)
        else:  # 不存在，重新打开
            x, y, w, h = self.image_location(self.yaml_dict['桌面']['同花顺_桌面'])
            assert x is not None
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=2, interval=0)
            time.sleep(3)  # 首次打开可能比较慢
            x, y, w, h = self.image_location(self.yaml_dict['首页']['自选'], retry=30)  # 检测是否打开
            assert x is not None
        # 任务栏位置
        x, y, w, h = self.image_location(self.yaml_dict['桌面']['同花顺_任务栏'])
        self.axis['桌面']['同花顺_任务栏'] = (x, y)
        # 放大页面
        x, y, w, h = self.image_location(self.yaml_dict['首页']['页面放大'])
        if x is not None:
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0)
            time.sleep(0.2)
        # 首页
        x, y, w, h = self.image_location(self.yaml_dict['首页']['自选'])
        self.axis['首页']['自选'] = (x, y)
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=1, interval=0)
        time.sleep(0.2)
        # 自选
        x, y, w, h = self.image_location(self.yaml_dict['自选']['涨幅'])
        assert x is not None
        self.axis['自选']['涨幅'] = (x, y)
        # 自选_股票
        for name in self.name_list:
            x, y, w, h = self.image_location(self.yaml_dict['股票'][f'{name}'])
            assert x is not None
            self.axis['自选'][f'{name}'] = (x, y)
            a, b, c, d = self.yaml_dict['自选']['涨幅截图']
            self.screenshot['自选'][f'{name}_涨幅'] = (int(self.axis['自选']['涨幅'][0] + a * self.w),
                                                   int(y + b * self.h), int(c * self.w), int(d * self.h))
        # macdfs
        x, y = self.axis['自选'][self.name_list[0]]
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=2, interval=0)
        time.sleep(0.2)
        x, y, w, h = self.image_location(self.yaml_dict['分时']['macdfs'])
        self.axis['分时']['macdfs'] = (x, y)
        assert x is not None
        a, b, c, d = self.yaml_dict['分时']['macdfs截图']
        self.screenshot['分时'][f'macdfs'] = (int(self.axis['分时']['macdfs'][0] + a * self.w),
                                            int(y + b * self.h), int(c * self.w), int(d * self.h))

    def _fenshi_macdfs(self):  # 获取自选中股票分时的macdfs
        for name in self.name_list:
            x, y = self.axis['首页']['自选']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0)
            time.sleep(0.2)
            x, y = self.axis['自选'][name]
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=2, interval=0)
            time.sleep(0.2)
            x1, y1, w, h = self.screenshot['分时']['macdfs']
            # 截图文字检测
            image = pyautogui.screenshot(region=(x1, y1, w, h))
            value = self.ocr.ocr(np.array(image))
            # 正则提取
            result = self.regex['分时']['macdfs_regex'].search(value)
            self.result[name]['diff'].append(self.str_deal(result.group(1)))
            self.result[name]['dea'].append(self.str_deal(result.group(2)))
            self.result[name]['macdfs'].append(self.str_deal(result.group(3)))
            # 可视化
            pyautogui.moveTo(x1 + w / 2, y1 + h / 2, duration=0)

    def _zixuan_zhangfu(self):  # 获取自选中股票的涨幅
        x, y = self.axis['首页']['自选']
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=1, interval=0)
        time.sleep(0.2)
        for name in self.name_list:
            x1, y1, w, h = self.screenshot['自选'][f'{name}_涨幅']
            # 截图文字检测
            image = pyautogui.screenshot(region=(x1, y1, w, h))
            value = self.str_deal(self.ocr.ocr(np.array(image)))
            self.result[name]['涨幅'].append(value)
            # 可视化
            pyautogui.moveTo(x1 + w / 2, y1 + h / 2, duration=0)

    def _analysis(self):
        message = '1'
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
