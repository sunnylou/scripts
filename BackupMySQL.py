#!/usr/bin/env python
#-*- coding: UTF-8 -*- 
##############################################################
#
# Date: 2017/09/22 
# Filename: BackupMySQL.py
# Description: backup mysql files,base percona xtrabackup
#
# 备份mysql数据库数据，在主库进行数据同步备份:10.99.10.22
# 备份的数据存储目录: /data/backup/mysqlbak/
# 备份策略是每天备份一次，以当天日期命名的目录，如:20170922
#
##############################################################


# Import required python libraries
import os 
import sys 
import time
import logging 
import datetime 
import subprocess 
import shutil

logging.basicConfig(level=logging.DEBUG, 
                format='[%(asctime)s]  [%(levelname)s] %(message)s', 
                datefmt='%Y-%m-%d %H:%M:%S', 
                filename='/software/scrpits/backupMysql/backupMysql.log', 
                filemode='a') 

# 配置数据库连接信息
DB_HOST = 'xx.xx.xx.xx'
DB_USER = 'bakuser'
DB_USER_PASS = 'bakpasswd'

# 配置本地保留多少天的数据备份,默认保留7天
DataSave = 30

# 配置备份的基础目录
BackupPath = '/data/backup/mysqlbak/'

DayTime = time.strftime('%Y%m%d')
TodayBackupPath =  BackupPath + DayTime


def Check():
    '''备份前检查，如果目录存在则退出，否则创建备份目录'''
    if os.path.exists(TodayBackupPath):
        res = 'The backup directory already exists: %s. exit ...' % TodayBackupPath
        print res
        logging.error(res)
        sys.exit()
    else:
        os.makedirs(TodayBackupPath)
        res1 = "creating backup folder %s " % TodayBackupPath
        logging.info(res1)


def BackupDB():
    '''备份数据库，定义备份指令，参数'''
    Check()

    logging.info('Start backing up the database.')
    iArgs = "--slave-info  --no-timestamp"
    BackupCmd = "/usr/bin/innobackupex %s --host=%s  --user=%s --password=%s %s "  \
                   %  (iArgs, DB_HOST, DB_USER, DB_USER_PASS, TodayBackupPath) 
    p = subprocess.Popen(BackupCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout,stderr = p.communicate()
    logging.info(stdout)
    logging.info(stderr)
    logging.info('The database backup is complete')

def GetTimePoint(days):
    ''' 返回需要删除的时间点 '''
    CurrTime = time.time()
    DelTime = 3600*24*int(days)
    TimePoint = CurrTime - DelTime
    return TimePoint


def CheckDir(cdir):
    ''' 删除文件夹的函数 '''
    try:
        if os.path.isdir(cdir):
            shutil.rmtree(cdir)
            s = 'remove dir %s succ ...' % cdir
            logging.info(s)
    except Exception as e:
        s = 'remove dir %s FAIL !!! %s' % (cdir, e)
        logging.error(s)
    

def CleanOld(beforeTime, path):
    ''' 遍历备份目录，获取目录mtime时间,比对时间戳，删除之前目录 '''
    logging.warn('Start cleaning up old backup data...')
    for eachdir in os.listdir(path):
        f = path + eachdir
        lastMtime = os.stat(f).st_mtime
        if lastMtime <= beforeTime:
            CheckDir(f)            
    
if __name__ == '__main__': 
    BackupDB()    
    t = GetTimePoint(DataSave)
    CleanOld(t, BackupPath) 

