import PIL
import pyautogui
import numpy as np
from PIL import Image


class block_class:
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
