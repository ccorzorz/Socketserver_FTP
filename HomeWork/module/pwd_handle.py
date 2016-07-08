#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
"""
密码处理模块
"""
import hashlib


def md5_pwd(pwd):
    """
    密码转为MD
    :param pwd:明文密码
    :return: MD5字
    """
    hash=hashlib.md5(bytes('odlboy',encoding='utf8'))
    hash.update(bytes(pwd,encoding='utf8'))
    res=hash.hexdigest()
    return res


if __name__ == '__main__':
    inp = input('num:')
    res=md5_pwd(inp)
    print(res)