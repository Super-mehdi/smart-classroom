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


# Clear existing seed data
print("Clearing existing data...")
db.query(AlertConfig).delete()
db.query(Class).delete()
db.query(User).delete()
db.commit()

# users
print("Creating users...")

teacher1 = User(
    email="teacher1@smartclass.com",
    hashed_password=hash_password("teacher123"),
    full_name="Zakaria El Hiouile",
    role=UserRole.teacher,
)
teacher2 = User(
    email="teacher2@smartclass.com",
    hashed_password=hash_password("teacher456"),
    full_name="EL MEHDI AMGHARY",
    role=UserRole.teacher,
)
superuser = User(
    email="admin@smartclass.com",
    hashed_password=hash_password("admin123"),
    full_name="Ana Admin",
    role=UserRole.superuser,
)

db.add_all([teacher1, teacher2, superuser])
db.commit()
db.refresh(teacher1)
db.refresh(teacher2)
db.refresh(superuser)

# classes
print("Creating classes...")

class1 = Class(name="Mathematics 101", teacher_id=teacher1.id)
class2 = Class(name="Physics 201",     teacher_id=teacher1.id)
class3 = Class(name="Computer Science 301", teacher_id=teacher2.id)

db.add_all([class1, class2, class3])
db.commit()
db.refresh(class1)
db.refresh(class2)
db.refresh(class3)

# Alert configs
print("Creating alert configs...")

for cls in [class1, class2, class3]:
    db.refresh(cls)
    config = AlertConfig(
        class_id=cls.id,
        absence_threshold=0.3,
        attention_threshold=0.4,
        recipient_emails=[cls.teacher.email],
    )
    db.add(config)

db.commit()

print("Done! Seeded:")
print("  - 3 users (2 teachers, 1 superuser)")
print("  - 3 classes")
print("  - 3 alert configs")

db.close()