#!/usr/local/bin/python
from flask import Flask
from flask import request
from flask import escape
from flask import Response
from hashlib import md5
from flask import make_response
from werkzeug.utils import secure_filename
import datetime
from binascii import hexlify, unhexlify
import crypto
import os
import db_helper as db
from bson.objectid import ObjectId
import random
import string
import shutil

__author__ = 'devilk_r'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 35 * 1024
TMP_UPLOAD_FOLDER = '/tmp'
TRUST_FOLDER = '/tmp/trust'
base_info_db = db.mongodb('upload_server', 'base_info')
session_info_db = db.mongodb('upload_server', 'session_info')
cookie_info_db = db.mongodb('upload_server', 'cookie_info')
upload_info_db = db.mongodb('upload_server', 'upload_info')
upload_task_info_db = db.mongodb('upload_server', 'upload_task_info')


@app.route('/collect', methods=['GET', 'POST'])
def collect():
    error = 'error!'
    key_index = None
    data = None
    if request.method == 'POST':
        print 'form : %s' % request.form
        agent = request.headers.get('User-Agent')
        if agent and agent != "29bd7da7271b5515f402128c8f5c5377":
            return error
        key = request.cookies.get('key')
        if key:
            print 'key is %s' % key
            message = check_session(str(key))
            # for test only
            # key_index = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        else:
            return 'Key error'

        if message is not None:
            key_index = message
        else:
            upload_path = check_cookie(str(key))
            if upload_path is not None and request.files.has_key('file'):
                print 'receive file %s' % request.files
                return handle_upload_file(request.files['file'], upload_path)

        if key_index is None:
            return 'no key_index!!!'

        if len(request.form) > 0:
            data = crypto.decrypt(unhexlify(request.form['data']), crypto.get_key(key_index))
            arg_list = data.split('&')
            arg_dict = {}
            for i in arg_list:
                g = i.split('=')
                if g and len(g) == 2:
                    arg_dict[g[0]] = g[1]
            return handle_request(arg_dict, key_index)

    return 'fatal error'


TRUST_VALUE = 2
info_cache = {}
item_cache = {}


def handle_request(arg_dict, key_index):
    error = 'message error!'
    if arg_dict.has_key('id'):

        if arg_dict.has_key('size') and arg_dict.has_key('md5'):
            # filter
            if arg_dict['id'].isdigit() and arg_dict['size'].isdigit() and arg_dict['md5'].isalnum() and check_id(
                    arg_dict['id']):
                if info_cache.has_key(arg_dict['id']):
                    for item in info_cache[arg_dict['id']]:
                        if item['size'] == arg_dict['size'] and item['md5'] == arg_dict['md5']:
                            item['count'] += 1
                            if item['count'] > TRUST_VALUE:
                                if new_upload_tasks(arg_dict['id'], item['size'], item['md5']):
                                    info_cache.pop(arg_dict['id'])
                        else:
                            info_cache[arg_dict['id']].append(
                                    dict({'size': arg_dict['size'], 'md5': arg_dict['md5'], 'count': 1}))
                else:
                    info_cache[arg_dict['id']] = []
                    info_cache[arg_dict['id']].append(
                            dict({'size': arg_dict['size'], 'md5': arg_dict['md5'], 'count': 1}))
                return 'OK'
            return error

        elif arg_dict['id'].isdigit():
            count, upload_path = get_upload_info(arg_dict['id'])
            if upload_path is not None and count is not None:
                return response_with_cookie(count, upload_path, key_index)
            else:
                return crypto.encrypt('boot_info', crypto.get_key(key_index))
        else:
            return error


def new_upload_tasks(task_id, size, hash_value):
    if upload_info_db.insert({'_id': ObjectId(str(task_id)), 'size': int(size), 'md5': hash_value}):
        total_count = int(size) / (32 * 1024) + 1
        for count in range(total_count):
            upload_task_info_db.insert(
                    {'task_id': task_id, 'upload_offset': count, 'upload_done': False})
        base_info_db.update_one({'_id': ObjectId(str(task_id))}, {"$set": {'has_task': True}})
        return True
    return False


def del_task(task_id):
    # delete upload_info_db & session_info_db & task_info_db
    r = base_info_db.query_one({'_id': ObjectId(str(task_id))})
    if r:
        session_info_db.delete_one({'_id': ObjectId(str(r['token']))})
        upload_info_db.delete_one({'_id': ObjectId(str(task_id))})
        upload_task_info_db.delete_many({'task_id': str(task_id)})
        base_info_db.update_one({'_id': ObjectId(str(task_id))},
                                {'$set': {'has_done': True, 'end_date': datetime.datetime.now()}})
        print "collect %s boot.img  done!" % str(r['model'])
    # All Done!!!!!!!
    return


def merge_boot(task_id):
    path = os.path.join(TRUST_FOLDER, str(task_id))
    # path = /tmp/trust/1234567890ab/
    boot = open(os.path.join(path, 'boot.img'), 'wb')
    for i in range(len(os.listdir(path)) - 1):
        with open(os.path.join(path, str(i))) as f:
            boot.writelines(f.readlines())
    boot.close()
    return


def check_boot(task_id):
    path = os.path.join(TRUST_FOLDER, str(task_id) + '/boot.img')
    info = upload_info_db.query_one({'_id': ObjectId(str(task_id))})
    hash_value = file_md5(path)
    if info and info['md5'] == hash_value:
        _id = base_info_db.save_file(path, hash_value)
        base_info_db.update_one({'_id': ObjectId(task_id)},
                                {'$set': {'boot_id': _id, 'boot_md5': hash_value}})
        return True
    return False


def check_path(path):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)


def cookie_generator(length):
    return ''.join(random.SystemRandom().choice(string.digits) for _ in range(length))


def response_with_cookie(offset, upload_path, key_index):
    while True:
        cookie = cookie_generator(24)
        if session_info_db.query_one({'_id': ObjectId(cookie)}) is None:
            break
    res = crypto.encrypt('boot_skip=%d&cookie=%s' % (offset, cookie), crypto.get_key(key_index)),
    cookie_info_db.insert({'_id': ObjectId(cookie), 'upload_path': upload_path})
    return res


def file_md5(fname):
    hash_obj = md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(1024), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def handle_upload_file(upload_file, store_path):
    if upload_file:
        check_path(store_path)
        i = len(os.listdir(store_path))
        filename = str(i) + '.tmp'
        upload_file.save(os.path.join(store_path, filename))
        if i > TRUST_VALUE:
            hash_dict = {}
            for name in os.listdir(store_path):
                hash_value = str(file_md5(os.path.join(store_path, name)))
                if hash_dict.has_key(hash_value):
                    hash_dict[hash_value] += 1
                    if hash_dict[hash_value] > 2:
                        check_path(os.path.join(TRUST_FOLDER, store_path.split('/')[2]))
                        shutil.move(os.path.join(store_path, name),
                                    os.path.join(TRUST_FOLDER,
                                                 store_path.split('/')[2] + '/' + store_path.split('/')[3]))
                        upload_task_info_db.update_one(
                                {'task_id': store_path.split('/')[2], 'upload_offset': int(store_path.split('/')[3])},
                                {'$set': {'upload_done': True}})
                        os.system("rm -f %s/*" % store_path)
                        break
                # MOVE FILE
                else:
                    hash_dict[hash_value] = 1

        # manage the cache
        return 'Upload OK!'


def check_id(task_id):
    if base_info_db.query_one({'_id': ObjectId(str(task_id))}):
        return True
    return False


def check_session(key):
    if len(key) != 24 or key.isdigit() is not True:
        print 'Key Error'
        return None
    r = session_info_db.query_one({'_id': ObjectId(str(key))})
    if r:
        return str(r['key_index'])
    return None


def check_cookie(cookie):
    if len(cookie) != 24 or cookie.isdigit() is not True:
        print 'Key Error'
        return None
    r = cookie_info_db.coll.find_one_and_delete({'_id': ObjectId(cookie)})
    if r:
        return r['upload_path']
    return None


def get_upload_info(task_id):
    if task_id.isdigit() is not True:
        return None
    base_info = base_info_db.query_one({'_id': ObjectId(str(task_id))})
    if base_info and base_info['has_task']:
        upload_task = upload_task_info_db.query_one({'task_id': task_id, 'upload_done': False})
        if upload_task is not None:
            upload_path = TMP_UPLOAD_FOLDER + '/' + str(task_id) + '/' + str(upload_task['upload_offset'])
            return upload_task['upload_offset'], upload_path
        else:
            merge_boot(task_id)
            if check_boot(task_id):
                del_task(task_id)
            else:
                print 'fatal error! incomplete boot.img!'
            return None, None
    return None, None


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=8080)
