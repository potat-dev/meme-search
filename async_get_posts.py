from time import time
from math import ceil
import asyncio
import aiohttp

api_endpoint = 'https://api.vk.com/method/wall.get'
pub_name = 'poiskmemow'
max_items = 100

with open('token.txt', 'r') as tokens:
    access_token = tokens.readline()

posts_data = []


async def get_page_data(session, page):
    global posts_data
    posts_url = f'{api_endpoint}?domain={pub_name}&count={max_items}&offset={page * max_items}&access_token={access_token}&v=5.131'
    async with session.get(posts_url) as responce:
        data = await responce.json()
        posts_data += data['response']['items']
    print(f'Получена страница {page}')


async def gather_data():
    posts_count_url = f'{api_endpoint}?domain={pub_name}&count={1}&access_token={access_token}&v=5.131'
    async with aiohttp.ClientSession() as session:
        responce = await session.get(posts_count_url)
        data = await responce.json()
        posts_count = data['response']['count']
        api_calls_count = ceil(posts_count / max_items)
        print(posts_count, api_calls_count)

        tasks = []
        for page in range(api_calls_count):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    start_time = time()
    asyncio.run(gather_data())
    finish_time = time() - start_time
    print(f'Время выполнения: {finish_time}')
    print(f'Количество постов: {len(posts_data)}')

main()
