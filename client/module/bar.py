#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
import sys
def bar(x):
    """
    进度条程序
    :param x: 下载上传进度比例*100
    :return:
    """
    #进度值
    rate=int(x)
    #进度相关进度条
    star='>'*rate
    r="\r进度:%s%s%%"%(star,rate)
    sys.stdout.write(r)
    sys.stdout.flush()