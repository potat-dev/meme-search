from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fuzzywuzzy import process, fuzz
from time import sleep
from settings import settings
from Database.database import Database, Cache


db = Database(settings)
cache = Cache(db)
cache.update()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search(q: str, limit: int = 10, min_score: int = 70, use_delay: bool = False):
    if use_delay:
        sleep(5)  # for testing purposes (react loading UI)
    results = process.extract(
        choices=cache.keywords,
        query=q,
        limit=limit,
        scorer=fuzz.partial_ratio
    )  # -> list of tuples (keywords, score, id)
    results = [
        {
            "text": result[0],
            "score": result[1],
            "id": str(result[2]),
            "images": cache.images[result[2]]
        }
        for result in results if result[1] >= min_score
    ]
    return {
        "count": len(results),
        "max_score": max(i["score"] for i in results),
        "results": results
    }


@app.get("/meme/{id}")
async def meme(id: int):
    return {
        "id": id,
        "keywords": cache.keywords[id],
        "images": cache.images[id]
    }


@app.get("/stats")
async def stats():
    return {
        "count": cache.posts_count,
    }


@app.post("/update")
async def update():
    cache.update()
    return {
        "count": cache.posts_count,
    }
