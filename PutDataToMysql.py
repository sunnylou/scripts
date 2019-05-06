#-*- coding: utf-8 -*-
#!/usr/bin/python
###############################################################
#   authorizer：MengXuan.Lou                                  #
#   Written in 2017-03-14 10:54                               #
#   Script is used to insert the topic data to mysql tables   #
###############################################################
import re
import subprocess
import time
import MySQLdb
import sys
import logging

now = time.strftime('%Y%m%d%H',time.localtime(time.time()))
filename = '/tmp/%scount.txt' % now
partitionfilename = '/tmp/%spartition.txt' % now

#日志设置
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/var/log/TopicToMysql.log',
                filemode='a')

#初始化表topic数据
def InitTopicData():
    topiclines = []
    p = subprocess.Popen("for i in $(cat  /tmp/count.list|grep -v '#'|grep shengchan|grep -v cool|awk '{print $1}');do grep -w $i %s |grep shengchan|grep -v cool;done" % filename,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    stdout,stderr = p.communicate()
    for i in stdout.split("\n"):
	if i:
	    w = i.split(" ")[0]+" "+i.split(" ")[4]+" "+i.split(" ")[3]
            line = re.sub(",", " ", w).split()
            topiclines.append(line)
    return topiclines

#初始化表moffset数据
def InitMoffsetData():
    moffsetlines = []
    p = subprocess.Popen("for i in $(cat  /tmp/count.list|grep -v '#'|grep shengchan|grep -v cool|awk '{print $1}');do grep -w $i %s|grep shengchan|grep -v cool;done" % filename,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    stdout,stderr = p.communicate()
    for i in stdout.split("\n"):
        if i:
            w = i.split(" ")[0]+" "+i.split(" ")[4]+" "+i.split(" ")[1]+" "+i.split(" ")[2]+" "+i.split(" ")[3]
            line = re.sub(",", " ", w).split()
	    line[2],line[3]=line[3],line[2]
	    line.insert(0,now)
            moffsetlines.append(line)
    return moffsetlines

#初始化表topicpartition数据
def InitTopicPartitionData():
    partitionlines = []
    p = subprocess.Popen("cat %s|grep shengchan|grep -v cool" % partitionfilename,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    stdout,stderr = p.communicate()
    for i in stdout.split("\n"):
        if i:
            w = i.split(",")[0]+" "+i.split(",")[5]+" "+i.split(",")[1]+" "+i.split(",")[4]+" "+i.split(",")[6]
            line = re.sub(",", " ", w).split()
            line.append("none")
            partitionlines.append(line)
    return partitionlines

#初始化表topicpartitiondetail数据
def InitTopicPartitionDetailData():
    partitiondetaillines = []
    p = subprocess.Popen("cat %s|grep shengchan|grep -v cool" % partitionfilename,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    stdout,stderr = p.communicate()
    for i in stdout.split("\n"):
        if i:
            w = i.split(",")[0]+" "+i.split(",")[5]+" "+i.split(",")[1]+" "+i.split(",")[3]+" "+i.split(",")[2]+" "+i.split(",")[4]+" "+i.split(",")[6]
            line = re.sub(",", " ", w).split()
            line.insert(0,now)
            line.insert(7,"none")
            #line.append("none")
            partitiondetaillines.append(line)
    return partitiondetaillines

#插入topic数据到mysql
def PutTopicDataToMysql():
    logging.info("Begin insert data to topic")
    try:
        conn=MySQLdb.connect(db='myflume',host='10.0.178.120',user='myflume',passwd='myflume',charset='utf8')
        cursor = conn.cursor()
        args3 = InitTopicData()
        for i in args3:
	    selectsql = "select * from topic where topicname = '%s' and groupname = '%s'" % (i[0],i[1])
            count = cursor.execute(selectsql)
            result = cursor.fetchone()
            if result:
	        updatesql = "update topic set offset='%s' where topicname='%s' and groupname = '%s'" % (i[2],i[0],i[1])
                cursor.execute(updatesql)
            else:
                cursor.execute("insert into topic values(%s,%s,%s)",i)
	conn.commit()
	cursor.close()
	conn.close()
	logging.info("Insert the topic data complete")
    except MySQLdb.Error,e:
        logging.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
	logging.error("Insert the failure")
    except:
        logging.error('Exception:' + str(sys.exc_info()[1]))
        logging.error("Insert the failure")

#插入moffset数据到mysql
def PutMoffsetDataToMysql():
    logging.info("Begin insert data to moffset")
    try:
        conn=MySQLdb.connect(db='myflume',host='10.0.178.120',user='myflume',passwd='myflume',charset='utf8')
        cursor = conn.cursor()
        args6 = InitMoffsetData()
        for x in args6:
            cursor.execute("insert into moffset values(%s,%s,%s,%s,%s,%s)",x)
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Insert the moffset data complete")
    except MySQLdb.Error,e:
        logging.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
	logging.error("Insert the failure")
    except:
        logging.error('Exception:' + str(sys.exc_info()[1]))
        logging.error("Insert the failure")

#插入topicpartition数据到mysql
def PutTopicpartitionDataToMysql():
    logging.info("Begin insert data to topicpartition")
    try:
        conn=MySQLdb.connect(db='myflume',host='10.0.178.120',user='myflume',passwd='myflume',charset='utf8')
        cursor = conn.cursor()
        args6 = InitTopicPartitionData()
        for i in args6:
            selectsql = "select * from topicpartition where topicname = '%s' and groupname = '%s' and partitionnum = '%s'" % (i[0],i[1],i[2])
            count = cursor.execute(selectsql)
            result = cursor.fetchone()
            if result:
                updatesql = "update topicpartition set offset= '%s',ownerhost= '%s' where topicname= '%s' and groupname = '%s' and partitionnum = '%s'" % (i[3],i[4],i[0],i[1],i[2])
                cursor.execute(updatesql)
            else:
                cursor.execute("insert into topicpartition values(%s,%s,%s,%s,%s,%s)",i)
        conn.commit()
        cursor.close()
        conn.close()
	logging.info("Insert the topicpartition data complete")
    except MySQLdb.Error,e:
        logging.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        logging.error("Insert the failure")
    except:
        logging.error('Exception:' + str(sys.exc_info()[1]))
        logging.error("Insert the failure")

#插入topicpartitiondetail数据到mysql
def PutTopicPartitionDetailDataToMysql():
    logging.info("Begin insert data to topicpartitiondetail")
    try:
        conn=MySQLdb.connect(db='myflume',host='10.0.178.120',user='myflume',passwd='myflume',charset='utf8')
        cursor = conn.cursor()
        args9 = InitTopicPartitionDetailData()
        for x in args9:
            cursor.execute("insert into topicpartitiondetail values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",x)
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Insert the topicpartitiondetail data complete")
    except MySQLdb.Error,e:
        logging.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        logging.error("Insert the failure")
    except:
        logging.error('Exception:' + str(sys.exc_info()[1]))
        logging.error("Insert the failure")

#执行
if __name__ == "__main__":
    PutTopicDataToMysql()
    PutMoffsetDataToMysql()
    PutTopicpartitionDataToMysql()
    PutTopicPartitionDetailDataToMysql()
