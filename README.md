# ...
### 环境
>```
>pip install finta tushare pyperclip pyautogui opencv-python onnxruntime -i https://pypi.tuna.tsinghua.edu.cn/simple
>```
### auto_gui/ths_information.py
>收集同花顺中某个行业的股票基本信息：dataset/industry/information.csv  
>手动或借助大模型对股票的基本信息进行筛选，去除与行业不相关、非核心业务、业绩很差的公司。改名为为：行业.csv  
>频率：初始收集和筛选一次，之后可以手动增删股票
### stock_process/industry_choice.py
>根据"dataset/industry"选择行业和股票：dataset/industry_choice.yaml  
### stock_process/tushare_block.py
>根据"dataset/industry_choice.yaml"收集股票数据：dataset/stock  
>需要密钥
### stock_process/data_add.py
>根据"dataset/industry_choice.yaml"和"dataset/stock"补全股票数据：dataset/stock_add
### stock_process/data_screen.py
>根据"dataset/industry_choice.yaml"和"dataset/stock_add"用规则筛选股票：dataset/industry_screen.yaml
### model_predict/model_predict.py
>根据"dataset/industry_screen.yaml"和"dataset/stock_add"训练模型筛选股票：dataset/model_predict.yaml
### auto_gui/ths_add.py
>根据"dataset/industry_choice.yaml"批量添加股票到同花顺板块中  
>频率：初始添加一次，之后可以手动增删股票
### auto_gui/auto_gui.py
>根据"dataset/industry_choice.yaml"批量添加股票到同花顺板块中
### 其他
>github链接：https://github.com/TWK2022/notebook  
>邮箱：1024565378@qq.com