#!/usr/bin/env python
#-*- encoding:utf-8 -*-
#file:EBSurf.py
import sys
import httplib
import urllib
import poplib
import email
import string
import getopt 
import os
import base64
import time
import socket

def myencode(str):
    if(type(str) == list):
        for everystr in str:
            everystr = myencode(everystr)
        return str
    else:
        return base64.b64encode(str)

def mydecode(str):
    if(type(str) == list):
        for everystr in str:
            everystr = mydecode(everystr)
        return str
    else:
        return base64.b64decode(str)

def readfile(filename):
    
    f = open(filename,'r')
    try: 
        configcontent = f.read()
        return configcontent
    except IOError:
        print "Read config file error，please check the config file if exists"
    finally:
        f.close()

def getconfigmap(configcontent):
    configitems = configcontent.split()
    configs = {}
    for item in configitems:
        (key,value) = item.split('=')
        configs[key] = value

    return configs
def writefile(filename,content):
    
    f = open(filename,'w')
    try:
        f.write(content)
    except IOError:
        print "write config file error"
    finally:
        f.close()
    
def getfromemail(name,mailpassword):
    mastersubjects = ["EBUPT VPN/PROXY SERVICES PASSWORD NOTICE MAIL","EB VPN Password for "+name,"Your EBUPT VPN PASSWORD"]
    server = None
    try:
        server = poplib.POP3('pop.exmail.qq.com')
        mailaddress = name + '@ebupt.com'
        server.user(mailaddress)
        server.pass_(mailpassword)
    except poplib.error_proto:
        print "Login failed, please check if the user name or password is correct."
        os.system('pause')
        sys.exit(1)
    except socket.gaierror:
        print 'Network is error,please check...'
        os.system('pause')
        sys.exit(1)

    (mailnum,mailsize) = server.stat()
    mailcontent = None

    for selected in range(0,mailnum):
        response,message,octets=server.retr(mailnum-selected)
        mail=email.message_from_string(string.join(message,'\n'))
        if( mail['subject'] in mastersubjects):
            charset = mail.get_content_charset()
            if charset == None :
                mailcontent = mail.get_payload()
            else:
                mailcontent = unicode(mail.get_payload(decode='base64'),charset)
            break
    if(mailcontent) :
        lines = mailcontent.split('\n')
        if(mail['subject'] == "Your EBUPT VPN PASSWORD"):
            (tip,password) = lines[1].split(': ')
        else:
            (tip,password) = lines[5].split(': ')
        return (name,password)
    else:
        print "Can't find the corresponding e-mail, please check if the VPN password e-mail exist."
        os.system('pause')
        sys.exit(1)
      
def dologin(auth_user,auth_pass):

    host = '10.1.1.7'
    port = 8000
    uri = '/'
    headers = {  
        "Content-Type": "application/x-www-form-urlencoded",  
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)",  
        }  
        
    params = urllib.urlencode({'auth_user':auth_user,'auth_pass':auth_pass,'accept':'登录'})
    try:
        conn = httplib.HTTPConnection(host,port,timeout=10)
        conn.request('POST',uri,params,headers)
        res = conn.getresponse()
        conn.close()
        return res.status
    except socket.timeout:
        return -1
    except socket.error:
        return -1

def usage():
    print """Usage:
    -h --help: Show help Information
    -u username: set username  of your email 
    -p password: set password of your email 
    no option: excute the file to autologin,before this you should set your username and password of your email in order to the program could enter your mailboxto get the VPN password"""
    os.system('pause')
    sys.exit()

def configtip(tiptype=0):
    if tiptype == 0 :
        print """You must set  username and password of your email like this:%s -u username -p password""" % sys.argv[0]
    elif tiptype ==1 :
        print """Can not find the file 'config'!You must set the username and password of your email first."""
    else:
        print """The config is demaged! Can not find the file 'config'!You must set the username and password of your email again."""

def tip(tiptype):
    if tiptype == 0 :
        print "Start overview the mail to find vpn password and it may takes a few minutes,please wait!"
    elif tiptype == 1 :
        print "A new week is comming ! overview the mail to find vpn password again and it may takes a few minutes,please wait!"
    elif tiptype == 2 :
        print "Already get the vpn password and  the config file is written again"
    elif tiptype == 3 :
        print "Start login...."
    elif tiptype == 4 :
        print "Login successful!"
    elif tiptype == 5 :
        print "Login failed!"
    elif tiptype == 6 :
        print "Can not connect to login server !Please confirm you connect to the internet and you are in a EB network environment!"
    else:
        print "welcome "


def checkNameAndPassword(name,mailpassword):
    try:
        server = poplib.POP3('pop.exmail.qq.com')
        mailaddress = name + '@ebupt.com'
        server.user(mailaddress)
        server.pass_(mailpassword)
        return 0
    except poplib.error_proto:
        return -1
    #网络异常
    except socket.gaierror:
        return -2
        
def configAccount(configfile):    
    print 'Please input the username and password of your email:'    
    while True:
        name = raw_input("name:")
        mailpassword = raw_input("password:")
        if name=="" or mailpassword =="":
            print 'Error input,please input again.'
        else:
            print 'Checking the username and the password.Be sure you connect to the internet and you are in a EB network environment.'
            checkresutl = checkNameAndPassword(name,mailpassword)
            if checkresutl==0:
                break;
            elif checkresutl==-1:
                print 'Username or password is error,please input again...'
            else:
                print 'Network is error,please check and try it again...'
    tip(0)
    (auth_user,auth_pass) = getfromemail(name,mailpassword)
    content = 'name='+auth_user+' mailpassword='+mailpassword+' vpnpassword='+auth_pass+' week='+time.strftime('%W') #记录周数
    writefile(configfile,myencode(content))
    tip(2)

def checkconfig(configfile):
    if(not os.path.isfile(configfile)):
        configtip(1)
        configAccount(configfile)
    configcontent = readfile(configfile)
    configs = getconfigmap(mydecode(configcontent))
    configkeys = ['name','mailpassword','vpnpassword','week']

    for key in configkeys:
        if(not configs.has_key(key)):
            configtip(2)
            configAccount(configfile)
    nowweek =  time.strftime('%W')
    if( configs['week'] != nowweek) :
        tip(1)
        (configs['name'],configs['vpnpassword']) = getfromemail(configs['name'],configs['mailpassword'])
        content = 'name='+configs['name']+' mailpassword='+configs['mailpassword']+' vpnpassword='+configs['vpnpassword']+' week='+nowweek #记录周数
        writefile(configfile,myencode(content))

    return (configs['name'],configs['vpnpassword'])

def handleoption(option): 
    mailname = mailpasswd = ''
    try:
        opts,args = getopt.getopt(option,'hu:p:',["help"])
        for opt,value in opts:
            if(opt == '-h' or opt == '--help'):
                usage()
            elif(opt == '-u'):
                mailname = value.split('@')
            elif(opt == '-p'):
                mailpasswd = value
            else:
                usage()
    except getopt.GetoptError:
        usage()

    if(not mailname or not mailpasswd) :
        configtip(0)
        os.system('pause')
        sys.exit()
    else:
        return(mailname[0],mailpasswd)
#由于用py2exe将python转换为exe时，脚本目录会发生变化，该函数是为了确认脚本目录，以便写入配置文件
def getscriptdir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    
def main():    
    configfile = getscriptdir() +'/config'
    if(len(sys.argv) == 1):
        (auth_user,auth_pass) = checkconfig(configfile)
    else:
        (name,mailpassword) = handleoption(sys.argv[1:])
        tip(0)
        (auth_user,auth_pass) = getfromemail(name,mailpassword)
        content = 'name='+name+' mailpassword='+mailpassword+' vpnpassword='+auth_pass+' week='+time.strftime('%W') #记录周数
        writefile(configfile,myencode(content))
        tip(2)
    
    tip(3)
    status = dologin(auth_user,auth_pass)
    if(status == 302 ): #登录成功情况下，因为其会重定向，所以响应码为302
        tip(4)
    elif(status == 200):
        tip(5)
    else:
        tip(6)
    os.system('pause')

if __name__ == '__main__':
    main()

