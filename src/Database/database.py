from pymongo import MongoClient
from halo import Halo


class Database:
    """
    Local cache of keywords and images
    for faster access and quick fuzzy search
    And also wrapper for mongoDB find() method
    """
    keywords = {}
    images = {}

    def __init__(self, settings):
        self.client = MongoClient(settings.mongo_uri)
        self.db = self.client[settings.mongo_db]
        self.collection = self.db[settings.mongo_collection]

    @property
    def posts_count(self):
        return len(self.keywords.items())

    def get_cached_ids(self):
        return set(self.keywords.keys())

    def get_server_ids(self):
        data = self.collection.find(projection=['_id'])
        return set(i['_id'] for i in data)

    def add_posts(self, posts):
        for post in posts:
            self.keywords[post['_id']] = post['keywords']
            self.images[post['_id']] = post['images']

    def remove_posts(self, ids):
        for id in ids:
            self.keywords.pop(id, None)
            self.images.pop(id, None)

    def get_posts(self, ids: list = []):
        query = {'_id': {'$in': ids}} if ids else {}
        return self.collection.find(query)

    def update(self):
        with Halo(text='Updating Database', spinner='bounce') as spinner:
            cached_ids = self.get_cached_ids()
            if cached_ids:
                try:
                    server_ids = self.get_server_ids()
                except Exception as e:
                    spinner.fail("Something went wrong!")
                    print("Exception:", e)
                    return None

                new_ids = server_ids - cached_ids
                if len(new_ids) > 0:
                    new_posts = self.get_posts(list(new_ids))
                    self.add_posts(new_posts)

                removed_ids = cached_ids - server_ids
                self.remove_posts(removed_ids)

                if len(new_ids) or len(removed_ids):
                    spinner.succeed(
                        f"Database Updated! ({len(new_ids)} added {len(removed_ids)} removed)")
                else:
                    spinner.warn("Database is up to date!")
            else:
                new_posts = self.get_posts()
                self.add_posts(new_posts)
                if self.posts_count:
                    spinner.succeed(f"Database Updated! ({self.posts_count} added)")
