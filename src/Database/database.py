from pymongo import MongoClient

class Database:
  def __init__(self, settings):
    self.client = MongoClient(settings.mongo_uri)
    self.db = self.client[settings.mongo_db]
    self.collection = self.db[settings.mongo_collection]

  def get_keywords(self):
    data = self.collection.find(projection=['keywords'])
    keywords = {i['_id']: i['keywords'] for i in data}
    return keywords

  def get_images(self):
    data = self.collection.find(projection=['images'])
    images = {i['_id']: i['images'] for i in data}
    return images