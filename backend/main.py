
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.mongo import connect_mongo, disconnect_mongo
from routers.auth import router as auth_router
from routers.attendance import router as attendance_router
from routers import attention
from routers.ws import router as ws_router, broadcaster
import asyncio
from routers.debug import router as debug_router
from routers.alert_config import router as alert_config_router
from routers.alert_history import router as alert_history_router
from routers.analytics import router as analytics_router
from routers.sessions import router as sessions_router
from routers.classes import router as classes_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongo()
    # start broadcaster as background task
    task = asyncio.create_task(broadcaster())
    yield
    # cancel broadcaster on shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await disconnect_mongo()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,       prefix="/api")
app.include_router(attendance_router)
app.include_router(attention.router)
app.include_router(ws_router)
app.include_router(debug_router)
app.include_router(alert_config_router, prefix="/api")
app.include_router(alert_history_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(classes_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")

@app.get("/api/health/")
async def health():
    return {"status": "ok"}