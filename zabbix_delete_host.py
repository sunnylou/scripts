#!/usr/bin/env python
# -*-coding:utf-8-*-
###    Used to delete the host  ####
# Authorized person: Lou Mengxuan  #
# Write at 2017/1/5 12:44          #
####################################
import urllib
import urllib2
import json
import sys
import time
import os


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
    # content = response.read()
    content = json.load(response)
    return content

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
        return

def delete_host(hostid, auth_code, uid, api_url):
    dict_data = {}
    dict_data['method'] = 'host.delete'  # 方法
    dict_data['id'] = uid  # 用户id
    dict_data['jsonrpc'] = "2.0"  # api版本
    dict_data['params'] = [hostid]  # 主机名
    dict_data['auth'] = auth_code  # auth串
    jdata = json.dumps(dict_data)  # 格式化json数据
    content = post_data(jdata, api_url)  # post json到接口
    return content

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
        helpmessage = '''
Usage:
python {0} IP(like：10.0.174.22)
python {1} filename
        '''.format(filename,filename)
        return helpmessage



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print help_message()
        sys.exit(1)
    uid = 5 # 用户ID
    username = 'XXX' # zabbix user
    password = 'XXXXX' # zabbix user passwd
    api_url = "http://xx.xx.xx.xx/zabbix/api_jsonrpc.php" # zabbix api url
    auth_code = auth(uid, username, password, api_url)
    if auth_code:
	if os.path.isfile(sys.argv[1]):
	    for host in open(sys.argv[1],"r"):
                hostname = host.strip("\n")
                hostid = get_hostid(hostname, auth_code, uid, api_url)
                if hostid:
                    delete = delete_host(hostid, auth_code, uid, api_url)
                    print("%s 已从监控系统删除" % hostname)
                else:
                    print("%s 未添加监控" % hostname)
	else:
            hostname = sys.argv[1]
            hostid = get_hostid(hostname, auth_code, uid, api_url)
            if hostid:
                delete = delete_host(hostid, auth_code, uid, api_url)
                print("%s 已从监控系统删除" % hostname)
            else:
                print("%s 未添加监控" % hostname)
        logout(uid, auth_code, api_url)


