import os
import re
import ocr
import time
import yaml
import ctypes
import logging
import argparse
import datetime
import pyperclip
import pyautogui
import numpy as np

if os.getcwd() == os.path.realpath(os.path.dirname(__file__)):  # 当前目录下运行
    from block import block_class
else:
    from .block import block_class
# -------------------------------------------------------------------------------------------------------------------- #
# 功能：实时监测股票，及时提醒买卖点
# -------------------------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description='|实时监测|')
parser.add_argument('--yaml_path', default='config.yaml', type=str, help='|配置文件位置|')
args, _ = parser.parse_known_args()
args.yaml_path = os.path.dirname(__file__) + '/' + args.yaml_path  # 配置文件位置


class auto_gui_class(block_class):
    def __init__(self, args=args):
        with open(args.yaml_path, 'r', encoding='utf-8') as f:  # 配置文件
            self.yaml_dict = yaml.load(f, Loader=yaml.SafeLoader)
        # 提取数据的正则表达式
        self.regex = self.yaml_dict.pop('regex')
        for key in self.regex.keys():
            self.regex[key] = re.compile(self.regex[key])
        # 相对路径转为绝对路径
        dir_path = os.path.dirname(__file__)
        for key in self.yaml_dict:
            for name in self.yaml_dict[key]:
                self.yaml_dict[key][name] = dir_path + '/' + self.yaml_dict[key][name]
        # 文字检测模型
        self.ocr = ocr.ocr.ocr_class()
        # 屏幕大小
        self.w, self.h = pyautogui.size()
        # 坐标
        self.axis = {}  # 中心坐标：{name1:{name2:(x,y)}}
        self.screenshot = {}  # 截图坐标：{name1:{name2:(x1,y1,w,h)}}
        for key in os.listdir(f'{dir_path}/match_image'):
            self.axis[key] = {}
            self.screenshot[key] = {}
        # 结果
        self.result = {}
        # 特定时间
        date = datetime.datetime.now().date()
        self.time_start = datetime.datetime.combine(date, datetime.time(9, 15, 00))  # 集合竞价时间
        self.time_morning_open = datetime.datetime.combine(date, datetime.time(9, 30, 00))  # 早上开盘时间
        self.time_morning_close = datetime.datetime.combine(date, datetime.time(11, 30, 00))  # 早上收盘时间
        self.time_afternoon_open = datetime.datetime.combine(date, datetime.time(13, 00, 00))  # 下午开盘时间
        self.time_afternoon_close = datetime.datetime.combine(date, datetime.time(15, 00, 00))  # 下午收盘时间

    def auto_gui(self, time_interval=3):  # 实时监控
        '''
            time_interval: 获取数据的最小时间间隔(系统运行需要一定时间)
        '''
        logging.info('--------------------auto_gui--------------------')
        # 初始化
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000002)  # 防止息屏，程序结束后失效
        self._ths_init()
        # 执行任务
        while True:
            time_now = datetime.datetime.now()  # 当前时间
            # 交易时间
            if self.time_start < time_now < self.time_morning_close or \
                    self.time_afternoon_open < time_now < self.time_afternoon_close:
                start_time = time.time()
                # 获取监测股票的信息
                name = self._get_data()
                # 分析股票信息
                self._analysis(name=name)
                # 间隔
                end_time = time.time()
                # print(f'|时间：{end_time - start_time:.4f}|')
                time.sleep(max(time_interval - (end_time - start_time), 0))
            # 早上前
            elif time_now < self.time_start:
                time.sleep((self.time_start - time_now).total_seconds())
            # 中午前
            elif time_now < self.time_afternoon_open:
                time.sleep((self.time_afternoon_open - time_now).total_seconds())
            # 收盘后
            else:
                print('! 结束:已收盘 !')
                break

    def _ths_init(self):  # 同花顺初始化
        # 回到桌面
        pyautogui.hotkey('win', 'd')
        pyautogui.moveTo(1, 1, duration=0)
        time.sleep(0.5)
        # 打开软件
        try:  # 已存在，直接打开
            self.find_and_click(self.yaml_dict['桌面']['同花顺_任务栏'], click=1)
        except:  # 不存在，重新打开
            self.find_and_click(self.yaml_dict['桌面']['同花顺_桌面'], click=2)
            time.sleep(3)  # 首次打开可能比较慢
            self.image_location(self.yaml_dict['首页']['自选'], retry=50, assert_=True)  # 检测是否打开
        # 记录任务栏位置
        x, y, w, h = self.image_location(self.yaml_dict['桌面']['同花顺_任务栏'])
        self.axis['桌面']['同花顺_任务栏'] = (x, y)
        # 放大页面
        try:
            self.find_and_click(self.yaml_dict['首页']['页面放大'], click=1, retry=2)
        except:
            pass
        # 收起推荐
        try:
            self.find_and_click(self.yaml_dict['首页']['收起推荐'], click=1, retry=2)
        except:
            pass
        # 下翻
        x, y, w, h = self.image_location(self.yaml_dict['首页']['下翻'], assert_=True)
        self.axis['首页']['下翻'] = (x, y)
        # 自选
        x, y, w, h = self.find_and_click(self.yaml_dict['首页']['自选'], click=2)
        self.axis['首页']['自选'] = (x, y)
        # 我的板块
        x, y, w, h = self.find_and_click(self.yaml_dict['自选']['我的板块'], click=1)
        self.axis['自选']['我的板块'] = (x, y)
        # 滚动鼠标
        pyautogui.moveTo(x, int(y + 0.1 * self.h), duration=0)
        for i in range(10):
            time.sleep(0.1)
            pyautogui.scroll(500)
        # 监测
        x, y, w, h = self.find_and_click(self.yaml_dict['自选']['监测'], click=1)
        self.axis['自选']['监测'] = (x, y)
        # 分时图
        x, y, w, h = self.find_and_click(self.yaml_dict['自选']['分时图'], click=1)
        self.axis['自选']['分时图'] = (x, y)
        # 微信
        x, y, w, h = self.image_location(self.yaml_dict['微信']['微信_任务栏'], assert_=True)
        self.axis['微信']['微信_任务栏'] = (x, y)

    def _get_data(self):  # 获取数据
        # 涨幅截图坐标
        x1 = int(0.685 * self.w)
        y1 = int(0.081 * self.h)
        # 涨幅截图长度
        w1 = int(0.112 * self.w)
        h1 = int(0.037 * self.h)
        # macdfs截图坐标
        x2 = int(0.0505 * self.w)
        y2 = int(0.5583 * self.h)
        # macdfs截图长度
        w2 = int(0.2458 * self.w)
        h2 = int(0.0194 * self.h)
        # 下翻位置
        x, y = self.axis['首页']['下翻']
        pyautogui.moveTo(x, y, duration=0)
        # 获取数据
        image1 = np.array(pyautogui.screenshot(region=(x1, y1, w1, h1)))
        name_str = self.ocr.ocr(image1)
        search1 = self.regex['名称'].search(name_str)
        image2 = np.array(pyautogui.screenshot(region=(x2, y2, w2, h2)))
        data_str = self.ocr.ocr(image2)
        search2 = self.regex['macdfs'].search(data_str)
        if search1 is None or search2 is None:
            name = None
            if search1 is not None:
                print(f'! {str(datetime.datetime.now().time())[:5]} | 未检测到数据 | {search1.group(1)} !')
            else:
                print(f'! {str(datetime.datetime.now().time())[:5]} | 未检测到任何数据 !')
        else:
            name = search1.group(1)
            macdfs = self.str_to_float(search2.group(1))
            if self.result.get(name) is None:
                self.result[name] = {'macdfs': [], 'macdfs状态': ''}
            self.result[name]['macdfs'].append(macdfs)
        # self.draw_image(image1)
        # self.draw_image(image2)
        # 点击下翻
        pyautogui.click(button='left', clicks=1, interval=0)
        time.sleep(0.2)
        return name

    def _analysis(self, name=None):
        message = ''  # 监测信息
        name_list = [name] if name else []
        for name in name_list:
            if len(self.result[name]['macdfs']) < 3:  # 数据太少跳过
                continue
            # macdfs
            macdfs = self.result[name]['macdfs']
            state = self.result[name]['macdfs状态']
            if state != '绿区峰值' and -0.01 > macdfs[-1] > macdfs[-2] >= macdfs[-3]:  # 绿区峰值
                message += f'{name} | macdfs买点\n'
                self.result[name]['macdfs状态'] = '绿区峰值'
            elif state != '红区峰值' and 0.01 < macdfs[-1] < macdfs[-2] <= macdfs[-3]:  # 红区峰值
                message += f'{name} | macdfs卖点\n'
                self.result[name]['macdfs状态'] = '红区峰值'
            elif -0.01 < macdfs[-1] < 0.01:
                self.result[name]['macdfs状态'] = ''
        if message:  # 需要发消息
            message = f'{str(datetime.datetime.now().time())[:5]} | {message}'
            # 复制
            pyperclip.copy(message.strip())
            # 打开微信
            x, y = self.axis['微信']['微信_任务栏']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0.1)
            # 粘贴
            pyautogui.hotkey('ctrl', 'v', interval=0)
            pyautogui.press('enter')  # 发送
            # 回到同花顺
            x, y = self.axis['桌面']['同花顺_任务栏']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0.1)


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = auto_gui_class()
    model.auto_gui()
