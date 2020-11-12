import subprocess
import random
import string
import db_helper as db
from bson.objectid import ObjectId
from hashlib import md5

__author__ = "Arno"


def gen_key_index(token):
    c_key_index = []
    python_key_index = []
    for _ in range(16):
        i = random.SystemRandom().choice(range(32))
        python_key_index.append(i)
        c_key_index.append('0x{:02x}'.format(i))
    python_key_index = bytearray(python_key_index)
    sessions_db = db.mongodb('upload_server', 'session_info')
    sessions_db.insert({'_id': ObjectId(token), 'key_index': ''.join(str(python_key_index))})
    return ', '.join(c_key_index) + '\\'


def config_new_client(model=None, release=None, version=None, machine=None, token=None, task_id=None):
    with open("native_client/jni/info.h", 'r') as f:
        l = f.readlines()
    l[9] = '\"%s\",\n' % model if model is not None else l[10]
    l[10] = '\"%s\",\n' % release if release is not None else l[11]
    l[11] = '\"%s\",\n' % version if version is not None else l[12]
    l[12] = '\"%s\",\n' % machine if machine is not None else l[13]
    l[13] = '\"%s\"' % task_id + '\n' if task_id is not None else l[15]
    l[25] = '\"key=%s\";\n' % token if token is not None else l[27]
    l[27] = gen_key_index(token) + '\n'

    with open("native_client/jni/info.h", 'w+') as f:
        f.writelines(l)

    deploy(model=model, release=release, version=version, machine=machine, task_id=task_id)

    return


def file_md5(fname):
    hash_obj = md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(1024), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def deploy(model=None, release=None, version=None, machine=None, task_id=None):
    client_info_db = db.mongodb('client_db', 'client_info')
    try:
        subprocess.check_output("ndk-build -C native_client", shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError, e:
        _id = client_info_db.save_file("native_client/libs/armeabi/native_client", str(task_id))
        client_info_db.insert(
                {"model": model, "release": release, "version": version, "machine": machine, "file_id": _id,
                 "file_name": str(task_id)})
