import cv2
import argparse
import onnxruntime
import numpy as np

# -------------------------------------------------------------------------------------------------------------------- #
# ocr图片文字检测：https://www.modelscope.cn/models/iic/cv_convnextTiny_ocr-recognition-general_damo
# 需要文件：model.onnx、vocab.txt
# 修改:：vocab.txt最前面加两个空行
# -------------------------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description='|ocr图片文字检测|')
parser.add_argument('--model_path', default='ocr_model/model.onnx', type=str, help='|ocr模型位置|')
parser.add_argument('--vocab_path', default='ocr_model/vocab.txt', type=str, help='|vocab词表位置|')
args, _ = parser.parse_known_args()


# -------------------------------------------------------------------------------------------------------------------- #
class ocr_class:
    def __init__(self, args=args):
        self.session = onnxruntime.InferenceSession(args.model_path, providers=['CPUExecutionProvider'])  # 模型
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        with open(args.vocab_path, 'r', encoding='utf-8') as f:  # 词表
            self.vocab_path = np.array([_[:-1] for _ in f.readlines()])

    def ocr(self, image):
        input_data = self.image_deal(image)
        output = self.session.run([self.output_name], {self.input_name: input_data})[0][0]
        predict = np.argmax(output, axis=1)
        predict = self.vocab_path[predict]
        predict = predict[np.where(predict[1:] != predict[:-1])]  # 相邻的不能重复
        predict = ''.join(predict.tolist())
        return predict

    @staticmethod
    def image_deal(image):
        cur_ratio = image.shape[1] / float(image.shape[0])
        mask_height = 32
        mask_width = 804
        if cur_ratio > float(mask_width) / mask_height:
            cur_target_height = mask_height
            cur_target_width = mask_width
        else:
            cur_target_height = mask_height
            cur_target_width = int(mask_height * cur_ratio)
        image = cv2.resize(image, (cur_target_width, cur_target_height))
        mask = np.zeros([mask_height, mask_width, 3]).astype(np.uint8)
        mask[:image.shape[0], :image.shape[1], :] = image
        image = mask
        image = np.array(image, dtype=np.float32)
        image_list = []
        for i in range(3):
            left = (300 - 48) * i
            image_list.append(image[:, left:left + 300, :])
        input_data = np.concatenate(image_list)
        input_data = np.resize(input_data / 255, (3, 32, 300, 3))
        input_data = input_data.transpose(0, 3, 1, 2)
        return input_data


# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    model = ocr_class(args)
    image = cv2.imread('image/demo.png')
    result = model.ocr(image)
    print(result)
