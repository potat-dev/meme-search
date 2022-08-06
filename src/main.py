from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fuzzywuzzy import process, fuzz
from time import time, sleep
from settings import settings
from Database.database import Database


db = Database(settings)
db.update()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search(q: str, limit: int = 10, min_score: int = 70, delay: int = 0):
    if delay:
        sleep(delay)  # for testing purposes (react loading UI)

    # measure time
    start = time()
    results = process.extract(
        choices=db.keywords,
        query=q,
        limit=limit,
        scorer=fuzz.partial_ratio
    )  # -> list of tuples (keywords, score, id)
    end = time()

    return {
        "count": len(results),
        "time": {"float": end - start, "str": str(round(end - start, 2))},
        "max_score": max(i["score"] for i in results),
        "results": [
            {
                "text": result[0],
                "score": result[1],
                "id": str(result[2]),
                "images": db.images[result[2]]
            }
            for result in results if result[1] >= min_score
        ]
    }


@app.get("/meme/{id}")
async def meme(id: int):
    return {
        "id": id,
        "keywords": db.keywords[id],
        "images": db.images[id]
    }


@app.get("/stats")
async def stats():
    return {
        "count": db.posts_count,
    }


@app.post("/update")
async def update():
    # measure time
    start = time()
    db.update()
    end = time()
    return {
        "count": db.posts_count,
        "time": {"float": end - start, "str": str(round(end - start, 2))},
    }
