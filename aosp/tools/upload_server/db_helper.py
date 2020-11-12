#!/usr/local/bin/python
from pymongo import MongoClient
from pymongo import errors
import helpers as helper
import gridfs
__author__ = 'devilk_r'


def main():
    return


class mongodb:
    def __init__(self, db, coll, uri='mongodb://localhost:27017', ):
        self.coll = ''
        self.__db = ''
        try:
            self.__client = MongoClient(uri)
            self.__setdb(db)
            self.__setcoll(coll)
        except errors.ConnectionFailure, e:
            helper.perror('Error when init!\n', e)
            self.__client = None
            exit(0)
            return

    def __setdb(self, db_name):
        try:
            if self.__client is not None:
                self.__db = self.__client[db_name]
        except Exception, e:
            helper.perror('Error when setting db!\n', e)
            self.__db = None
        return

    def __setcoll(self, coll_name):
        try:
            if self.__db is not None:
                self.coll = self.__db[coll_name]
        except Exception, e:
            helper.perror('Error when setting collection!\n', e)
            self.coll = None
        return

    def insert(self, dic):
        try:
            if self.coll is not None:
                return str(self.coll.insert_one(dic).inserted_id)
            else:
                helper.perror('not set coll!\n')
                return
        except Exception, e:
            helper.perror('Error when insert!\n', e)
            return

    def update_one(self, *dic):
        try:
            if self.coll is not None and len(dic) == 2:
                return str(self.coll.update_one(dic[0], dic[1]))
            else:
                helper.perror('not set coll!\n')
                return
        except Exception, e:
            helper.perror('Error when update!\n', e)
            return

    def update_many(self, *dic):
        try:
            if self.coll is not None and len(dic) == 2:
                return str(self.coll.update_many(dic[0], dic[1]))
            else:
                helper.perror('not set coll!\n')
                return
        except Exception, e:
            helper.perror('Error when update!\n', e)
            return

    def delete_one(self, *dic):
        try:
            if self.coll is not None and len(dic) == 1:
                return str(self.coll.delete_one(dic[0]))
            else:
                helper.perror('not set coll!\n')
                return
        except Exception, e:
            helper.perror('Error when update!\n', e)
            return

    def delete_many(self, *dic):
        try:
            if self.coll is not None and len(dic) == 1:
                return str(self.coll.delete_many(dic[0]))
            else:
                helper.perror('not set coll!\n')
                return
        except Exception, e:
            helper.perror('Error when update!\n', e)
            return

    def query(self, *dic):
        if self.coll is not None:
            if len(dic) == 1:
                cursor = self.coll.find(dic[0])
                return cursor
            # for i in cursor....
            if len(dic) == 2:
                cursor = self.coll.find(dic[0], dic[1])
                return cursor
            helper.perror('query args error!\n')
            return None
        else:
            helper.perror('not set coll!\n')
            return None

    def query_one(self, *dic):
        if self.coll is not None:
            if len(dic) == 1:
                item = self.coll.find_one(dic[0])
                return item
            # for i in cursor....
            if len(dic) == 2:
                item = self.coll.find_one(dic[0], dic[1])
                return item
            helper.perror('query args error!\n')
            return None
        else:
            helper.perror('not set coll!\n')
            return None

    def save_file(self, file_path, file_name):
        fs = gridfs.GridFS(self.__db)
        return fs.put(open(file_path, 'rb'), filename=file_name)

    def get_file(self, _id):
        fs = gridfs.GridFS(self.__db)
        return fs.get(_id)


if __name__ == '__main__':
    main()
