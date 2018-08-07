# -*- coding: UTF-8 -*-

from flask import Flask
from flask_cors import CORS
from flask import request
import paramiko
import os
import time
import logging
import datetime
import json

remove = Flask(__name__)
CORS(remove)

now = datetime.datetime.now().strftime("%Y%m%d%H%M") 
password = "XXXX"
loginuser = "root"
loginport = 22

logging.basicConfig(level = logging.INFO,
        format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(thread)d %(message)s',
        datefmt = '%a, %d %b %Y %H:%M:%S',
        filename = '/var/log/rmdir.log',
        filemode = 'a'
        )     
     
def LoginAndPerformOperation(host,loginuser,password,loginport,user,dir,area):
    """
    1、登录客户端
    2、通过area字段判断要清理的目录是本地还是集群（本地目录切换skyleo，集群目录切换前端传入用户进行操作）
    3、切换用户进行清理操作（创建备份目录，然后执行mv动作）
    """
    s=paramiko.SSHClient() 
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        s.connect(hostname=host,port=int(loginport),username=loginuser,password=password)
        logging.info("host %s login success." % host)
    except Exception,e:
        logging.error("host %s login failed,Error msg:%s" % (host,e))
        msg = {}
        msg['status'] = '1'
        msg['errmsg'] = 'login host failed'
        s.close()
        return msg
    splitdir = dir.split("/") #按分隔符"/"把目录分割成列表
    while '' in splitdir:     #
        splitdir.remove('')   #去除列表中空元素
    project = splitdir[-1]    #获取项目名称
    if area == '1':
        bk_dir = "/CustomerCofingBack/%s/%s/" % (user,project+"_"+now)  #拼接备份目录
        create_bk_dir = 'sudo -u %s hadoop fs -mkdir -p %s' % (user,bk_dir) #创建备份目录命令
        mv_files = 'sudo -u %s hadoop fs -mv %s* %s' % (user,dir,bk_dir) #创建mv命令
    elif area == '2':
        bk_dir = "/data11/%s/back/%s/" % (user,project+"_"+now)  #拼接备份目录
        create_bk_dir = 'sudo -u skyleo mkdir -p %s' % bk_dir    #创建备份目录命令
        mv_files = 'sudo -u skyleo mv -f %s* %s' % (dir,bk_dir)   #创建mv命令
    else:
        logging.error("area parameter is wrong")
        msg = {} 
        msg['status'] = '1' 
        msg['errmsg'] = 'area parameter is wrong'
        return msg
        
    stdin, stdout, stderr = s.exec_command(create_bk_dir,get_pty=True)  #创建备份目录
    if stderr.read():  #判断执行成功与否
        logging.error("back dir %s create failed,Error msg:%s" % (bk_dir,stderr.read()))
        msg = {} 
        msg['status'] = '1' 
        msg['errmsg'] = 'back dir create failed'
        s.close()
        return msg
    else:         
        logging.info("Back dir %s create sucess" % bk_dir)
    
    stdin, stdout, stderr = s.exec_command(mv_files,get_pty=True)   #执行mv命令
    if stderr.read():   #判断执行成功与否                                
        logging.error("mv files from %s to %s failed,Error msg:%s" % (dir,bk_dir,stderr.read()))
        msg = {}
        msg['status'] = '1'
        msg['errmsg'] = 'mv files failed'
        s.close()
        return msg
    else:
        logging.info("mv files from %s to %s sucess" % (dir,bk_dir))
        msg = {}
        msg['status'] = '0'
        msg['errmsg'] = ''
        s.close()
        return msg        
   

@remove.route("/remove/", methods=['GET', 'POST'])
def main():
    msg = ''
    if request.method == 'POST':
        user = request.form['user']
        ip = request.form['ip']
        dir = request.form['dir']
        area = request.form['area']
        #msg = "user:{};dir:{}".format(user,dir)
        res = LoginAndPerformOperation(ip,loginuser,password,loginport,user,dir,area)
        msg = json.dumps(res)
    else:
        msg = 'hello world!'
    return msg


if __name__ == "__main__":
    bindhost = '0.0.0.0'
    bindport = 9999
    remove.debug = True
    remove.run(host=bindhost, port=bindport)

