import os
import pyautogui
import numpy as np

if os.getcwd() == os.path.realpath(os.path.dirname(__file__)):
    from auto_gui import auto_gui_class
else:
    from .auto_gui import auto_gui_class


# -------------------------------------------------------------------------------------------------------------------- #
#
# -------------------------------------------------------------------------------------------------------------------- #
class get_information_class(auto_gui_class):
    def __init__(self):
        super().__init__()
        pyautogui.press('f10', presses=1, interval=0)  # 进入f10公司信息页面
        # 公司亮点
        x, y, w, h = self.image_location(self.yaml_dict['信息']['公司亮点'], assert_=True)
        self.axis['信息']['公司亮点'] = (x, y)
        self.screenshot['信息']['公司亮点'] = (x + w // 2, y - h // 2, int((0.5 * self.w) // 2), h)
        # 主营业务
        x, y, w, h = self.image_location(self.yaml_dict['信息']['主营业务'], assert_=True)
        self.axis['信息']['主营业务'] = (x, y)
        self.screenshot['信息']['主营业务'] = (x + w // 2, y - h // 2, int((0.5 * self.w) // 2), h)

    def get_information(self):  # 获取股票的公司信息
        # 获取数据
        x, y, w, h = self.screenshot['信息']['公司亮点']
        image1 = np.array(pyautogui.screenshot(region=(x, y, w, h)))
        name_str = self.ocr.ocr(image1)
        search1 = self.regex['名称'].search(name_str)
        x, y, w, h = self.screenshot['信息']['主营业务']
        image2 = np.array(pyautogui.screenshot(region=(x, y, w, h)))
        data_str = self.ocr.ocr(image2)
        search2 = self.regex['macdfs'].search(data_str)
        if search1 is None or search2 is None:
            print('! 未检测到数据 !')
        else:
            a = search1.group()
            b = search2.group()
        self.draw_image(image1)
        self.draw_image(image2)
        return None


if __name__ == '__main__':
    # auto_gui_class.screenshot_measure()  # 截图测量
    model = get_information_class()
    model.get_information()
    pass
