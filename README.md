# ...
### 环境
>```
>
>```
### auto_gui/ths_information.py
>收集同花顺中某个行业的股票基本信息  
>将结果放入dataset/industry中，名称改为 行业.csv  
>手动或借助大模型对股票的基本信息进行筛选，去除与行业不相关、非核心业务、业绩很差的公司  
>频率：初始收集和筛选一次，之后可以手动增删股票
### stock_process/stock_process.py
>从上一步的结果中选择行业和股票
### stock_process/tushare_block.py
>根据上一步的结果收集股票数据  
>需要密钥
### stock_process/stock_add.py
>在初始股票数据中增加数据
### 筛选
>筛选
### auto_gui/ths_add.py
>将股票批量添加到同花顺的板块中  
>频率：初始添加一次，之后可以手动增删股票
### auto_gui/auto_gui.py
>实时监测股票  
### 其他
>github链接：https://github.com/TWK2022/notebook  
>邮箱：1024565378@qq.com