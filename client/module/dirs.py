#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
"""
文件以及目录相关处理模块
"""
import sys,os
BASEDIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
from conf.setting import *

def GetDirSize(dir_name):
    """
    获取目录大小程序
    :param dir_name: 目录名称
    :return: 目录目前的大小
    """
    size=0
    for root,dirs,files in os.walk(dir_name):
        for name in files:
            size+=os.path.getsize(os.path.join(root,name))
    return size

def GetUsrLib(user):
    """
    获取文件的家目录
    :param user: 用户名称
    :return: 家目录
    """
    user_lib = '%s/%s'%(user_document,user)
    return user_lib

def m_b(args):
    """
    数据换算,M转字节
    :param args:数据,M
    :return:字节
    """
    return args*1048576

def b_m(args):
    """
    数据换算字节转M
    :param args:数据,字节
    :return: M
    """
    return args/1048576

# def GetAvi

if __name__ == '__main__':
    res = b_m(128974848)
    print(res)



