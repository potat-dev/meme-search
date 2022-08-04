from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fuzzywuzzy import process, utils, fuzz
from Database import database
from settings import settings
from time import sleep
from halo import Halo

db = database.Database(settings)


def update_database():
    with Halo(text='Updating Database', spinner='bounce') as spinner:
        try:
            keywords, images = (db.get_keywords(), db.get_images())
            spinner.succeed("Database Updated!")
            return (keywords, images)
        except Exception as e:
            spinner.fail("Something went wrong!")
            print(e)
            return (None, None)


keywords, images = update_database()

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
        choices=keywords,
        query=q,
        limit=limit,
        scorer=fuzz.partial_ratio
    )  # -> list of tuples (keywords, score, id)
    results = [
        {
            "text": result[0],
            "score": result[1],
            "id": str(result[2]),
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
