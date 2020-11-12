import client_generator
import db_helper as db
import random
import string
from bson.objectid import ObjectId
import datetime
import client_generator
from binascii import b2a_hex, a2b_hex

__author__ = "Arno"


def id_generator(length):
    return ''.join(random.SystemRandom().choice(string.digits) for _ in range(length))


# after new rom find
def new_task(model=None, release=None, version=None, machine=None):
    base_db = db.mongodb('upload_server', 'base_info')
    token = id_generator(24)
    task_id = id_generator(24)
    if base_db.insert({'_id': ObjectId(str(task_id)), 'model': model, 'version': version, 'release': release,
                       'machine': machine, 'token': token, 'has_task': False,
                       'begin_date': datetime.datetime.now()}):
        client_generator.config_new_client(model=model, release=release, version=version, machine=machine, token=token,
                                           task_id=task_id)
    return


if __name__ == '__main__':
    new_task(model="AOSP on HammerHead", release="3.4.0-g7717f76",
             version="#1 SMP PREEMPT Wed Nov 4 21:42:24 UTC 2015",
             machine="armv7l")
    print "update and deploy done!"
