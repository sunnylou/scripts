#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko, time, datetime, os, telnetlib

now = datetime.datetime.now().strftime("%Y%m%d")
basedir = '/root/switch_conf_bk'
currTime = time.time()
deltTime = 3600*24*8 # 8天前

def RemoveFilesBeforeDate(beforeTime, path = "."):
    for eachFile in os.listdir(path):
        f = path + os.sep + eachFile
        lastMTime = os.stat(f).st_mtime
        if os.path.isfile(f) and lastMTime <= beforeTime:
            try:
                os.remove(f)
                #elif os.path.isdir(f):
                #    shutil.rmtree(f)
                #else:
                #    os.remove(f)
                print ("删除 {0}, 成功！".format(f))
            except Exception as e:
                print("删除 {0}, 失败！ 错误如下：".format(f))
                print(e)

def WriteToFile(host,output):
    filename = '%s-%s' % (host, now)
    with open(os.path.join(basedir, filename),'w') as f:
        f.write(output)


def GetConf(host, username, password, showconf, pagesplit, connmode):
    connmode = connmode.strip('\n')
    if connmode == 'ssh':
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(host, 22, username = username, password = password,look_for_keys=False, allow_agent=False)
        except Exception, e:
            print e
        else:
            remote_conn = client.invoke_shell()
            output = remote_conn.recv(1000)
            remote_conn.send("%s\n" % pagesplit )
            time.sleep(1)
            remote_conn.send("\n")
            remote_conn.send("%s\n" % showconf)
            time.sleep(20)
            output = remote_conn.recv(50000000000000)
            WriteToFile(host,output)
    if connmode == 'telnet':
        finish = '>' 
        try:
            tn = telnetlib.Telnet(host, port=23, timeout=10)
        except Exception, e:
            print host, e
        else:
            #tn.set_debuglevel(2)  
    
            # 输入登录用户名  
            tn.read_until('Username:')
            tn.write(username + '\n')
    
            # 输入登录密码  
            tn.read_until('Password:')
            tn.write(password + '\n')
    
            # 登录完毕后执行命令  
            tn.read_until(finish)
            tn.write(pagesplit + '\n')
            time.sleep(1)
            tn.read_until(finish)
            tn.write(showconf + '\n')
            time.sleep(10)
            output = tn.read_very_eager()        
            #output = tn.read_all()        
            WriteToFile(host,output)
            #执行完毕后，终止Telnet连接（或输入exit退出）  
            tn.close() # tn.write('exit\n')  
if __name__ == '__main__':
    with open('/root/switch_conf_bk/script/switch_list','r') as item:
        for line in item:
           print line.split(',')
           GetConf(*line.split(',')) 
    RemoveFilesBeforeDate(currTime - deltTime, path = basedir)
