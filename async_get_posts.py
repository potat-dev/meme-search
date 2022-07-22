from mpire import WorkerPool
from vk_api import VkApi
from math import ceil
import re

with open('token.txt', 'r') as tokens:
    token = tokens.readline()
    vk = VkApi(token=token)

pub_name = 'poiskmemow'
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
    print("without images:", len(posts))

    with open('only_text.txt', 'w', encoding="utf-8") as f:
      for post in posts:
        f.write(f'{post.text}\n')





# api_endpoint = 'https://api.vk.com/method/wall.get'
# pub_name = 'poiskmemow'
# max_items = 100

# with open('token.txt', 'r') as tokens:
#     access_token = tokens.readline()

# posts_data = []


# async def get_page_data(session, page):
#     global posts_data
#     posts_url = f'{api_endpoint}?domain={pub_name}&count={max_items}&offset={page * max_items}&access_token={access_token}&v=5.131'
#     async with session.get(posts_url) as responce:
#         data = await responce.json()
#         posts_data += data['response']['items']
#     print(f'Получена страница {page}')


# async def gather_data():
#     posts_count_url = f'{api_endpoint}?domain={pub_name}&count={1}&access_token={access_token}&v=5.131'
#     async with aiohttp.ClientSession() as session:
#         responce = await session.get(posts_count_url)
#         data = await responce.json()
#         posts_count = data['response']['count']
#         api_calls_count = ceil(posts_count / max_items)
#         print(posts_count, api_calls_count)

#         tasks = []
#         for page in range(api_calls_count):
#             task = asyncio.create_task(get_page_data(session, page))
#             tasks.append(task)

#         await asyncio.gather(*tasks)


# def main():
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     start_time = time()
#     asyncio.run(gather_data())
#     finish_time = time() - start_time
#     print(f'Время выполнения: {finish_time}')
#     print(f'Количество постов: {len(posts_data)}')

# main()
