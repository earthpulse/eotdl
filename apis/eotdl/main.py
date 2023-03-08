from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import hello

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(hello.router)


@app.get("/")
async def root():
    return {
        'name': 'eotdl',
        'version': '0.0.1',
        'description': 'Earth Observation Training Data Lab',
        'contact': 'it@earthpulse.es'
    }