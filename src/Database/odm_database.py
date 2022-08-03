from typing import List
from odmantic import Model
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from src.settings import settings

class Post(Model):
  keywords: str
  images: List[str]

  class Config:
    collection = 'Test Collection'


client = AsyncIOMotorClient(settings.mongo_uri)
engine = AIOEngine(motor_client=client, database=settings.mongo_db)

async def main():
  posts = await engine.find(
    Post,
    Post.keywords.match(r'.*кот.*'),
  )
  posts = {
    post.id: post.keywords for post in posts
  }

import asyncio
asyncio.run(main())