import os
import ocr
import time
import argparse
import pyperclip
import pyautogui
import pandas as pd

if os.getcwd() == os.path.realpath(os.path.dirname(__file__)):  # 当前目录下运行
    from block import block_class
else:
    from .block import block_class

# -------------------------------------------------------------------------------------------------------------------- #
# 功能：将read_path文件中的内容添加到同花顺自定义板块中
# 运行条件：进入要添加到自定义板块中，再返回代码并运行
# -------------------------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description='|添加股票|')
parser.add_argument('--read_path', default='国产操作系统.csv', type=str, help='|要添加的文件名.csv|')
args_default, _ = parser.parse_known_args()
args_default.read_path = os.path.dirname(os.path.dirname(__file__)) + '/dataset/industry/' + args_default.read_path


class stock_add_class(block_class):
    def __init__(self, args=args_default):
        super().__init__()
        df = pd.read_csv(args.read_path)
        self.name = df['股票'][::-1]  # 倒序，涨幅大的放前面
        # 文字检测模型
        self.ocr = ocr.ocr.ocr_class()
        # 回到桌面
        pyautogui.hotkey('win', 'd')
        pyautogui.moveTo(1, 1, duration=0)
        time.sleep(0.5)
        # 进入同花顺
        self.find_and_click(self.image_dict['桌面']['同花顺_任务栏'], click=1)
        # 添加股票
        x, y, w, h = self.image_location(self.image_dict['自选']['添加股票'], assert_=True)
        self.position['自选']['添加股票'] = (x, y)
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=1, interval=0)
        # 操作
        x, y, w, h = self.image_location(self.image_dict['自选']['操作'], assert_=True)
        self.position['自选']['操作'] = (x, y)
        # 加股票
        self.screenshot['自选']['加股票'] = \
            (int(x - self.w * 0.015), int(y + self.h * 0.03), int(0.035 * self.w), int(0.03 * self.h))
        self.click_position = (x, y + int(0.05 * self.h))  # 加股票点击位置
        # 搜索框
        x, y, w, h = self.image_location(self.image_dict['自选']['搜索框'], assert_=True)
        self.position['自选']['搜索框'] = (x, y)
        # 图片识别导入
        x, y, w, h = self.image_location(self.image_dict['自选']['图片识别导入'], assert_=True)
        self.position['自选']['图片识别导入'] = (x, y)
        # 清空搜索
        self.position['自选']['清空搜索'] = (int(x - self.w * 0.015), y)
        # 关闭添加
        x, y, w, h = self.image_location(self.image_dict['自选']['关闭添加'], assert_=True)
        self.position['自选']['关闭添加'] = (x, y)

    def stock_add(self):  # 获取股票的公司信息
        for name in self.name:
            # 搜索框
            x, y = self.position['自选']['搜索框']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0)
            # 复制
            pyperclip.copy(name)
            # 粘贴
            pyautogui.hotkey('ctrl', 'v', interval=0)
            pyautogui.press('enter')  # 发送
            # 添加股票
            image = pyautogui.screenshot(region=self.screenshot['自选']['加股票'])
            str_ = self.ocr.ocr(image).strip()
            if str_ == '加股票':  # 加股票
                x, y = self.position['自选']['加股票']
                pyautogui.moveTo(x, y, duration=0)
                pyautogui.click(button='left', clicks=1, interval=0)
            # 清空搜索
            x, y = self.position['自选']['清空搜索']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0)
            time.sleep(0.1)
        # 关闭添加
        x, y = self.position['自选']['关闭添加']
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click(button='left', clicks=1, interval=0)


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = stock_add_class()
    model.stock_add()
