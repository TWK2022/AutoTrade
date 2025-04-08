import os
import tqdm
import time
import argparse
import pyautogui
import numpy as np

if os.getcwd() == os.path.realpath(os.path.dirname(__file__)):  # 当前目录下运行
    from auto_gui import auto_gui_class
else:
    from .auto_gui import auto_gui_class

# -------------------------------------------------------------------------------------------------------------------- #
# 功能：自动收集同花顺某个板块中的所有股票f10信息。记录到information.txt
# 运行条件：进入要收集的行业/概念/板块，点击进入行业的第一支股票，再返回代码并运行
# 后续筛选：让大模型根据内容来筛选股票，每50个一组。如：根据以下信息，筛选出与A行业相关性很强、业绩有上涨预期的股票
# -------------------------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description='|收集信息|')
parser.add_argument('--number', default=500, type=int, help='|收集股票上限|')
parser.add_argument('--screen', default=['00', '60'], type=list, help='|保留的股票开头|')
args_default, _ = parser.parse_known_args()


class stock_information_class(auto_gui_class):
    def __init__(self, args=args_default):
        super().__init__()
        self.number = args.number
        self.screen = args.screen
        # 回到桌面
        pyautogui.hotkey('win', 'd')
        pyautogui.moveTo(1, 1, duration=0)
        time.sleep(0.5)
        # 进入同花顺
        self.find_and_click(self.yaml_dict['桌面']['同花顺_任务栏'], click=1)
        # 进入f10公司信息页面
        pyautogui.press('f10', presses=1, interval=0)
        # 下一个股
        x, y, w, h = self.image_location(self.yaml_dict['信息']['下一个股'], assert_=True)
        self.axis['信息']['下一个股'] = (x, y)
        # 公司亮点
        x, y, w, h = self.image_location(self.yaml_dict['信息']['公司亮点'], assert_=True)
        self.axis['信息']['公司亮点'] = (x, y)
        self.screenshot['信息']['公司亮点'] = (x + w // 2, y - h // 2, int((0.55 * self.w) // 2), h)
        # 主营业务
        x, y, w, h = self.image_location(self.yaml_dict['信息']['主营业务'], assert_=True)
        self.axis['信息']['主营业务'] = (x, y)
        self.screenshot['信息']['主营业务'] = (x + w // 2, y - h // 2, int((0.55 * self.w) // 2), h)

    def stock_information(self):  # 获取股票的公司信息
        for _ in tqdm.tqdm(range(self.number)):
            # 下翻位置
            x, y = self.axis['信息']['下一个股']
            pyautogui.moveTo(x, y, duration=0)
            # 等待页面刷新
            time.sleep(0.2)
            # 名称
            x, y, w, h = (int(0.448 * self.w), int(0.083 * self.h), int(0.114 * self.w), int(0.032 * self.h))
            image1 = np.array(pyautogui.screenshot(region=(x, y, w, h)))
            name_str = self.ocr.ocr(image1)
            search1 = self.regex['名称'].search(name_str)
            name = search1.group(1).strip()
            code = search1.group(2)
            if name and self.result.get(name) is not None:  # 循环了一轮
                print('| 提前结束 | 循环了一轮 |')
                break
            if code[:2] not in self.screen:  # 非目标股票
                pyautogui.click(button='left', clicks=1, interval=0)  # 下一页
                continue
            # 截图
            image = np.array(pyautogui.screenshot())
            self.result[name] = {}
            # 公司亮点
            x, y, w, h = self.screenshot['信息']['公司亮点']
            self.result[name]['公司亮点'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 主营业务
            x, y, w, h = self.screenshot['信息']['主营业务']
            self.result[name]['主营业务'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 收入
            x, y, w, h = self.image_location(self.yaml_dict['信息']['收入'], confidence=0.75)
            if x is None:  # 未检测到
                self.result[name]['收入'] = None
            else:
                x, y, w, h = (x + w // 2, y - h // 2, int((0.3 * self.w) // 2), h)
                self.result[name]['收入'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 净利润
            x, y, w, h = self.image_location(self.yaml_dict['信息']['净利润'], confidence=0.75)
            if x is None:  # 未检测到
                self.result[name]['净利润'] = None
            else:
                x, y, w, h = (x + w // 2, y - h // 2, int((0.3 * self.w) // 2), h)
                self.result[name]['净利润'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 毛利率
            x, y, w, h = self.image_location(self.yaml_dict['信息']['毛利率'], confidence=0.75)
            if x is None:  # 未检测到
                self.result[name]['毛利率'] = None
            else:
                x, y, w, h = (x + w // 2, y - h // 2, int((0.3 * self.w) // 2), h)
                self.result[name]['毛利率'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 下一页
            pyautogui.click(button='left', clicks=1, interval=0)
        # 记录
        line_all = []
        for name in self.result.keys():
            output = f'{name} | ' \
                     f'公司亮点：{self.result[name]["公司亮点"]} | ' \
                     f'主营业务：{self.result[name]["主营业务"]} | ' \
                     f'收入：{self.result[name]["收入"]} | ' \
                     f'净利润：{self.result[name]["净利润"]} | ' \
                     f'毛利率：{self.result[name]["毛利率"]} |'
            line_all.append(output + '\n')
            print(output)
        with open('information.txt', 'w', encoding='utf-8') as f:
            f.writelines(line_all)


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = stock_information_class()
    model.stock_information()
