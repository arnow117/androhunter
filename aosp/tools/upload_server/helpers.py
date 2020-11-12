__author__ = 'devilk_r'
import os
import logging

import time
def perror(msg,e='None'):
    print "[-] %s" %msg
    with open('log/error','a+') as f:
                f.writelines('%s:\nError when preprocessing!\n%s\n\n' %(time.ctime(), e))
def pinfo(msg):
    print "[+] %s" %msg
def pdebug(msg):
    logging.debug("[+] %s" %msg)

