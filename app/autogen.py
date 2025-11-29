from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.models.consts import ZONE
from app.models.user import User
from app.database import engine
from app.auth.utils import hash_user_password

USERS = [
    {"email": "yarden@example.com", "name": "Yarden", "password": "Securepassword1", "registrationTimestamp": "2023-01-01T12:01:09Z", "roles": ["admin", "user"]},
    {"email": "another@example.com", "name": "Another", "password": "Anotherpassword1", "registrationTimestamp": "2024-05-02T13:02:05Z", "roles": ["user"]},
    {"email": "jerbi@example.com", "name": "Jerbi", "password": "Jerbipassword1", "registrationTimestamp": "2025-08-09T14:07:05Z", "roles": ["user"]},
    {"email": "late@gmail.com", "name": "Late by an hour", "password": "Late1", "registrationTimestamp": datetime.now(tz=ZONE) - timedelta(hours=25), "roles": ["user"]}
]


def init_data():
    """Initialize the database with predefined users"""
    with Session(engine) as session:
        for user_data in USERS:
            user = session.exec(select(User).where(User.email == user_data["email"])).first()
            if not user:
                user = User(**user_data)
                user.password = hash_user_password(user.password)
                session.add(user)
        session.commit()
