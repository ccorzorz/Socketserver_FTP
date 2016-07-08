#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
"""
成员后台管理入口
"""
import sys,os
BASEDIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
import module.ftp_manage

if __name__ == '__main__':
    module.ftp_manage.manager()