#-*- coding: utf-8 -*-
#!/usr/bin/python
import paramiko
import threading
import sys
import subprocess
import logging
import Queue


queue=Queue.Queue()


#日志设置
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/var/log/fenfa.log',
                filemode='a')


#ssh连接执行命令
def ssh2(ip,username,password,cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,password,timeout=5)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        #stdin, stdout, stderr = ssh.exec_command('chown zabbix:zabbix /tmp/zabbix/ -R')
err = stderr.read().strip()
        if err:
            logging.error(err)
    #logging.error("%s change owner and group failed" % (ip))
    else:
    #logging.info("%s change owner and group succeed" % (ip))
    logging.info("%s exec %s succeed" % (ip,cmd))
ssh.close()
    except Exception,e:
        logging.error('%s exec command\t%s'%(ip,e))


#批量发送文件
def sftp(queue,username,password):
    while True:
ip = queue.get()
print ip
        try :
    mkdir = "if [ ! -d /etc/zabbix/zabbix_scripts ];then mkdir -p /etc/zabbix/zabbix_scripts;fi"
    ssh2(ip,username,password,mkdir)
            t = paramiko.Transport((ip, 22))
            t.connect(username=username, password=password)
            sftp =paramiko.SFTPClient.from_transport(t)
            p = subprocess.Popen("ls /bdcc/collection/%s" % ip,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            stdout,stderr = p.communicate()
            #print stdout
            for filename in stdout.split("\n"):
                if filename:
                    sftp.put("/bdcc/collection/%s/%s" % (ip,filename),"/etc/zabbix/zabbix_scripts/%s" % filename)
                    logging.info('send to %s %s succeed' % (ip,filename))
    chown = "chown zabbix:zabbix /etc/zabbix/zabbix_scripts -R"
            ssh2(ip,username,password,chown)
            t.close()
        except Exception,e:
            logging.error('%s\t%s'%(ip,e))
        queue.task_done()
if __name__=='__main__':
    logging.info("Begin......")
    ip = []
    x = subprocess.Popen("ls /bdcc/collection/",stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    stdout,stderr = x.communicate()
    for ipa in stdout.split("\n"):
        if ipa:
            ip.append(ipa)
    #print ip
    username = "user"
    password = "passwd"
    for i in xrange(2):
       t =threading.Thread(target=sftp,args=(queue,username,password))
       t.setDaemon(True)
       t.start()
    
    for s in ip:
       print s
       queue.put(s)
    queue.join()
    logging.info("End")
