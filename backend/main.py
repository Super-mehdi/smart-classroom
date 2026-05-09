from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers import example, attention

from contextlib import asynccontextmanager
from db.mongo import connect_mongo, disconnect_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongo()
    yield
    await disconnect_mongo()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(example.router)
app.include_router(auth_router, prefix="/api")
app.include_router(attention.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/health/")
async def health():
    return {"status": "ok"}