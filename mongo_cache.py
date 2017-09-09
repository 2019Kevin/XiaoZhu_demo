from datetime import datetime, timedelta
from pymongo import MongoClient


class MongoCache:
    def __init__(self, client=None, expires=timedelta(days=30)):
        self.client = MongoClient('localhost', 27017) if client is None else client
        self.db = self.client.xiaozhu        #创建数据库
        self.db.webpage.create_index('timestamp', expireAfterSeconds=expires.total_seconds())

    def __contains__(self, url):
        try:
            self[url]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, url):
        """载入这个url地址对应的结果
        """
        record = self.db.webpage.find_one({'_id': url})
        if record:
            return record['result']
        else:
            raise KeyError(url + ' does not exist')


    def __setitem__(self, url, result):
        """保存这个url所对应的结果
        """
        record = {'result': result, 'timestamp': datetime.utcnow()}
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)


    def clear(self):
        self.db.webpage.drop()


















