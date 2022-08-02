from fastapi import FastAPI
from fuzzywuzzy import process, utils, fuzz
import pandas as pd

data = pd.read_pickle(r'D:\Projects\meme-search\posts_data.pickle')

images = {i['id']: i['photos'] for i in data}
keywords = {i['id']: i['text'] for i in data}

app = FastAPI()

@app.get("/search/{query}")
async def search(query: str, limit: int = 10, min_score: int = 70):
  results = process.extract(query, keywords, limit=limit, scorer=fuzz.partial_ratio)
  max_score = max(r[2] for r in results)
  results = [
    {
      "text": result[0],
      "score": result[1],
      "id": result[2],
      "images": images[result[2]]
    }
    for result in results if result[1] >= min_score
  ]
  return {
    "count": len(results),
    "max_score": max_score,
    "results": results
  }

@app.get("/meme/{id}")
async def meme(id: int):
  return {
    "id": id,
    "keywords": keywords[id],
    "images": images[id]
  }