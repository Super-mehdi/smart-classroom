import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

client: AsyncIOMotorClient = None


def get_mongo_client() -> AsyncIOMotorClient:
    return client


def get_mongo_db():
    return client[os.environ["MONGO_DB"]]


async def connect_mongo():
    global client
    client = AsyncIOMotorClient(os.environ["MONGO_URI"])
    db = get_mongo_db()
    await init_collections(db)
    print("Connected to MongoDB")


async def disconnect_mongo():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


async def init_collections(db: AsyncIOMotorDatabase):
    existing = await db.list_collection_names()

    # attention_logs
    if "attention_logs" not in existing:
        await db.create_collection("attention_logs")
    await db["attention_logs"].create_index(
        [("session_id", 1), ("ts", 1)]
    )

    # cv_debug_logs
    if "cv_debug_logs" not in existing:
        await db.create_collection("cv_debug_logs")
    await db["cv_debug_logs"].create_index(
        [("session_id", 1), ("frame_id", 1)]
    )

    # alert_history
    if "alert_history" not in existing:
        await db.create_collection("alert_history")
    await db["alert_history"].create_index(
        [("session_id", 1)]
    )

    # face_embeddings
    if "face_embeddings" not in existing:
        await db.create_collection("face_embeddings")
    await db["face_embeddings"].create_index(
        [("student_id", 1)],
        unique=True   
    )

    print("MongoDB collections and indexes ready")