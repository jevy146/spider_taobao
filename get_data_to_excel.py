# -*- coding: utf-8 -*-
# @Time    : 2020/4/3 16:02
# @Author  : 结尾！！
# @FileName: get_data_to_excel.py
# @Software: PyCharm

import pymongo
client = pymongo.MongoClient("192.168.124.21",port=27017)  #默认的端口为27017，笔记本电脑的Ip
db = client["taobao"]

import pandas as pd
#链接数据库
import  numpy as np

dbtable=db ['xiaolongxia']

res=dbtable.find()
search_df=[]
for one_link in res:
    try:
        print(one_link)
        search_df.append(one_link)
    except:
        pass
print('总计条数',len(search_df))
df1=pd.DataFrame(search_df)

df1.to_excel('./小龙虾.xlsx',header=True,index=None)
