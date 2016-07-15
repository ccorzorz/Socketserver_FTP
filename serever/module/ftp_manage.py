#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
"""
后台管理模块
"""
import sys,os,shutil,prettytable
BASEDIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
from conf.setting import *
import module.pwd_handle,module.data_handle


def DiskValue(user):
    """
    磁盘配额
    :param user: 用户名
    :return: 配额值
    """
    while True:
        disck_value=input('请输入用户%s磁盘的配额(单位M):'%user)
        #异常处理
        try:
            disck_value=int(disck_value)
        except:
            print('输入有误!请重新输入')
        else:
            return disck_value


def CreateUser():
    """
    添加用户模块
    :return:
    """
    #加载数据
    data=module.data_handle.data_load()
    while True:
        user=input('请输入用户名:')
        #判断用户是否存在
        if data.get(user):
            print('用户名已存在!')
        else:
            pwd=input('请输入%s的密码:'%user)
            #处理密码
            pwd=module.pwd_handle.md5_pwd(pwd)
            #创建相关home目录
            os.mkdir('%s/%s'%(user_document,user))
            disk_value=DiskValue(user)
            data[user] = [pwd,disk_value]
            #刷新数据文件
            module.data_handle.data_flush(data)
            print('''{0}用户已创建
目录为:{1}/{0}
最大可用空间为{2}M'''.format(user,user_document,disk_value))
            break

def DelUser():
    """
    删除用户
    :return:
    """
    data=module.data_handle.data_load()
    while True:
        user=input('请输入用户名:')
        if data.get(user) == None:
            print('此用户不存在!')
        else:
            del data[user]
            shutil.rmtree('%s/%s'%(user_document,user))
            module.data_handle.data_flush(data)
            print('用户%s已删除!'%user)
            break

def ShowAll():
    """
    显示所有用户信息,读取数据后,将相关信息打印
    :return:
    """
    data=module.data_handle.data_load()
    if len(data) == 0:
        print('暂时没有用户!')
    else:
        row=prettytable.PrettyTable()
        row.field_names=['用户名','磁盘配额(单位M)','家目录']
        for user in data:
            document='%s/%s'%(user_document,user)
            row.add_row([user,data[user][1],document])
        print(row)

def Logout():
    exit('管理程序退出!')

#将函数添加值列表
menu=[ShowAll,CreateUser,DelUser,Logout]

def manager():
    """
    主程序
    :return:
    """
    #校验用户名和密码,如正确进入程序,否则登录失败
    admin_user = input('请输入管理员用户名:')
    admin_pwd = input('请输入管理员密码:')
    if admin_user == 'admin' and admin_pwd == 'admin':
        print('登录成功!')
        while True:
            #打印主菜单
            row=prettytable.PrettyTable()
            row.field_names=['查看所有用户','添加用户','删除用户','退出程序']
            row.add_row([0,1,2,'3&q'])
            print(row)
            inp = input('请选择功能相应的序列号:')
            if inp == 'q' or inp == 'quit':Logout()
            #错误处理,如果选择错误,提示输入错误,正确则执行相关程序
            try:
                inp=int(inp)
                menu[inp]()
            except:print('输入有误')
    else:
        print('登录失败!')

if __name__ == '__main__':
    manager()