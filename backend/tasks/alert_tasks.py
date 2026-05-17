import os
from datetime import datetime, timedelta
from tasks.celery_app import celery_app
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import AlertConfig, Class, User, Session as ClassSession
import redis as redis_lib
from tasks.email_tasks import send_alert_email


@celery_app.task(name="tasks.alert_tasks.check_thresholds")
def check_thresholds():
    pass


def _write_alert_history(
    session_id: int,
    alert_type: str,
    threshold: float,
    value: float,
    recipients: list,
):
    """
    Insert alert record into MongoDB alert_history collection.
    Called after every successfully queued email alert.
    """

    async def _insert():
        client = AsyncIOMotorClient(os.environ["MONGO_URI"])
        db     = client[os.environ["MONGO_DB"]]
        await db["alert_history"].insert_one({
            "session_id":   session_id,
            "type":         alert_type,
            "triggered_at": datetime.utcnow(),
            "threshold":    threshold,
            "value":        round(value, 4),
            "recipients":   recipients,
        })
        client.close()
        print(f"[alert_history] Written — session {session_id} type={alert_type}")

    asyncio.run(_insert())


@celery_app.task(name="tasks.alert_tasks.check_absence_alert")
def check_absence_alert(
    session_id: int,
    present_ids: list,
    absent_ids: list,
):
    total = len(present_ids) + len(absent_ids)
    if total == 0:
        return

    absent_ratio = len(absent_ids) / total
    print(f"[absence_alert] Session {session_id}: "
          f"{len(absent_ids)}/{total} absent ({absent_ratio:.2%})")

    engine   = create_engine(os.environ["DATABASE_URL"])
    Session  = sessionmaker(bind=engine)
    db       = Session()

    try:
        session = db.query(ClassSession).filter(
            ClassSession.id == session_id
        ).first()
        if not session:
            return

        config = db.query(AlertConfig).filter(
            AlertConfig.class_id == session.class_id
        ).first()
        if not config:
            print(f"[absence_alert] No alert config for class {session.class_id}")
            return

        if absent_ratio <= config.absence_threshold:
            print(f"[absence_alert] Below threshold — no alert")
            return

        r         = redis_lib.Redis.from_url(os.environ["REDIS_URL"])
        dedup_key = f"alert:{session_id}:absence"
        if r.exists(dedup_key):
            print(f"[absence_alert] Dedup active — skipping")
            return

        r.setex(dedup_key, 600, "1")

        cls        = db.query(Class).filter(Class.id == session.class_id).first()
        teacher    = db.query(User).filter(User.id == cls.teacher_id).first()
        recipients = config.recipient_emails or [teacher.email]

        body = (
            f"Absence Alert — Session {session_id}\n\n"
            f"Absent students ({len(absent_ids)}/{total}): "
            f"{', '.join(absent_ids)}\n"
            f"Absence rate: {absent_ratio:.1%} "
            f"(threshold: {config.absence_threshold:.1%})\n\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        )

        for email in recipients:
            send_alert_email.delay(
                email,
                f"⚠️ Absence Alert — Session {session_id}",
                body,
            )
            print(f"[absence_alert] Alert queued for {email}")

        # write to MongoDB alert_history
        _write_alert_history(
            session_id=session_id,
            alert_type="absence",
            threshold=config.absence_threshold,
            value=absent_ratio,
            recipients=recipients,
        )

    finally:
        db.close()


@celery_app.task(name="tasks.alert_tasks.check_attention_alert")
def check_attention_alert(session_id: int):

    async def _get_scores():
        client   = AsyncIOMotorClient(os.environ["MONGO_URI"])
        db_mongo = client[os.environ["MONGO_DB"]]
        now      = datetime.utcnow()
        cutoff   = now - timedelta(seconds=15)

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
                    "_id": {
                        "$subtract": [
                            {"$toLong": "$ts"},
                            {"$mod": [{"$toLong": "$ts"}, 5000]}
                        ]
                    },
                    "avg_score": {"$avg": "$score"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        buckets = await db_mongo["attention_logs"].aggregate(
            pipeline
        ).to_list(length=10)
        client.close()
        return buckets

    buckets = asyncio.run(_get_scores())

    if len(buckets) < 3:
        print(f"[attention_alert] Not enough ticks ({len(buckets)}/3) — skipping")
        return

    scores = [b["avg_score"] for b in buckets[-3:]]
    print(f"[attention_alert] Last 3 tick scores: {[round(s,3) for s in scores]}")

    engine  = create_engine(os.environ["DATABASE_URL"])
    Session = sessionmaker(bind=engine)
    db      = Session()

    try:
        session = db.query(ClassSession).filter(
            ClassSession.id == session_id
        ).first()
        if not session:
            return

        config = db.query(AlertConfig).filter(
            AlertConfig.class_id == session.class_id
        ).first()
        if not config:
            return

        all_below = all(s < config.attention_threshold for s in scores)
        if not all_below:
            print(f"[attention_alert] Not all ticks below threshold — no alert")
            return

        r         = redis_lib.Redis.from_url(os.environ["REDIS_URL"])
        dedup_key = f"alert:{session_id}:attention"
        if r.exists(dedup_key):
            print(f"[attention_alert] Dedup active — skipping")
            return

        r.setex(dedup_key, 600, "1")

        cls        = db.query(Class).filter(Class.id == session.class_id).first()
        teacher    = db.query(User).filter(User.id == cls.teacher_id).first()
        recipients = config.recipient_emails or [teacher.email]
        class_avg  = round(sum(scores) / len(scores), 3)

        body = (
            f"Attention Alert — Session {session_id}\n\n"
            f"Class attention has been low for 3 consecutive ticks.\n"
            f"Average score: {class_avg} "
            f"(threshold: {config.attention_threshold})\n"
            f"Last 3 scores: {[round(s,3) for s in scores]}\n\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        )

        for email in recipients:
            send_alert_email.delay(
                email,
                f"⚠️ Attention Alert — Session {session_id}",
                body,
            )
            print(f"[attention_alert] Alert queued for {email}")

        # write to MongoDB alert_history
        _write_alert_history(
            session_id=session_id,
            alert_type="attention",
            threshold=config.attention_threshold,
            value=class_avg,
            recipients=recipients,
        )

    finally:
        db.close()