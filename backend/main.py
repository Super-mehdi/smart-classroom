from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.mongo import connect_mongo, disconnect_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongo()   
    yield
    await disconnect_mongo()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}