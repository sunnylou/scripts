#!/usr/bin/env python
#coding:utf-8

'''
Created on 2016年7月7日

@author: mengxuan.lou
'''

from rediscluster import StrictRedisCluster
import sys
import time

def redis_cluster():
    redis_nodes =  [{'host':'10.34.2.44','port':8381},
                    {'host':'10.34.2.44','port':8382},
                    {'host':'10.34.2.44','port':8383},
                    {'host':'10.34.2.44','port':8384},
                    {'host':'10.34.2.44','port':8385},
                    {'host':'10.34.2.44','port':8386},
                    {'host':'10.34.2.44','port':8387}
                   ]
    try:
        redisconn = StrictRedisCluster(startup_nodes=redis_nodes)
    except Exception,e:
        print "Connect Error!"
        sys.exit(1)
    btime = int(time.time())
    print "开始时间:" + str(btime)
    for i in range(1000):
        redisconn.set('loutest'+str(i),'mengxuantest'+str(i))
        print "loutest%s is: " % str(i), redisconn.get('loutest'+str(i))
        redisconn.delete('loutest'+str(i))
    atime = int(time.time())
    print "结束时间:" + str(atime)
    usetime = atime - btime
    print "用时:" + str(usetime)
if __name__ == "__main__":
    redis_cluster()
