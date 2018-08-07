#!/usr/bin/python
# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
import MySQLdb
import datetime
from os import getcwd,path

pwd = '/software/scripts'
today = datetime.datetime.now().strftime("%Y%m%d")
#today = '20170705'
mailto_list = ["test@qq.com"]
mail_host = "smtp.qq.com"  #设置服务器
mail_user = "loumx@qq.com"    #用户名
mail_pass = "pass"   #口令
res = []
customer = []
form = []

def send_mail(to_list,sub,content):  #to_list：收件人；sub：主题；content：邮件内容
    me = "LouMengXuan"+"<"+mail_user+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content,_subtype='html',_charset='utf-8')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = sub    #设置主题
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP_SSL(mail_host,465)
	#s.set_debuglevel(1)
        s.login(mail_user,mail_pass)  #登陆服务器
        s.sendmail(me, to_list, msg.as_string())  #发送邮件
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

def query_kv_data_from_mysql():
    conn = MySQLdb.connect(host="xx.xx.xx.x",user="user",passwd="pass",db="bdcsc2_report",charset="utf8")
    cursor = conn.cursor()
    sql = "select date,dbname,sum(count) as cnt from bdcsc2_kv_data_count  where date='%s' and dbname != 'ctyun_bdcsc_sys' group by dbname having cnt>1000000000;" % today
    cursor.execute(sql)
    for row in cursor.fetchall():
        res.append(list(row))
    cursor.close()
    conn.close()
    return res

def mail_html_message():
    z = 0
    res = query_kv_data_from_mysql()
    if res:
        nu = len(res)
        f = open(path.join(pwd,'customer.txt'),'r')
        for i in f:
            x = i.split(",")
            customer.append(x)
        f.close()
        while z < nu:
            for x in res:
                Customer_shorthand = x[1]
                for y in customer:
                   if Customer_shorthand == y[0].decode('utf-8'):
                	a = 'a' + str(z)
            	        a = []
                        a.append(y[1].strip())
                	a.append(x[1])
                	a.append(x[2])
                	a.append(x[0])
        		form.append(a)
            	z += 1
        if form:
            noises = ['All','以下客户KV数据已超量','请通知客户并回复清理时间','谢谢']
            message = """
Hi,%s:
   %s,%s,%s
                      """ % (noises[0].decode('utf-8'),noises[1].decode('utf-8'),noises[2].decode('utf-8'),noises[3].decode('utf-8'))
            html_start = """
                    <font face="Courier New, Courier, monospace"><pre>
                         """
            html_end = """
                    </table>
                    </pre></font>
                    Lou MengXuan <br/>
                    Best Regards
                       """
            th = ["客户名称","库名","数据量","时间"]
            title = """
                    <table border="1" bordercolor="black" cellspacing="0px" cellpadding="4px">
                    <tr bgcolor="#0099FF">
                    <th>%s</th>
                    <th>%s</th>
                    <th>%s</th>
                    <th>%s</th>
                    </tr>
                    """ % (th[0].decode('utf-8'),th[1].decode('utf-8'),th[2].decode('utf-8'),th[3].decode('utf-8'))
            n = 0
            yy = ''
            while n < nu:
                for i in form:
                    body = 'body' + str(n)
                    body = """
                    <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    </tr>
                           """ % (i[0].decode('utf-8'),i[1],i[2],i[3])
                    yy += body
                    n += 1
            content = html_start + message + title.lstrip() + yy.rstrip() + html_end
            return content
        else:
	    print "By the library name no corresponding relationship with the customers"
	    return None
    else:
	print "%s no excess of library data" % today
	return None

if __name__ == '__main__':
    content = mail_html_message()
    if content:
        if send_mail(mailto_list,"Kv Data Clean --%s" % today,content):
            print "%s send success" % today
        else:
            print "%s send failure" % today
