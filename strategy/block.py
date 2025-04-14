import os
import numpy as np
import pandas as pd


class block_class:
    '''
        bottom_increase_volume: 5日线下方先缩量后底部放量
                scale: 放量倍数
                date_max: 最大缩量天数
    '''

    def __init__(self):
        self.path_dir = os.path.dirname(os.path.dirname(__file__)) + '/dataset/stock_add'

    def bottom_volume_count(self, scale=1.5):
        name_list = os.listdir(self.path_dir)
        path_list = [self.path_dir + '/' + _ for _ in name_list]
        result_df = pd.DataFrame([[0, 0, 0] for _ in range(5)], columns=['总次数', '上涨', '上穿5日线'],
                                 index=['缩量0日', '缩量1日', '缩量2日', '缩量3日', '缩量4日'])
        for path in path_list:
            df = pd.read_csv(path)
            df['均价'] = 0.5 * df['收盘价'] + 0.1 * df['开盘价'] + 0.2 * df['最高价'] + 0.2 * df['最低价']
            result_df += self.bottom_volume(df, scale=scale)
        result_df['上涨'] = np.round(result_df['上涨'] / len(path_list), 2)
        result_df['上穿5日线'] = np.round(result_df['上穿5日线'] / len(path_list), 2)
        print(result_df)

    @staticmethod
    def bottom_volume(df, scale=1.5):
        value = df['均价'].values
        close = df['收盘价'].values
        close_5 = df['收盘价_EMA_5'].values
        volume = df['成交量'].values
        total_dict = {_: 0 for _ in range(5)}
        correct_dict = {_: 0 for _ in range(5)}
        cross_dict = {_: 0 for _ in range(5)}
        for index in range(5, len(df) - 2):
            # 昨日在5日线下方，今日成交量放大，持续放量(129)
            if close[index - 1] < close_5[index - 1] and scale * volume[index - 1] < volume[index]:
                if volume[index - 1] > volume[index - 2]:
                    total_dict[0] += 1
                    if value[index] > close[index - 1] or value[index + 1] > value[index]:  # 今/明日上涨
                        correct_dict[0] += 1
                    if value[index + 1] > close_5[index + 1]:  # 上穿5日线
                        cross_dict[0] += 1
                # 缩量1日(1219)
                date = 1
                if (close[index - date - 1] < close_5[index - date - 1]
                        and volume[index - date] < volume[index - date - 1]):
                    if volume[index - date - 1] > volume[index - date - 2]:
                        total_dict[date] += 1
                        if value[index] > close[index - 1] or value[index + 1] > value[index]:
                            correct_dict[date] += 1
                        if value[index + 1] > close_5[index + 1]:
                            cross_dict[date] += 1
                    # 缩量2日(23219)
                    date = 2
                    if (close[index - date - 1] < close_5[index - date - 1]
                            and volume[index - date] < volume[index - date - 1]):
                        if volume[index - date - 1] > volume[index - date - 2]:
                            total_dict[date] += 1
                            if value[index] > close[index - 1] or value[index + 1] > value[index]:
                                correct_dict[date] += 1
                            if value[index + 1] > close_5[index + 1]:
                                cross_dict[date] += 1
                        # 缩量3日(343219)
                        date = 3
                        if (close[index - date - 1] < close_5[index - date - 1]
                                and volume[index - date] < volume[index - date - 1]):
                            if volume[index - date - 1] > volume[index - date - 2]:
                                total_dict[date] += 1
                                if value[index] > close[index - 1] or value[index + 1] > value[index]:
                                    correct_dict[date] += 1
                                if value[index + 1] > close_5[index + 1]:
                                    cross_dict[date] += 1
                            # 缩量4日(4543219)
                            date = 4
                            if (close[index - date - 1] < close_5[index - date - 1]
                                    and volume[index - date] < volume[index - date - 1]):
                                if volume[index - date - 1] > volume[index - date - 2]:
                                    total_dict[date] += 1
                                    if value[index] > close[index - 1] or value[index + 1] > value[index]:
                                        correct_dict[date] += 1
                                    if value[index + 1] > close_5[index + 1]:
                                        cross_dict[date] += 1
        value = []
        index = []
        for date in correct_dict.keys():
            value.append([total_dict[date], correct_dict[date] / (total_dict[date] + 1e-6),
                          cross_dict[date] / (total_dict[date] + 1e-6)])
            index.append(f'缩量{date}日')
        column = ['总次数', '上涨', '上穿5日线']
        df = pd.DataFrame(value, columns=column, index=index)
        return df

    @staticmethod
    def bottom_rebound(path_dir, scale=1.5):
        name_list = os.listdir(path_dir)
        path_list = [f'{path_dir}/{_}' for _ in name_list]
        total = 0
        correct = 0
        for path in path_list:
            df = pd.read_csv(path)
            close = df['收盘价'].values
            close_5 = df['收盘价_EMA_5'].values
            close_10 = df['收盘价_EMA_10'].values
            volume = df['成交量'].values
            for index in range(1, len(df) - 2):
                # 前1日在5日线与10日线之间，今日放量
                if (close_5[index - 1] < close[index - 1] < close_10[index - 1]
                        and volume[index] > scale * volume[index - 1]):
                    total += 1
                    if close[index + 1] > close_10[index + 1]:  # 明日站上10日线
                        correct += 1
        result = round(correct / total, 2)
        print(f'| {result} | 样本{total} |')


if __name__ == '__main__':
    model = block_class()
    model.bottom_volume_count()
