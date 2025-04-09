import os
import PIL
from PIL import Image


# -------------------------------------------------------------------------------------------------------------------- #
# 改变图片的分辨率
# 将图片放大后相比重新截图会变得模糊，但不影响识别
# -------------------------------------------------------------------------------------------------------------------- #
def change_image(dir_path, odl_size, new_size):
    print(f'| {dir_path}中所有图片大小将从{odl_size}改为{new_size} |')
    input('| 会覆盖原图片 | 取消：ctrl+d | 确定：回车|')
    scale_w = new_size[0] / odl_size[0]
    scale_h = new_size[1] / odl_size[1]
    dir_name_list = os.listdir(dir_path)
    for dir_name in dir_name_list:
        dir_name_path = f'{dir_path}/{dir_name}'
        name_list = os.listdir(dir_name_path)
        for name in name_list:
            name_path = f'{dir_name_path}/{name}'
            image = PIL.Image.open(name_path)
            w, h = image.size
            image = image.resize((int(w * scale_w), int(h * scale_h)))
            image.save(name_path)


# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    dir_path = '../match_image'
    odl_size = (1920, 1080)
    new_size = (1920, 1080)
    change_image(dir_path, odl_size, new_size)
