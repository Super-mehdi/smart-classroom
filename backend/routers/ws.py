import asyncio
from datetime import datetime, timedelta
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from db.mongo import get_mongo_db

router = APIRouter(tags=["websocket"])

subscribers: dict[int, list[WebSocket]] = {}


async def add_subscriber(session_id: int, ws: WebSocket):
    if session_id not in subscribers:
        subscribers[session_id] = []
    subscribers[session_id].append(ws)


async def remove_subscriber(session_id: int, ws: WebSocket):
    if session_id in subscribers:
        try:
            subscribers[session_id].remove(ws)
        except ValueError:
            pass

        if not subscribers[session_id]:
            del subscribers[session_id]
            print(f"No more subscribers for session {session_id} — cleaned up")


async def broadcast(session_id: int, data: dict):
    if session_id not in subscribers:
        return

    dead = []
    for ws in subscribers[session_id]:
        try:
            await ws.send_json(data)
        except Exception as e:
            print(f"Broadcast error: {e}")
            dead.append(ws)

    for ws in dead:
        await remove_subscriber(session_id, ws)


async def fetch_latest_attention(session_id: int) -> dict:
    db     = get_mongo_db()
    cutoff = datetime.utcnow() - timedelta(seconds=10)

    pipeline = [
        {
            "$match": {
                "session_id": session_id,
                "ts": {"$gte": cutoff},
            }
        },
        {"$sort": {"ts": 1}},
        {
            "$group": {
                "_id":   "$student_id",
                "score": {"$last": "$score"},
                "yaw":   {"$last": "$yaw"},
                "pitch": {"$last": "$pitch"},
                "ear":   {"$last": "$ear"},
                "ts":    {"$last": "$ts"},
            }
        },
        {
            "$project": {
                "_id":        0,
                "student_id": "$_id",
                "score":      1,
                "yaw":        1,
                "pitch":      1,
                "ear":        1,
                "ts":         1,
            }
        },
        {"$sort": {"student_id": 1}},
    ]

    results = await db["attention_logs"].aggregate(pipeline).to_list(length=100)

    for r in results:
        if isinstance(r.get("ts"), datetime):
            r["ts"] = r["ts"].isoformat()

    scores    = [r["score"] for r in results]
    class_avg = round(sum(scores) / len(scores), 4) if scores else None

    return {
        "session_id": session_id,
        "students":   results,
        "class_avg":  class_avg,
        "ts":         datetime.utcnow().isoformat(),
    }


async def broadcaster():
    print("Broadcaster started")
    while True:
        await asyncio.sleep(2)

        if not subscribers:
            continue

        for session_id in list(subscribers.keys()):
            try:
                data = await fetch_latest_attention(session_id)
                await broadcast(session_id, data)
            except Exception as e:
                print(f"Broadcaster error for session {session_id}: {e}")


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()
    await add_subscriber(session_id, websocket)

    print(f"WebSocket connected — session {session_id} "
          f"({len(subscribers[session_id])} subscriber(s))")

    try:
        while True:
            await asyncio.wait_for(
                websocket.receive_text(),
                timeout=30.0
            )

    except asyncio.TimeoutError:
        # client stopped responding — try ping
        try:
            await websocket.send_json({"type": "ping"})
        except Exception:
            await remove_subscriber(session_id, websocket)
            print(f"WebSocket timed out — session {session_id}")

    except WebSocketDisconnect:
        await remove_subscriber(session_id, websocket)
        remaining = len(subscribers.get(session_id, []))
        print(f"WebSocket disconnected — session {session_id} "
              f"({remaining} subscriber(s) remaining)")