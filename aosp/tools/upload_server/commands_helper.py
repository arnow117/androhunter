#!/usr/local/bin/python
__author__ = 'devilk_r'
import os
import subprocess


def command(type,path,target='',tools_path = "tools/",comm = False):
    command_line = {
                       "xml": "java -jar {tools_path}AXMLPrinter2.jar {path} > {target}",
                       "smali": "java -jar {tools_path}baksmali.jar {path} -o {target}",
                       "apktool_d": "java -jar {tools_path}apktool.jar d -o {path} {target}",
                       "apktool_d_fast": "java -jar {tools_path}apktool.jar d -r -o {path} {target}",
                       "apktool_b": "java -jar {tools_path}apktool.jar b {path}",
                       "cert": "keytool -printcert -file {path} > {target}",
                       "download": "",
                       "diff": "diff -b {path} {target}"
     }[type].format(tools_path=tools_path, path=path, target=target)
    if comm:
        try:
            r = subprocess.check_output(command_line,shell=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError, e:
            return e
    else:
        r = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r.wait()
        # r.communicate()
if __name__ =="__main__":
    command("smali", "../apk/Calculator.apk", "../out/tmp")