import sys
import os
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

import bcrypt
from db.session import SessionLocal
from models import User, UserRole

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

db = SessionLocal()

test_user = User(
    email="test@smartclass.com",
    hashed_password=hash_password("password123"),
    full_name="Test Teacher",
    role=UserRole.teacher
)

db.add(test_user)
db.commit()
db.refresh(test_user)

print(f"User created: {test_user.email} (id={test_user.id})")

db.close()