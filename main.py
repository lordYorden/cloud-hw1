from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func
from models import ZONE, Criteria, User
from datetime import datetime
import bcrypt
import re
from db import get_session, engine
from sqlmodel import Session, delete, select
from sqlalchemy.orm import defer
from fastapi_pagination import add_pagination, Params
from fastapi_pagination.ext.sqlmodel import paginate

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
    #todo: decied on spliting rules
    if len(password) < 3:
        raise ValueError('Password must be at least 3 characters long')
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one digit')
    if not re.search(r'[a-z]', password):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'[A-Z]', password):
        raise ValueError('Password must contain at least one uppercase letter')
    return password

USERS = [
    {"email": "yarden@example.com", "name": "Yarden", "password": "Securepassword1", "registrationTimestamp": "2023-01-01T12:01:09Z", "roles": ["admin", "user"]},
    {"email": "another@example.com", "name": "Another", "password": "Anotherpassword1", "registrationTimestamp": "2024-05-02T13:02:05Z", "roles": ["user"]},
    {"email": "jerbi@example.com", "name": "Jerbi", "password": "Jerbipassword1", "registrationTimestamp": "2025-08-09T14:07:05Z", "roles": ["user"]}
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

app = FastAPI()
add_pagination(app)
         
@app.get("/")
async def ping_and_init():
    """Ping endpoint to check if the server is running and initialize data"""
    init_data()
    return {"Hello": "World"}

@app.exception_handler(ValueError)
async def value_exception_handler(request: Request, exc: ValueError):
    """
    Handles ValueError exceptions
    :param request: Request
    :param exc: ValueError
    """
    return JSONResponse(status_code=401, content={"detail": str(exc)})

#handles all other exceptions like springboot
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles all uncaught exceptions
    :param request: Request
    :param exc: Exception
    """
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.post("/users", response_model_exclude={"password"})
async def upload_notification(to_upload: User, session: Session = Depends(get_session)) -> User:
    """
    Upload a new user
    :param to_upload: User to upload
    :param session: Database session
    :return: Uploaded User
    """
    to_upload.password = hash_user_password(to_upload.password)
    user = User(**to_upload.model_dump())
    
    if not user.roles:
        raise ValueError("User must have at least one role")
    
    session.add(user)

    session.commit()
    session.refresh(user)
    return user

@app.get("/users/{email}", response_model_exclude={"password"})
async def get_specific_user(email: str, password: str,
                            session: Session = Depends(get_session)) -> User:
    """
    Get a specific user by email
    :param email: User email
    :param password: User password
    :param session: Database session
    :return: User
    """
    user = authenticate_user(email, password, session)

    return user

@app.put("/users/{email}", status_code=204)
async def update_user(email: str, to_update: User, password: str,
                      session: Session = Depends(get_session)):
    """
    Update a specific user by email
    :param email: User email
    :param to_update: User data to update
    :param password: User password
    :param session: Database session
    """
    user = authenticate_user(email, password, session)

    for key, value in to_update.model_dump().items():
        if key not in ["email", "registrationTimestamp"] and value is not None:
            if key == "password":
                value = hash_user_password(value)
            elif key == "roles" and not value:
                raise ValueError("User must have at least one role")
            setattr(user, key, value)

    session.add(user)
    session.commit()

@app.get("/users/")
async def get_users(session: Session = Depends(get_session),
                    criteria: Criteria | None = None, value: str | None = None,
                    params: Params = Depends()) -> list[User]:
    """
    Get users based on criteria
    :param session: Database session
    :param criteria: Criteria to filter users
    :param value: Value for the criteria
    :param params: Pagination parameters
    :return: List of Users
    """

    if not criteria:
        page = paginate(query=select(User)
                        .options(defer(User.password))
                        ,session=session, params=params)

    elif not value and criteria != Criteria.REGISTERATION_TODAY:
        raise HTTPException(status_code=400, detail="Value is required for the specified criteria")

    elif criteria == Criteria.ROLE:
        page = paginate(query=select(User)
                        .where(User.roles.any(value))
                        .options(defer(User.password))
                        ,session=session, params=params)

    elif criteria == Criteria.EMAIL_DOMAIN:
        domain_pattern = f"%@{value}"
        page = paginate(query=select(User)
                        .where(User.email.like(domain_pattern))
                        .options(defer(User.password))
                        ,session=session, params=params)

    elif criteria == Criteria.REGISTERATION_TODAY:
        today = datetime.now(tz=ZONE).date()
        page = paginate(
            query=select(User)
            .where(func.date(User.registrationTimestamp) == today)
            .options(defer(User.password))
            ,session=session, params=params)
    else:
        raise HTTPException(status_code=400, detail="Invalid criteria")

    return page.items

@app.delete("/users/", status_code=204)
async def delete_all_users(session: Session = Depends(get_session)):
    """
    Delete all users
    :param session: Database session
    """
    session.exec(delete(User))
    session.commit()