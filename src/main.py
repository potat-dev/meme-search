from fastapi import FastAPI
from fuzzywuzzy import process, utils, fuzz
from Database import database
from settings import settings

db = database.Database(settings)


def update_database():
    print('Updating database...')  # TODO: change to logger
    keywords, images = db.get_keywords(), db.get_images()
    print('Database updated ✅')
    return keywords, images


keywords, images = update_database()
app = FastAPI()


@app.get("/search/{query}")
async def search(query: str, limit: int = 10, min_score: int = 70):
    results = process.extract(
        choices=keywords,
        query=query,
        limit=limit,
        scorer=fuzz.partial_ratio
    )
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
        "max_score": max(i["score"] for i in results),
        "results": results
    }


@app.get("/meme/{id}")
async def meme(id: int):
    return {
        "id": id,
        "keywords": keywords[id],
        "images": images[id]
    }


@app.get("/stats")
async def stats():
    return {
        "count": len(keywords),
    }


@app.post("/update")
async def update():
    global keywords, images
    keywords, images = update_database()
    return {
        "count": len(keywords),
    }
