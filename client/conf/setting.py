#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
"""
程序文件相关配置
"""
import sys,os
BASEDIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
# print(BASEDIR)
#用户数据库文件配置
user_data_file = '%s%sdata%suser.json'%(BASEDIR,os.sep,os.sep)
#用户家目录配置
# user_document = '%s%sdocument'%(BASEDIR,os.sep)
#下载目录配置
download_document = '%s%sdownload'%(BASEDIR,os.sep)