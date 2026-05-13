from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.mongo import connect_mongo, disconnect_mongo
from routers.auth import router as auth_router
from routers.attendance import router as attendance_router
from routers import attention


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongo()
    yield
    await disconnect_mongo()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,        prefix="/api")
app.include_router(attendance_router,  prefix="/api")
app.include_router(attention.router)


@app.get("/api/health/")
async def health():
    return {"status": "ok"}