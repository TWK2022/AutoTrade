import os
import yaml
import argparse
import pandas as pd

# -------------------------------------------------------------------------------------------------------------------- #
# 筛选出某个行业的股票
# -------------------------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description='|选择股票|')
parser.add_argument('--industry', default='军工,医药,电力,社区团购,粮食概念,黄金概念', type=str, help='|选择的行业，如"A,B,C"|')
parser.add_argument('--stock_path', default='dataset/stock_all.yaml', type=str, help='|股票列表|')
parser.add_argument('--read_dir', default='dataset/industry', type=str, help='|行业csv文件|')
parser.add_argument('--save_path', default='dataset/stock_screen.yaml', type=str, help='|保存位置|')
args_default = parser.parse_args()
args_default.industry = args_default.industry.split(',')
args_default.stock_path = os.path.dirname(os.path.dirname(__file__)) + '/' + args_default.stock_path
args_default.read_dir = os.path.dirname(os.path.dirname(__file__)) + '/' + args_default.read_dir
args_default.save_path = os.path.dirname(os.path.dirname(__file__)) + '/' + args_default.save_path


# -------------------------------------------------------------------------------------------------------------------- #
class stock_process_class:
    def __init__(self, args=args_default):
        self.industry = args.industry
        self.read_dir = args.read_dir
        self.save_path = args.save_path
        with open(args_default.stock_path, 'r', encoding='utf-8') as f:
            self.stock_dict = yaml.load(f, Loader=yaml.SafeLoader)

    def stock_process(self):
        self.industry_choice()

    def industry_choice(self):
        result_dict = {}
        record = 0
        for industry in self.industry:
            result_dict[industry] = {}
            path = f'{self.read_dir}/{industry}.csv'
            name_all = pd.read_csv(path)['股票'].values
            for name in name_all:
                result_dict[industry][name] = self.stock_dict[name]
                record += 1
        # 保存
        with open(self.save_path, 'w', encoding='utf-8') as f:
            yaml.dump(result_dict, f, allow_unicode=True, sort_keys=False)
        print(f'| 总数:{record} | 保存结果至:{self.save_path} |')


# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    model = stock_process_class()
    model.stock_process()
