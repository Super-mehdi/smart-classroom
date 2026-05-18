import os
import sys
import bcrypt
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Class, AlertConfig, UserRole

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Check if worker exists
worker_email = os.environ.get("WORKER_EMAIL", "worker@smartclass.com")
worker_pass = os.environ.get("WORKER_PASSWORD", "worker123")

existing_worker = db.query(User).filter(User.email == worker_email).first()
if not existing_worker:
    print(f"Creating worker user: {worker_email}")
    worker = User(
        email=worker_email,
        hashed_password=hash_password(worker_pass),
        full_name="CV Worker",
        role=UserRole.superuser, # Give it enough permissions to see all sessions
    )
    db.add(worker)
    db.commit()
else:
    print(f"Worker user {worker_email} already exists.")

db.close()
