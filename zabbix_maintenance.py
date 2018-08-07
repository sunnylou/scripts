#!/usr/bin/env python
# -*-coding:utf-8-*-
###Used to modify the host state####
# Authorized person: Lou Mengxuan  #
# Write at 2017/1/5 12:44          #
####################################
import urllib
import urllib2
import json
import sys
import time
import os
 
now = time.time()

def auth(uid, username, password, api_url):
    """
    zabbix认证
    :param uid:
    :param username:
    :param password:
    :return:
    """
    dict_data = {}
    dict_data['method'] = 'user.login'  # 方法
    dict_data['id'] = uid  # 用户id
    dict_data['jsonrpc'] = "2.0"  # api版本
    dict_data['params'] = {"user": username, "password": password}  # 用户账号密码
    jdata = json.dumps(dict_data)  # 格式化json数据
    content = post_data(jdata, api_url)  # post json到接口
    auth_code = content['result']
    return auth_code  # 返回auth_code
 
 
def post_data(jdata, url):
    """
    POST方法
    :param jdata:
    :param url:
    :return:
    """
    req = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
    response = urllib2.urlopen(req)
    content = json.load(response)
    return content
 
 
def get_maintenance_id(uid,auth_code,hostid,api_url):
    """
    get maintenance id
    """
    n = 0
    maintenanceid = []
    dict_data = {}
    dict_data['method'] = 'maintenance.get'
    dict_data['id'] = uid  # 用户id
    dict_data['jsonrpc'] = "2.0"  # api版本
    dict_data['auth'] = auth_code  # api版本
    dict_data['params'] = {"hostids":hostid}
    jdata = json.dumps(dict_data)  # 格式化json数据
    content = post_data(jdata, api_url)  # post json到接口
    for i in content['result']:
        if int(i['active_till']) > int(now):
	    n += 1
            maintenanceid.append(i['maintenanceid'])
    if n > 0:
        return maintenanceid  # 返回maintenanceid
    else:
        return None
    

def delete_maintenance(uid,maintenance_id, auth_code, api_url):
    """
    delete maintenance
    :return:
    """
    dict_data = {}
    dict_data['method'] = 'maintenance.delete'  # 方法
    dict_data['id'] = uid  # 用户id
    dict_data['jsonrpc'] = "2.0"  # api版本
    dict_data['auth'] = auth_code  # api版本
    maintenance_ids = maintenance_id
    dict_data['params'] = maintenance_ids  # maintenance_id
    jdata = json.dumps(dict_data)  # 格式化json数据
    content = post_data(jdata, api_url)  # post json到接口
    return content  # 返回信息
 
 
def create_maintenance(name, hostid, active_since, active_till, period, auth_code, api_url):
    """
    create maintenance
    :return:
    """
    dict_data = {}
    dict_data['method'] = 'maintenance.create'  # 方法
    dict_data['id'] = uid  # 用户id
    dict_data['jsonrpc'] = "2.0"  # api版本
    dict_data['auth'] = auth_code  # api版本
    dict_data['description'] = "UPDATE" + hostid  # api版本
    hostids = [hostid]
    timeperiods = [{"timeperiod_type": 0, "start_time": 64800, "period": period}]
    dict_data['params'] = {"name": name, "active_since": active_since, "timeperiods": timeperiods,
                           "active_till": active_till, "hostids": hostids}  # 用户账号密码
    jdata = json.dumps(dict_data)  # 格式化json数据
    content = post_data(jdata, api_url)  # post json到接口
    return content  # 返回信息


def get_hostid(hostname, auth_code, uid, api_url):
    """
    use hostname get hostid
    :param hostname:
    :param auth:
    :param uid:
    :return:
    """
    dict_data = {}
    dict_data['method'] = 'host.get'  # 方法
    dict_data['id'] = uid  # 用户id
    dict_data['jsonrpc'] = "2.0"  # api版本
    dict_data['params'] = {"filter":{"host": hostname}}  # 主机名
    dict_data['auth'] = auth_code  # auth串
    jdata = json.dumps(dict_data)  # 格式化json数据
    content = post_data(jdata, api_url)  # post json到接口
    if content['result']:
        hostid = content['result'][0]['hostid']
        return hostid  # 返回hostid
    else:
        pass
 
def logout(uid, auth_code, api_url):
    """
    退出
    :param uid:
    :param auth_code:
    :return:
    """
    dict_data = {}
    dict_data['method'] = 'user.logout'  # 方法
    dict_data['id'] = uid  # 用户id
    dict_data['jsonrpc'] = "2.0"  # api版本
    dict_data['params'] = []
    dict_data['auth'] = auth_code  # auth串
    jdata = json.dumps(dict_data)  # 格式化json数据
    content = post_data(jdata, api_url)  # post json到接口
    return content  # 返回信息


def help_message():
        filename = __file__
        #print filename
        helpmessage = '''Usage:
python {0} enable  ./files/filename(适用于多ip关闭告警)
python {1} enable  IP(like:10.0.174.22)
python {2} disable ./files/filename(适用于多ip开启告警)
python {3} disable IP(like:10.0.174.22)
        '''.format(filename,filename,filename,filename)
        return helpmessage
 

if __name__ == '__main__':
    # user info
    uid = 5 # 用户ID
    username = 'XXX' # zabbix user                                         
    password = 'XXXXX' # zabbix user passwd                                
    api_url = "http://xx.xx.xx.xx/zabbix/api_jsonrpc.php" # zabbix api url 
    if len(sys.argv) < 3:
        print help_message()
        sys.exit(1)
    else:
        if sys.argv[1] == 'enable':
            auth_code = auth(uid, username, password, api_url)  # 认证串
            if auth_code:
		if os.path.isfile(sys.argv[2]):
                    for hostname in open(sys.argv[2],'r'):
                        hostname = hostname.strip(' \n')  # 主机名
                        hostid = get_hostid(hostname, auth_code, uid, api_url)
                        try:
                            if hostid:
				maintenance_id = get_maintenance_id(uid,auth_code,hostid,api_url)
				if maintenance_id:
				    print ("%s\t已经是维护状态，无需再次关闭\n" % (hostname))
				else:
                                    period = 2592000  # 默认关闭一个月
                                    active_since = int(now)  # 开始时间
                                    active_till = int(now) + int(period)  # 结束时间
                                    res = create_maintenance('AutoMaintenance_' + hostname + '_' + str(active_since), hostid, active_since, active_till, period,
                                                             auth_code, api_url)  # 创建维护
                                    print ("%s\t已修改至维护状态\n" % (hostname))
                        except Exception, e:
                            continue
		else:
		    hostname = sys.argv[2]
                    hostid = get_hostid(hostname, auth_code, uid, api_url)
                    try:
                        if hostid:
                            maintenance_id = get_maintenance_id(uid,auth_code,hostid,api_url)
                            if maintenance_id:
                                print ("%s\t已经是维护状态，无需再次关闭\n" % (hostname))
                            else:
                                period = 2592000  # 默认关闭一个月
                                active_since = int(time.time())  # 开始时间
                                active_till = int(time.time()) + int(period)  # 结束时间
                                res = create_maintenance('AutoMaintenance_' + hostname + '_' + str(active_since), hostid, active_since, active_till, period,
                                                         auth_code, api_url)  # 创建维护
                                print ("%s\t已修改至维护状态\n" % (hostname))
                    except Exception, e:
			pass
                logout(uid, auth_code, api_url)  # 退出登录
        elif sys.argv[1] == 'disable':
            auth_code = auth(uid, username, password, api_url)  # 认证串
            if auth_code:
		if os.path.isfile(sys.argv[2]):
                    for hostname in open(sys.argv[2],'r'):
                        hostname = hostname.strip(' \n')  # 主机名
                        hostid = get_hostid(hostname, auth_code, uid, api_url)
                        try:
                            if hostid:
                                maintenance_id = get_maintenance_id(uid,auth_code,hostid,api_url) # 获取主机维护模式id
				if maintenance_id:
                                    req = delete_maintenance(uid,maintenance_id, auth_code, api_url) # 将主机从维护模式中删除
                                    print ("%s\t已从维护状态置为正常监控状态\n" % (hostname))
				else:
				    print ("%s\t已经为正常监控状态，无需再次开启\n" % (hostname))
                        except Exception, e:
                            continue
		else:
                    hostname = sys.argv[2]
                    hostid = get_hostid(hostname, auth_code, uid, api_url)
                    try:
                        if hostid:
                            maintenance_id = get_maintenance_id(uid,auth_code,hostid,api_url) # 获取主机维护模式id
			    if maintenance_id:
                                req = delete_maintenance(uid,maintenance_id, auth_code, api_url) # 将主机从维护模式中删除
                                print ("%s\t已从维护状态置为正常监控状态\n" % (hostname))
			    else:
				print ("%s\t已经为正常监控状态，无需再次开启\n" % (hostname))
                    except Exception, e:
                        pass
                logout(uid, auth_code, api_url)  # 退出登录
        else:
           print help_message()
           sys.exit(1)
