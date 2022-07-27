from mpire import WorkerPool
from vk_api import VkApi
from math import ceil
import pickle
import json
import re

with open('token.txt', 'r') as tokens:
    token = tokens.readline()
    vk = VkApi(token=token)

pub_name = 'poiskmemow'
# pub_name = 'kartinochkistekstom'
max_items = 100

def format_text(text):
  url_re = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
  src_url = f'([Ии]сточник.*?)?( {url_re})+'
  tags_re = r'#.+?@\S+'
  # clear text
  text = text.replace('\n', ' ').replace('\r', ' ') # remove newlines
  text = re.sub(src_url, '', text) # remove source links
  text = re.sub(url_re, '', text) # remove urls
  text = re.sub(tags_re, '', text) # remove hashtags
  text = text.replace('#', '') # convert hashtags to words
  text = ' '.join(text.split()).strip() # remove double spaces
  return text

def get_posts(offset):
    request_data = {
        'domain': pub_name,
        'count': max_items,
        'offset': offset * max_items
    }
    return vk.method("wall.get", request_data)['items']

class Post:
  def __init__(self, json):
    self.json, self.id = json, json['id']
    self.text, self.photos = self._parse_post(json)

  def _parse_post(self, json):
    text = format_text(json['text'])
    photos = []
    if 'attachments' in json.keys():
      for attachment in json['attachments']:
        if attachment['type'] == 'photo':
          max_src = max(attachment['photo']['sizes'], key=lambda x: x['width'] * x['height'])['url']
          photos.append(max_src)
    return text, photos
  
  def __str__(self):
    return f'Post(id={self.id}, text={self.text}, photos={self.photos})'

  # to dict
  def to_dict(self):
    return {
      'id': self.id,
      'text': self.text,
      'photos': self.photos
    }


if __name__ == '__main__':
    count = vk.method("wall.get", {'domain': pub_name, 'count': 1})['count']
    api_calls_count = ceil(count / max_items)

    with WorkerPool() as pool:
        results = pool.map(
            get_posts, range(api_calls_count), progress_bar=True)

    posts_data = [item for sublist in results for item in sublist]
    print(len(posts_data))

    posts = [Post(post) for post in posts_data]
    print("all posts:", len(posts))

    posts = [post for post in posts if post.photos and post.text]
    print("with images:", len(posts))

    with open('only_text.txt', 'w', encoding="utf-8") as f:
      for post in posts:
        f.write(f'{post.text}\n')

    with open('posts_data.pickle', 'wb') as f:
      pickle.dump([post.to_dict() for post in posts], f)

    with open('posts_data.json', 'w', encoding="utf-8") as f:
      f.write(json.dumps([{"keywords": post.text, "images": post.photos} for post in posts], ensure_ascii=False))