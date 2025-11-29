from fastapi import HTTPException
from sqlmodel import Session, select
import bcrypt
import re
from app.models.user import User


def authenticate_user(email: str, password: str, session: Session) -> User:
    """
    Authenticate a user by email and password
    :param email: User email
    :param password: User password
    :param session: Database session
    :return: Authenticated User
    """
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise ValueError("Incorrect password")
    
    return user


def hash_user_password(password: str) -> str:
    """
    Hash the user's password
    :param password: Password to hash
    :return: Hashed password
    """
    validate_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def validate_password(password: str) -> str:
    """
    Validate password strength
    :param password: Password to validate
    :return: Validated password
    """
    # todo: decide on splitting rules
    if len(password) < 3:
        raise ValueError('Password must be at least 3 characters long')
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one digit')
    if not re.search(r'[a-z]', password):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'[A-Z]', password):
        raise ValueError('Password must contain at least one uppercase letter')
    return password
