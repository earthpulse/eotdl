from fastapi import FastAPI
from eotds.hello import hello

app = FastAPI()


@app.get("/")
async def root():
    return hello()