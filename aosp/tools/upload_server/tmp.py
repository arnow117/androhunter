#!/usr/local/bin/python
__author__ = 'devilk_r'
import base64
from Crypto.Cipher import AES


def main2():
    with open('/root/myProjects/myjni/native_probe/jni/uuid5000.tmp', 'r') as ds:
        uuidl = ds.readlines()
    i = 0
    for i in range(len(uuidl)):
        uuidl[i] = '"' + uuidl[i].strip('\n') + '",\n'
    uuidl[len(uuidl) - 1] = uuidl[len(uuidl) - 1].replace(',', '}')
    with open('/root/myProjects/myjni/native_probe/jni/info.h', 'w') as f:
        f.writelines(uuidl)
        f.write('test')
    return


def encrypt_uuid():
    with open('/root/myProjects/myjni/native_probe/jni/uuid-30-1-new', 'r') as ds:
        uuidl = ds.readlines()
    with open('/root/myProjects/myjni/native_probe/jni/uuid-30-1-enc', 'w') as dt:
        for i in range(len(uuidl)):
            o = AES.new('Hu0McGxT7V1k9QoF', AES.MODE_CBC, 'Hu0McGxT7V1k9QoF')
            if len(uuidl[i].strip('\n')) == 27:
                uuidl[i] = '"' + base64.b64encode(o.encrypt(uuidl[i].strip('\n') + ' ' * 5)) + '",\n'
                dt.write(uuidl[i])


def write2code():
    with open('/root/myProjects/myjni/native_probe/jni/info.h', 'r') as dp:
        cache_lines = dp.readlines()
    with open('/root/myProjects/myjni/native_probe/jni/uuid-30-1-enc', 'r') as ds:
        uuidl = ds.readlines()
    for i in xrange(20000):
        cache_lines.append(uuidl[i])
    with open('/root/myProjects/myjni/native_probe/jni/info.h', 'w') as dt:
        for line in cache_lines:
            dt.write(line)
# 20000

if __name__ == '__main__':
    write2code()
