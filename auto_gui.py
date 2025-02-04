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
        self.h, self.w = pyautogui.size()  # 屏幕大小
        self.ocr = ocr_class()

    def auto_gui(self):
        logging.info('--------------------auto_gui--------------------')
        # 桌面
        pyautogui.moveTo(1, 1, duration=0)
        pyautogui.hotkey('win', 'd')
        time.sleep(0.2)
        # 打开软件
        x, y = self._find_click(self.yaml_dict['匹配图片']['同花顺_任务栏'])  # 已存在
        if x is None:  # 不存在，重新打开
            x, y = self._find_click(self.yaml_dict['匹配图片']['同花顺_桌面'], click=2)
            time.sleep(3)
        if x is None:
            raise
        # 放大页面
        self._find_click(self.yaml_dict['匹配图片']['页面放大'])
        # 自选
        self._find_click(self.yaml_dict['匹配图片']['自选'])
        # 涨幅
        x, y = self.image_location(self.yaml_dict['匹配图片']['涨幅'])
        if x is None:
            raise
        # 上证指数
        self._find_click(self.yaml_dict['匹配图片']['上证指数'])

    def _state_judge(self):  # 检查软件状态
        # 桌面
        pyautogui.moveTo(1, 1, duration=0)
        pyautogui.hotkey('win', 'd')
        time.sleep(0.2)
        # 检查软件状态
        try:  # 已经打开
            self._find_click(self.yaml_dict['匹配图片']['软件_任务栏'], click=2)
        except:  # 重新启动
            self._find_click(self.yaml_dict['匹配图片']['软件'])
        # 位于第1个页面
        x, y = self.image_location(path1, retry=3)
        if x is not None:
            return None
        # 位于第2个页面
        x, y = self.image_location(path2, retry=3)
        if x is not None:
            return None

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
        plt.gca().xaxis.set_major_locator(MultipleLocator(50))
        plt.gca().yaxis.set_major_locator(MultipleLocator(50))
        plt.show()


if __name__ == '__main__':
    # logging.basicConfig(filename='log.log', level=logging.INFO, encoding='utf-8',
    #                     format='%(asctime)s | %(levelname)s | %(message)s')
    model = auto_gui_class(yaml_path='config/auto_gui.yaml')
    model.screenshot_measure()
    model.auto_gui()
    pass
