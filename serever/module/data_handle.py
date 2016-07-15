#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz

"""
数据处理相关模块
"""
import sys,os,json
BASEDIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
from conf.setting import *


#刷新用户数据程序
def data_flush(data):
    json.dump(data,open(user_data_file,'w'),ensure_ascii=True,indent=1)


#加载文件数据程序
def data_load():
    res = json.load(open(user_data_file,'r'))
    return res


