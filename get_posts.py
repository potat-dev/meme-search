import asyncio
from vkbottle.api import API
from math import ceil
from loguru import logger
from tqdm import tqdm

# settings
max_items = 100
pub_name = 'poiskmemow'
logger.disable("vkbottle")

with open('token.txt', 'r') as token:
    tokens = token.read().splitlines()

api = API(tokens)

async def get_posts() -> None:
    posts = await api.wall.get(count=1, domain=pub_name)
    count = posts.count
    api_calls_count = ceil(count / max_items)
    print(count, api_calls_count)

    requests = [
        api.APIRequest(
            "wall.get", {'domain': pub_name, 'count': max_items, 'offset': i * max_items})
        for i in range(ceil(count / max_items))
    ]

    posts_data = []
    pbar = tqdm(total=api_calls_count)
    async for response in api.request_many(requests):
        posts_data += response['response']['items']
        pbar.update(1)
    pbar.close()
    print(len(posts_data), len(posts_data[0]))

loop = asyncio.get_event_loop()
loop.run_until_complete(get_posts())
