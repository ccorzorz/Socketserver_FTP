#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
"""
文件校验程序
"""
import hashlib,os

def GetFileMd5(filename):
    """
    获取文件MD5值
    :param filename: 文件名称,绝对路径
    :return: MD5值
    """
    if not os.path.isfile(filename):
        return 'Not file'
    else:
        #hashlib加密
        hash=hashlib.md5(bytes('oldboy',encoding='utf8'))
        f = open(filename,'rb')
        #循环读取文件,并update md5值
        while True:
            b =  f.read(4096)
            if not b:
                break
            hash.update(b)
        res = hash.hexdigest()
        return res

if __name__ == '__main__':

    res=GetFileMd5('/Users/shane/PycharmProjects/Py_study/Base/S2/test.xml')
    print(res)

    res2=GetFileMd5('/Users/shane/Documents/web.xml')
    print(res2)





