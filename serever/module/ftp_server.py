#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
"""
FTP server端主程序
"""
import socketserver, json, subprocess, sys, os, shutil, prettytable
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
from conf.setting import *
import module.data_handle,module.dirs,module.check_intact,module.bar


class MyServer(socketserver.BaseRequestHandler):
    """
    继承socket,派生类
    """
    #设置类的静态字段
    user = None
    space_avaiable = None
    current_dic = None

    def handle(self):
        #handle方法
        conn = self.request
        #发送欢迎消息
        conn.sendall(bytes('FTP服务器已连接,请输入用户名密码登录.', encoding='utf8'))
        #接受客户端发送来的登录信息
        data = conn.recv(1024)
        #执行校验用户登录信息
        check_res = self.__Check(data)
        #登录成功处理
        if check_res:
            self.user,self.space_avaiable,self.current_dic = check_res
            check_res = '用户%s登录成功,可用空间为%sM,输入help查看帮助!'%(self.user,module.dirs.b_m(self.space_avaiable))
        #登录失败
        else:
            check_res = '登录失败,用户名密码验证失败!'
        #登录结果发送给客户端
        conn.sendall(bytes(check_res,encoding='utf8'))
        #如登录成功,进入主程序
        if self.__Check(data):
            #进入循环
            while True:
                #打印当前登录用户
                print('self.user:',self.user)
                #接收消息
                data = conn.recv(1024)
                #如果消息中有用法下载的信息
                if data.decode().startswith('start_get,'):
                    data=data.decode().split(',')[-1]
                    print(data)
                    #执行下载的方法
                    self.get_action(data,conn)
                #断点下载方法
                elif data.decode().startswith('continue_get,'):
                    continue_get_info=data.decode().split(',')[-1]
                    print(continue_get_info)
                    self.continue_get_action(continue_get_info,conn)
                else:
                    #非以上消息,设置任务字典
                    task_dic=json.loads(data.decode())
                    print(type(task_dic))
                    print(task_dic)
                    print('%s says %s'%(self.client_address,task_dic))
                    #如果数据为空,进入下一次循环
                    if len(data) == 0:continue
                    else:
                        #非空情况,设置任务类型
                        task_action = task_dic.get('action')
                        #退出处理,发送关闭确认消息,退出循环
                        if task_action == 'exit':
                            print('action:exit!!!!!!!')
                            conn.sendall(bytes('bye!',encoding='utf8'))
                            break
                        #利用反射,如果有相关任务方法,调用方法
                        elif hasattr(self,task_action):
                            func=getattr(self,task_action)
                            print('task_action:',task_action)
                            #调用方法,接受结果
                            msg=func(task_dic,conn)
                            print(msg)
                            #发送结果到客户端
                            conn.sendall(bytes(msg,encoding='utf8'))
                        #如果无相关方法,提示客户端无命令
                        else:
                            msg='无此命令!'
                            print(msg)
                            conn.sendall(bytes(msg,encoding='utf8'))
    #ls方法
    def ls(self,task_dic,conn):
        cmd=task_dic['action']
        #如果有参数,设置为操作目录
        if task_dic.get('file_name'):
            file_name=task_dic.get('file_name')
            ob='%s%s%s'%(self.current_dic,os.sep,file_name)
        #否则,操作目录为当前用户home
        else:
            ob=self.current_dic
        #拼接命令字符串
        cmd='%s %s'%(cmd,ob)
        #调用subprocess模块
        cmd_res=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        res=cmd_res.stdout.read().decode().replace(self.current_dic,'')
        #错误信息提取
        if not res:
            res=cmd_res.stderr.read().decode()
        #无结果,为空目录
        if len(res) == 0:
            res = '空目录'
        return res
    #cd方法
    def cd(self,task_dic,conn):
        #设置操作对象
        file_name=task_dic['file_name']
        #如果没有参数,切换到家目录
        if not file_name:
            msg='已切换至%s家目录!'%self.user
            return msg
        #否则判断home的绝对路径和参数对象的绝对路径
        home_dir=module.dirs.GetUsrLib(self.user)
        abs_home_dir=os.path.abspath(home_dir)
        want_dir='%s%s%s%s'%(self.current_dic,os.sep,file_name,os.sep)
        abs_want_dir=os.path.abspath(want_dir)
        print(abs_home_dir)
        print(abs_want_dir)
        #如果操作非home中的文件,提醒无权限
        if abs_home_dir not in abs_want_dir:
            msg = '此用户无权限访问home目录之外的文件或目录!!!'
            return msg
        else:
            #否则,如果对象为.的操作
            if file_name == '.':
                msg='当前目录没有切换'
                return msg
            #对象为..的操作,修改当前目录的值
            elif file_name == '..':
                dic_list=self.current_dic.split(os.sep)
                del dic_list[-1]
                self.current_dic=os.sep.join(dic_list)
                print(self.current_dic)
                msg='已切换至上层目录.'
                return msg
            else:
                #非以上的对象,修改静态字段当前目录
                abs_file='%s%s%s'%(self.current_dic,os.sep,file_name)
                if os.path.isdir(abs_file):
                    #如果对象为目录,修改当前目录
                    self.current_dic='%s%s%s'%(self.current_dic,os.sep,file_name)
                    msg='已切换至目录%s'%file_name
                else:
                    #如果对象为文件
                    msg='无效的目录名'
        return msg
    #rm的方法
    def rm(self,task_dic,conn):
        file_name=task_dic['file_name']
        #无参数处理
        if not file_name:
            msg='需要删除对象作为参数'
            return msg
        #有参数
        else:
            #文件绝对路径设置
            asb_file='%s%s%s'%(self.current_dic,os.sep,file_name)
            print(asb_file)
            #如果为不存在文件
            if not os.path.exists(asb_file):
                msg='无效的文件名.'
                return msg
            else:
                #取得系统中的绝对路径
                path_asb_file=os.path.abspath(asb_file)
                home_dir=module.dirs.GetUsrLib(self.user)
                abs_home_dir=os.path.abspath(home_dir)
                #如果对象为非home中的文件
                if abs_home_dir not in path_asb_file:
                    msg = '无操作权限!!'
                    return msg
                else:
                    #如果对象为目录,非空目录提示用户,空目录删除
                    if os.path.isdir(asb_file):
                        try:
                            os.removedirs(asb_file)
                        except:
                            msg='目录非空文件,无法删除!'
                            return msg
                        else:
                            msg='已删除目录%s'%file_name
                            return msg
                    else:
                        #如果对象为文件,删除文件
                        os.remove(asb_file)
                        msg='已删除文件%s'%file_name
                        return msg

    #创建目录方法
    def mkdir(self,task_dic,conn):
        file_name=task_dic['file_name']
        #无参数
        if not file_name:
            msg='需要目录名称作为参数!'
        else:
            #设置文件绝对路径
            abs_file='%s%s%s'%(self.current_dic,os.sep,file_name)
            #非法文件名
            if file_name == '.' or file_name == '..':
                msg='非法的目录名'
            #如果已存在目录
            elif os.path.exists(abs_file):
                msg = '已有文件或目录%s'%file_name
            #不存在文件,如果如果连续目录,连续创建,如果只一个目录,创建
            else:
                dir='%s%s%s'%(self.current_dic,os.sep,file_name)
                if os.sep in file_name:
                    os.makedirs(dir)
                    msg='已连续创建目录%s'%file_name
                else:
                    os.mkdir(dir)
                    msg = '已创建目录%s'%file_name
        return msg
    #帮助方法
    def help(self,task_dic,conn):
        msg="""
+++++++++++++++++++++++++++++
cd:             切换目录
ls:             查看目录或者文件
mkdir:          创建目录
mkdir xx/xx:    连续创建目录
rm:             删除文件
help:           查看帮助
put:            上传文件
get:            下载文件
++++++++++++++++++++++++++++++
        """
        return msg
    #get方法
    def get(self,task_dic,conn):
        #无参数
        if task_dic['file_name']==None:
            return 'Unknow files'
        #如有参数,取得绝对路径
        file_name=task_dic['file_name']
        user_lib=module.dirs.GetUsrLib(self.user)
        abs_file='%s%s%s'%(user_lib,os.sep,file_name)
        #如果不存在,提示
        if not os.path.exists(abs_file):
            return '无此文件:%s'%task_dic['file_name']
        #如果是目录,无法下载
        elif os.path.isdir(abs_file):
            return '目录文件无法下载'
        #否则,拼接字符串为消息,包括文件大小,md5
        else:
            file_size=os.stat(abs_file).st_size
            file_md5=module.check_intact.GetFileMd5(abs_file)
            get_info='get|%s|%s|%s'%(file_name,file_size,file_md5)
            return get_info

    #下载文件方法
    def get_action(self,msg,conn):
        get_info=msg.split('|')
        file_name=get_info[1]
        user_lib=module.dirs.GetUsrLib(self.user)
        abs_file='%s%s%s'%(user_lib,os.sep,file_name)
        #打开文件,发送
        with open(abs_file,'rb') as f:
            for line in f:
                conn.sendall(line)
        module.bar.bar(100)
        print('发送完毕')

    #断点下载方法,获取文件信息,并发送
    def continue_get_action(self,continue_get_info,conn):
        get_info=continue_get_info.split('|')
        file_name=get_info[0]
        now_file_size=int(get_info[1])
        user_lib=module.dirs.GetUsrLib(self.user)
        abs_file='%s%s%s'%(user_lib,os.sep,file_name)
        with open(abs_file,'rb') as f:
            f.seek(now_file_size)
            for line in f:
                conn.sendall(line)
        module.bar.bar(100)
        print('\n发送完毕')

    #上传方法,先获取文件相关信息
    def put(self,task_dic,conn):
        file_size=task_dic['file_size']
        file_name=task_dic['file_name']
        print('file_size:',file_size)
        print('file_name:',file_name)
        print('self.space_avaiable:',self.space_avaiable)
        #无put参数
        if not file_name:
            msg='Unknow files'
            return msg
        else:
            user_lib=self.current_dic
            abs_file='%s%s%s'%(user_lib,os.sep,file_name)
            # print()
            #如果文件存在
            if os.path.exists(abs_file):
                file_md5=module.check_intact.GetFileMd5(abs_file)
                #校验md5,如果匹配一致,提示用户
                if file_md5==task_dic['file_md5']:
                    msg='FTP服务器中已存在文件:%s,并且MD5值一致'%file_name
                    return msg
                #不一致,断点续传
                else:
                    now_file_size=os.stat(abs_file).st_size
                    print('now_file_size',now_file_size)
                    print(type(now_file_size))
                    msg_break='break:上次传输中断,需断点续传!'
                    conn.sendall(bytes(msg_break,encoding='utf8'))
                    #接受确认上传
                    msg_go=conn.recv(1024).decode()
                    #断点上传
                    if msg_go == 'Go':
                        conn.sendall(bytes(str(now_file_size),encoding='utf8'))
                        recv_size=0
                        diff = task_dic['file_size']-now_file_size
                        with open(abs_file,'rb+') as f:
                            f.seek(0,2)
                            while recv_size < diff:
                                data=conn.recv(1024)
                                f.write(data)
                                recv_size+=len(data)
                                num=recv_size/diff*100
                                module.bar.bar(num)
                        file_md5=module.check_intact.GetFileMd5(abs_file)
                        if file_md5 == task_dic['file_md5']:
                            msg='\n文件:%s传输并校验完成,MD5值为:%s'%(file_name,file_md5)
                            return msg
                        else:
                            #如果不一致,说明文件下载出错
                            msg='\n链路出现问题,文件不一致!'
                            return msg
            #文件不存在
            else:
                #判断可用空间
                if file_size > self.space_avaiable:
                    msg='Have not enough space!!!'
                    return msg
                else:
                    #发送上传确认消息
                    msg_start='start'
                    conn.sendall(bytes(msg_start,encoding='utf8'))
                    #避免粘包,接受文件并拼接
                    recv_size=0
                    with open(abs_file,'wb') as f:
                        while recv_size < file_size:
                            data=conn.recv(1024)
                            f.write(data)
                            recv_size+=len(data)
                            num=recv_size/file_size*100
                            module.bar.bar(num)
                    file_md5=module.check_intact.GetFileMd5(abs_file)
                    #MD5校验
                    if file_md5 == task_dic['file_md5']:
                        msg='\n文件:%s传输并校验完成,MD5值为:%s'%(file_name,file_md5)
                        return msg
                    else:
                        msg='\n链路出现问题,文件不一致!'
                        return msg

    #登录信息校验
    def __Check(self, data):
        user_data = module.data_handle.data_load()
        data=data.decode()
        data=data.strip().split('|')
        #异常处理
        try:
            #登录校验正确,设置相关信息
            if user_data[data[0]][0] == data[1]:
                user=data[0]
                user_lib=module.dirs.GetUsrLib(user)
                user_lib_size=module.dirs.GetDirSize(user_lib)
                space_avaiable=module.dirs.m_b(user_data[user][1])-user_lib_size
                return user,space_avaiable,user_lib
        except:return None

def main():
    """
    主函数,创建soketserver类,开启forver模式
    :return:
    """
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 9009), MyServer)
    server.serve_forever()
