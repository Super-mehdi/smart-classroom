# backend/seed.py
from db.session import SessionLocal
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

test_user = User(
    email="test@smartclass.com",
    hashed_password=pwd_context.hash("password123"),
    full_name="Test Teacher",
    role="teacher"
)

db.add(test_user)
db.commit()
db.refresh(test_user)

print(f"✅ User created: {test_user.email} (id={test_user.id})")
db.close()