from pymongo import MongoClient
from dataclasses import dataclass
from halo import Halo


class Database:
    """
    Wrapper for mongoDB find() method
    """
    def __init__(self, settings):
        self.client = MongoClient(settings.mongo_uri)
        self.db = self.client[settings.mongo_db]
        self.collection = self.db[settings.mongo_collection]

    def get_ids(self):
        data = self.collection.find(projection=['_id'])
        return set(i['_id'] for i in data)

    def get_posts(self, ids: list):
        return self.collection.find({'_id': {'$in': ids}})


@dataclass
class Cache:
    """
    Local cache of keywords and images
    for faster access and quick fuzzy search
    """
    db: Database
    keywords = {}
    images = {}

    @property
    def ids(self):
        return set(i for i, _ in self.keywords.items())

    @property
    def posts_count(self):
        return len(self.keywords)

    def add_posts(self, posts):
        self.keywords.update({p['_id']: p['keywords'] for p in posts})
        self.images.update({p['_id']: p['images'] for p in posts})

    def remove_posts(self, ids):
        for id in ids:
            self.keywords.pop(id, None)
            self.images.pop(id, None)

    def update(self):
        with Halo(text='Updating cache', spinner='bounce') as spinner:
            cached_ids = self.ids
            try:
                server_ids = self.db.get_ids()
            except Exception as e:
                spinner.fail("Something went wrong!")
                print("Exception:", e)
                return None

            new_ids = server_ids - cached_ids
            if len(new_ids) > 0:
                new_posts = self.db.get_posts(list(new_ids))
                self.add_posts(new_posts)

            removed_ids = cached_ids - server_ids
            self.remove_posts(removed_ids)

            if len(new_ids) > 0 or len(removed_ids) > 0:
                spinner.succeed(f"Cache Updated! ({len(new_ids)} added {len(removed_ids)} removed)")
            else:
                spinner.warn("Cache is up to date!")
