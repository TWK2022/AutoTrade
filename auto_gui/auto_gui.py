import os
import ocr
import time
import ctypes
import logging
import datetime
import pyperclip
import pyautogui

if os.getcwd() == os.path.realpath(os.path.dirname(__file__)):  # 当前目录下运行
    from block import block_class
else:
    from .block import block_class


# -------------------------------------------------------------------------------------------------------------------- #
# 功能:实时监测行业，及时提醒买卖点
# -------------------------------------------------------------------------------------------------------------------- #
class auto_gui_class(block_class):
    def __init__(self):
        super().__init__()
        # 文字检测模型
        self.ocr = ocr.ocr.ocr_class()
        # 结果
        self.result = {}
        # 特定时间
        date = datetime.datetime.now().date()
        self.time_start = datetime.datetime.combine(date, datetime.time(9, 15, 00))  # 集合竞价时间
        self.time_morning_open = datetime.datetime.combine(date, datetime.time(9, 30, 00))  # 早上开盘时间
        self.time_morning_close = datetime.datetime.combine(date, datetime.time(11, 30, 00))  # 早上收盘时间
        self.time_afternoon_open = datetime.datetime.combine(date, datetime.time(13, 00, 00))  # 下午开盘时间
        self.time_afternoon_close = datetime.datetime.combine(date, datetime.time(15, 00, 00))  # 下午收盘时间
        # 回到桌面
        pyautogui.hotkey('win', 'd')
        pyautogui.moveTo(1, 1, duration=0)
        time.sleep(0.5)
        # 打开软件
        try:  # 已存在，直接打开
            self.find_and_click(self.image_dict['桌面']['同花顺_任务栏'], click=1)
        except:  # 不存在，重新打开
            self.find_and_click(self.image_dict['桌面']['同花顺_桌面'], click=2)
            time.sleep(3)  # 首次打开可能比较慢
            self.image_location(self.image_dict['首页']['自选'], retry=50, assert_=True)  # 检测是否打开
        # 记录任务栏位置
        x, y, w, h = self.image_location(self.image_dict['桌面']['同花顺_任务栏'])
        self.position['桌面']['同花顺_任务栏'] = (x, y)
        # 放大页面
        try:
            self.find_and_click(self.image_dict['首页']['页面放大'], click=1, retry=2)
        except:
            pass
        # 收起推荐
        try:
            self.find_and_click(self.image_dict['首页']['收起推荐'], click=1, retry=2)
        except:
            pass
        # 下翻
        x, y, w, h = self.image_location(self.image_dict['首页']['下翻'], assert_=True)
        self.position['首页']['下翻'] = (x, y)
        # 自选
        x, y, w, h = self.find_and_click(self.image_dict['首页']['自选'], click=2)
        self.position['首页']['自选'] = (x, y)
        # 我的板块
        x, y, w, h = self.find_and_click(self.image_dict['自选']['我的板块'], click=1)
        self.position['自选']['我的板块'] = (x, y)
        # 滚动鼠标
        pyautogui.moveTo(x, int(y + 0.1 * self.h), duration=0)
        for i in range(10):
            time.sleep(0.1)
            pyautogui.scroll(500)
        # 监测
        x, y, w, h = self.find_and_click(self.image_dict['自选']['监测'], click=1)
        self.position['自选']['监测'] = (x, y)
        # 分时图
        x, y, w, h = self.find_and_click(self.image_dict['自选']['分时图'], click=1)
        self.position['自选']['分时图'] = (x, y)
        # 微信
        x, y, w, h = self.image_location(self.image_dict['微信']['微信_任务栏'], assert_=True)
        self.position['微信']['微信_任务栏'] = (x, y)
        # 名称截图
        self.screenshot['名称'] = (int(0.685 * self.w), int(0.080 * self.h), int(0.120 * self.w), int(0.035 * self.h))
        # macdfs截图
        self.screenshot['macdfs'] = (int(0.050 * self.w), int(0.559 * self.h), int(0.240 * self.w), int(0.019 * self.h))
        # 上证指数macdfs截图
        self.screenshot['macdfs_上证'] = (int(0.057 * self.w), int(0.514 * self.h),
                                        int(0.240 * self.w), int(0.019 * self.h))
        # 行业指数macdfs截图
        self.screenshot['macdfs_行业'] = (int(0.057 * self.w), int(0.548 * self.h),
                                        int(0.240 * self.w), int(0.019 * self.h))

    def auto_gui(self, time_interval=2):  # 实时监控
        '''
            time_interval: 获取数据的最小时间间隔(系统运行需要一定时间)
        '''
        logging.info('--------------------auto_gui--------------------')
        # 初始化
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000002)  # 防止息屏，程序结束后失效
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
                # print(f'|时间:{end_time - start_time:.4f}|')
                time.sleep(max(time_interval - (end_time - start_time), 0))
            # 早上前
            elif time_now < self.time_start:
                time.sleep((self.time_start - time_now).total_seconds())
            # 中午前
            elif time_now < self.time_afternoon_open:
                break
                time.sleep((self.time_afternoon_open - time_now).total_seconds())
            # 收盘后
            else:
                print('! 结束:已收盘 !')
                break

    def _get_data(self):  # 获取数据
        # 时间
        time_now = str(datetime.datetime.now().time())[:5]
        # 下翻位置
        x, y = self.position['首页']['下翻']
        pyautogui.moveTo(x, y, duration=0)
        # 名称
        image_name = pyautogui.screenshot(region=self.screenshot['名称'])
        name_str = self.ocr.ocr(image_name)
        search_name = self.regex['名称'].search(name_str)
        if search_name is None:
            print(f'! {time_now} | 未检测到名称 !')
            pyautogui.click(button='left', clicks=1, interval=0)  # 点击下翻
            time.sleep(0.2)
            return None
        name = search_name.group()
        if self.result.get(name) is None:
            self.result[name] = {'macdfs': [], 'macdfs峰值': 0.0}
        # macdfs
        if name == '上证指数':
            image_macdfs = pyautogui.screenshot(region=self.screenshot['macdfs_上证'])
        elif True:  # 行业信息
            image_macdfs = pyautogui.screenshot(region=self.screenshot['macdfs_行业'])
        else:  # 个股信息
            image_macdfs = pyautogui.screenshot(region=self.screenshot['macdfs'])
        data_str = self.ocr.ocr(image_macdfs)
        search_macdfs = self.regex['macdfs'].search(data_str)
        if search_macdfs is None:
            print(f'! {time_now} | 未检测到数据:{name} !')
            pyautogui.click(button='left', clicks=1, interval=0)  # 点击下翻
            time.sleep(0.2)
            return None
        macdfs = self.str_to_float(search_macdfs.group(1))
        self.result[name]['macdfs'].append(macdfs)
        # 点击下翻
        pyautogui.click(button='left', clicks=1, interval=0)
        time.sleep(0.2)
        # 结果
        print(f'| {time_now} | {name} | {macdfs} |')
        return name

    def _analysis(self, name=None):
        message = ''  # 监测信息
        name_list = [name] if name else []
        for name in name_list:
            if len(self.result[name]['macdfs']) < 3:  # 数据太少跳过
                continue
            # macdfs
            macdfs = self.result[name]['macdfs']
            peak_value = self.result[name]['macdfs峰值']
            if macdfs[-3] < peak_value and macdfs[-3] <= macdfs[-2] < macdfs[-1] < -0.01:  # 绿区峰值
                message += f'{name} | macdfs买点\n'
                self.result[name]['macdfs峰值'] = macdfs[-2]
            elif macdfs[-3] > peak_value and macdfs[-3] >= macdfs[-2] > macdfs[-1] > 0.01:  # 红区峰值
                message += f'{name} | macdfs卖点\n'
                self.result[name]['macdfs峰值'] = macdfs[-2]
        if message:  # 需要发消息
            message = f'{str(datetime.datetime.now().time())[:5]} | {message}'
            # 打开微信
            x, y = self.position['微信']['微信_任务栏']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0.1)
            # 复制
            pyperclip.copy(message.strip())
            # 粘贴
            pyautogui.hotkey('ctrl', 'v', interval=0)
            pyautogui.press('enter')  # 发送
            # 回到同花顺
            x, y = self.position['桌面']['同花顺_任务栏']
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click(button='left', clicks=1, interval=0.1)


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = auto_gui_class()
    model.auto_gui()
