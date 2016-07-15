#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz
"""
客户端主程序
"""
import sys,os,socket,json
BASEDIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
from conf.setting import *
import module.pwd_handle,module.check_intact,module.bar

def SendUsrInfo():
    """
    登录信息发送程序,拼接字符串并发送
    :return:
    """
    user=input('请输入用户名:')
    pwd=input('请输入%s的密码:'%user)
    pwd=module.pwd_handle.md5_pwd(pwd.strip())
    user_info='%s|%s'%(user.strip(),pwd)
    return user_info

def put_action(abs_filepath):
    """
    put 命令模块,发送本地文件到服务器
    :param abs_filepath: 文件名称,带路径
    :return:
    """
    print('start send %s'%abs_filepath)
    #打开文件并发送
    f = open(abs_filepath,'rb')
    for line in f:
        sk.send(line)
    #显示进度条
    module.bar.bar(100)
    print('\nsend complete')
    #接受回复信息,并将信息回显
    msg=sk.recv(1024).decode()
    f.close()
    return msg


def get_action(info):
    """
    下载文件
    :param info:
    :return:
    """
    #文件路径字符串拼接
    get_info=info.split('|')
    file_name=get_info[1]
    file_size=int(get_info[2])
    file_md5=get_info[3]
    abs_file='%s%s%s'%(download_document,os.sep,file_name)
    #接受文件,防止粘包,使用循环,并打印进度条
    recv_size=0
    with open(abs_file,'wb') as f:
        while recv_size < file_size:
            data=sk.recv(1024)
            f.write(data)
            recv_size+=len(data)
            num=recv_size/file_size*100
            module.bar.bar(num)
    #文件上传和下载MD5文件校验
    now_file_md5=module.check_intact.GetFileMd5(abs_file)
    if now_file_md5 == file_md5:
        print('\n%s下载完成,并且文件校验一致,MD5值为:%s'%(file_name,now_file_md5))
    else:print('\n校验文件不一致,请重新下载!')

def put_break(abs_filepath):
    """
    put断点发送
    :param abs_filepath: 文件名,带路径
    :return: 接受到的服务发来的消息
    """
    #发送Go消息,让服务端知道是断点发送开始
    sk.sendall(bytes('Go',encoding='utf8'))
    #确认文件的大小,并发送
    server_file_size=int(sk.recv(1024).decode())
    # print(server_file_size)
    # print(type(server_file_size))
    with open(abs_filepath,'rb') as f:
        #指针定位到断点位置并发送剩余的内容
        f.seek(server_file_size)
        data=f.read()
        sk.sendall(data)
    #进度条
    module.bar.bar(100)
    print('\nsend complet!')
    #接受校验结果消息
    msg=sk.recv(1024).decode()
    f.close()
    return msg


def dic_send_data(cmd_dic,cmd_list):
    """
    发送给服务端的消息处理
    :param cmd_dic:类似报头的字典数据
    :param cmd_list:输入的命令拆分后的列表
    :return:
    """
    cmd_dic['action']=cmd_list[0]
    #命令只有无参数字典处理
    if len(cmd_list)==1:
        return cmd_dic
    #cd命令字典处理
    elif cmd_dic['action']=='cd':
        cmd_dic['file_name']=cmd_list[1]
        return cmd_dic
    #mkdir处理
    elif cmd_dic['action']=='mkdir':
        cmd_dic['file_name']=cmd_list[1]
        return cmd_dic
    #rm处理
    elif cmd_dic['action'] == 'rm':
        cmd_dic['file_name']=cmd_list[1]
        return cmd_dic
    #put处理
    elif cmd_dic['action'] == 'put':
        if not os.path.exists(cmd_list[1]) or os.path.isdir(cmd_list[1]):
            print('1111111111111111')
            cmd_dic['file_name']=None
            return cmd_dic
        # elif os.path
        else:
            cmd_dic['file_name']=cmd_list[1].split(os.sep)[-1]
            abs_filepath=cmd_list[1]
            file_size=os.stat(abs_filepath).st_size
            cmd_dic['file_size']=file_size
            cmd_dic['file_md5']=module.check_intact.GetFileMd5(abs_filepath)
            return cmd_dic

    else:
        #将输入的命令拆分,赋予相关的变量或者值
        abs_filepath=cmd_list[1]
        #如果对象是不带路径的文件
        if os.sep not in abs_filepath:
            cmd_dic['file_name']=cmd_list[1]
            return cmd_dic
        #如果文件存在的处理动作
        elif os.path.isfile(abs_filepath):
            file_size=os.stat(abs_filepath).st_size
            file_name=abs_filepath.split(os.sep)[-1]
            print('file:%s file_size:%s'%(abs_filepath,file_size))
            cmd_dic['file_name']=file_name
            cmd_dic['file_size']=file_size
            cmd_dic['file_md5']=module.check_intact.GetFileMd5(abs_filepath)
            return cmd_dic
        else:return cmd_dic

#设置IP,端口,并创建soket对象,连接相关IP和端口
ip_port=('127.0.0.1',9009)
sk=socket.socket()
sk.connect(ip_port)
def main():
    #接收欢迎消息
    wel_msg=sk.recv(1024)
    print(wel_msg.decode())

    #发送用户名密码校验,并接受登录结果
    user_info=SendUsrInfo()
    sk.send(bytes(user_info,encoding='utf8'))
    check_res=sk.recv(4096)
    print(check_res.decode())
    #如果登录成功,进入命令行
    if '成功' in check_res.decode():
        while True:
            #输入命令
            cmd = input('>>:').strip()
            #拆分输入的字符串
            cmd_list=cmd.split()
            #初化报头字典
            cmd_dic={"action":None,"file_name":None,"file_size":None,"file_md5":None}
            #如果回车,进入下一次循环
            if len(cmd_list) == 0:continue
            #否则处理报头字典
            else:cmd_dic=dic_send_data(cmd_dic,cmd_list)

            print(cmd_dic)


            # print(cmd_dic)
            #发送报头字典
            sk.sendall(bytes(json.dumps(cmd_dic),encoding='utf8'))
            #接收服务端回执消息并打印
            msg=sk.recv(1024).decode()
            print(msg)

            #退出程序
            if msg == 'bye!':
                break
            #开始put文件
            elif msg == 'start':
                res = put_action(cmd_list[1])
                print(res)
            #开始断点put文件
            elif msg.startswith('break'):
                res = put_break(cmd_list[1])
                print(res)
            #下载相关处理
            elif msg.startswith('get'):
                get_info=msg.split('|')
                file_name=get_info[1]
                file_size=int(get_info[2])
                file_md5=get_info[3]
                abs_file='%s%s%s'%(download_document,os.sep,file_name)
                now_file_md5=module.check_intact.GetFileMd5(abs_file)
                #如果文件已存在,MD5校验文件一致性
                if os.path.exists(abs_file):
                    if file_md5==now_file_md5:
                        print('文件%s已存在,MD5值为:%s'%(file_name,file_md5))

                    else:
                        #断点续传
                        print('有文件,需断点续传!')
                        now_file_size=os.stat(abs_file).st_size
                        print(now_file_size)
                        continue_get_info='continue_get,%s|%s'%(file_name,now_file_size)
                        sk.sendall(bytes(continue_get_info,encoding='utf8'))
                        diff_size=file_size-now_file_size
                        recv_size=0
                        with open(abs_file,'rb+') as f:
                            f.seek(0,2)
                            while recv_size < diff_size:
                                data=sk.recv(1024)
                                f.write(data)
                                recv_size+=len(data)
                                now_size=os.stat(abs_file).st_size
                                num=now_size/file_size*100
                                module.bar.bar(num)
                            module.bar.bar(100)
                        #校验下载后的文件和源文件的一致性
                        geted_file_md5=module.check_intact.GetFileMd5(abs_file)
                        if geted_file_md5 == file_md5:
                            print('\n%s下载完成,文件校验一致,MD5值为:%s'%(file_name,geted_file_md5))
                        else:
                            print('\n%s下载完成,但文件不一致,请重新下载!'%file_name)
                else:
                    #无本地文件时,直接下载新文件
                    info='start_get,%s'%msg
                    sk.sendall(bytes(info,encoding='utf8'))
                    get_action(msg)
    #登录失败,关闭连接
    else:
        sk.close()

