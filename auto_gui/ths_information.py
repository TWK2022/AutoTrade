import os
import tqdm
import time
import ocr
import argparse
import pyautogui
import numpy as np
import pandas as pd

if os.getcwd() == os.path.realpath(os.path.dirname(__file__)):  # 当前目录下运行
    from block import block_class
else:
    from .block import block_class

# -------------------------------------------------------------------------------------------------------------------- #
# 功能:自动收集同花顺某个板块中的所有股票f10信息。记录到.txt
# 运行条件:进入要收集的行业/概念/板块，点击进入行业的第一支股票，再返回代码并运行
# 后续筛选:让大模型根据内容来筛选股票，开启深度思考和联网搜索
# 如:结合以下信息和你的知识库，筛选出与A行业最不相关、或核心业务占比最少的股票M-N支左右，结果只需要给出名称：
# -------------------------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description='|收集信息|')
parser.add_argument('--number', default=1000, type=int, help='|收集股票上限|')
parser.add_argument('--screen', default=['00', '60'], type=list, help='|保留的股票开头|')
parser.add_argument('--drop_st', default=True, type=bool, help='|是否去除ST股票|')
parser.add_argument('--keep_path', default='社区团购.csv', type=str, help='|存在时只保留其中的数据|')
parser.add_argument('--save_path', default='information.csv', type=str, help='|保存位置|')
args_default, _ = parser.parse_known_args()
save_dir = os.path.dirname(os.path.dirname(__file__)) + '/dataset/industry/'
args_default.keep_path = save_dir + args_default.keep_path
args_default.save_path = save_dir + args_default.save_path
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


class ths_information_class(block_class):
    def __init__(self, args=args_default):
        super().__init__()
        self.number = args.number
        self.screen = args.screen
        self.drop_st = args.drop_st
        self.save_path = args.save_path
        if os.path.exists(args.keep_path) and '.csv' in args.keep_path:
            df = pd.read_csv(args.keep_path)
            self.name_all = df['股票'].values
        else:
            self.name_all = None
        # 文字检测模型
        self.ocr = ocr.ocr.ocr_class()
        # 结果
        self.result = {}
        # 回到桌面
        pyautogui.hotkey('win', 'd')
        pyautogui.moveTo(1, 1, duration=0)
        time.sleep(0.5)
        # 进入同花顺
        self.find_and_click(self.image_dict['桌面']['同花顺_任务栏'], click=1)
        # 进入f10公司信息页面
        pyautogui.press('f10', presses=1, interval=0)
        # 下一个股
        x, y, w, h = self.image_location(self.image_dict['信息']['下一个股'], assert_=True)
        self.position['信息']['下一个股'] = (x, y)
        # 主营业务
        x, y, w, h = self.image_location(self.image_dict['信息']['主营业务'], assert_=True)
        self.position['信息']['主营业务'] = (x, y)
        self.screenshot['信息']['主营业务'] = (x + w // 2, y - h // 2, int((0.62 * self.w) // 2), h)
        # 公司亮点
        x, y, w, h = self.image_location(self.image_dict['信息']['公司亮点'], assert_=True)
        self.position['信息']['公司亮点'] = (x, y)
        self.screenshot['信息']['公司亮点'] = (x + w // 2, y - h // 2, int((0.62 * self.w) // 2), h)
        # 概念贴合度排名
        x, y, w, h = self.image_location(self.image_dict['信息']['概念贴合度排名'], assert_=True)
        self.position['信息']['概念贴合度排名'] = (x, y)
        self.screenshot['信息']['概念贴合度排名'] = (x + w // 2, y - h // 2, int((0.62 * self.w) // 2), h)
        # 所属申万行业
        x, y, w, h = self.image_location(self.image_dict['信息']['所属申万行业'], assert_=True)
        self.position['信息']['所属申万行业'] = (x, y)
        self.screenshot['信息']['所属申万行业'] = (x + w // 2, y - h // 2, int((0.1 * self.w) // 2), h)

    def ths_information(self):  # 获取股票的公司信息
        for _ in tqdm.tqdm(range(self.number)):
            # 下翻位置
            x, y = self.position['信息']['下一个股']
            pyautogui.moveTo(x, y, duration=0)
            # 等待页面刷新
            time.sleep(0.3)
            # 名称
            x, y, w, h = (int(0.448 * self.w), int(0.083 * self.h), int(0.114 * self.w), int(0.032 * self.h))
            image1 = pyautogui.screenshot(region=(x, y, w, h))
            name_str = self.ocr.ocr(image1)
            search1 = self.regex['名称和代码'].search(name_str)
            if search1 is None:  # 没有检测到
                pyautogui.click(button='left', clicks=1, interval=0)  # 下一页
                continue
            name = search1.group(1)
            code = search1.group(2)
            if self.name_all is not None and name not in self.name_all:  # 只更新数据
                pyautogui.click(button='left', clicks=1, interval=0)  # 下一页
                continue
            if name and self.result.get(name) is not None:  # 循环了一轮
                print('| 提前结束 | 循环了一轮 |')
                break
            if self.drop_st and 'ST' in name:  # 去除ST股票
                pyautogui.click(button='left', clicks=1, interval=0)  # 下一页
                continue
            if code[:2] not in self.screen:  # 非目标股票
                pyautogui.click(button='left', clicks=1, interval=0)  # 下一页
                continue
            # 截图
            image = np.array(pyautogui.screenshot())
            self.result[name] = {}
            # 主营业务
            x, y, w, h = self.screenshot['信息']['主营业务']
            self.result[name]['主营业务'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 公司亮点
            x, y, w, h = self.screenshot['信息']['公司亮点']
            self.result[name]['公司亮点'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 概念贴合度排名
            x, y, w, h = self.screenshot['信息']['概念贴合度排名']
            self.result[name]['概念贴合度排名'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 所属申万行业
            x, y, w, h = self.screenshot['信息']['所属申万行业']
            self.result[name]['所属申万行业'] = self.ocr.ocr(image[y:y + h, x:x + w])
            # 下一页
            pyautogui.click(button='left', clicks=1, interval=0)
        # 记录
        line_all = []
        for name in self.result.keys():
            line_all.append([name, '主营业务：' + self.result[name]['主营业务'],
                             '公司亮点：' + self.result[name]['公司亮点'],
                             '概念贴合度排名：' + self.result[name]['概念贴合度排名'],
                             '所属申万行业：' + self.result[name]['所属申万行业']])
        column = ['股票', '主营业务', '公司亮点', '概念贴合度排名', '所属申万行业']
        df = pd.DataFrame(line_all, columns=column)
        df.to_csv(self.save_path, index=False)
        if self.name_all is not None:  # 未更新的股票
            name_all = set(self.name_all)
            result_name = set(list(self.result.keys()))
            distance = list(name_all - result_name)
            print(f'未更新的股票:{distance}')


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = ths_information_class()
    model.ths_information()
