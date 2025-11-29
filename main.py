from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from models import ZONE, Criteria, User
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import bcrypt
import re
from db import init_db, get_session, engine
from sqlmodel import Session, delete, select
from sqlalchemy.orm import defer
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from fastapi_pagination import Page, add_pagination, Params
from fastapi_pagination.ext.sqlmodel import paginate

def authenticate_user(email: str, password: str, session: Session) -> User:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    #validate_password(password)
    
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise ValueError("Incorrect password")
    
    return user

def hash_user_password(password: str) -> str:
    
    validate_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def validate_password(password: str) -> str:
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()    
    #init_data()
    yield

app = FastAPI(lifespan=lifespan)
add_pagination(app)

def init_data():
    with Session(engine) as session:
        for user_data in USERS:
            user = session.exec(select(User).where(User.email == user_data["email"])).first()
            if not user:
                user = User(**user_data)
                user.password = hash_user_password(user.password)
                session.add(user)
        session.commit()
    
@app.get("/")
async def ping():
    return {"Hello": "World"}

@app.exception_handler(ValueError)
async def value_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})

#handles all other exceptions like springboot
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.post("/users")
async def upload_notification(to_upload: User, session: Session = Depends(get_session)) -> User:
    #salt = bcrypt.gensalt()
    #validate_password(to_upload.password)
    to_upload.password = hash_user_password(to_upload.password) #= bcrypt.hashpw(to_upload.password.encode('utf-8'), salt).decode('utf-8')
    
    user = User(**to_upload.model_dump())
    session.add(user)
    
    session.commit()
    session.refresh(user)
    
    user.password = "redacted"
    return user

@app.get("/users/{email}")
async def get_specific_user(email: str, password: str, session: Session = Depends(get_session)) -> User:
    user = authenticate_user(email, password, session)
    
    user.password = "redacted"
    return user

@app.put("/users/{email}", status_code=204)
async def update_user(email: str, to_update: User, password: str, session: Session = Depends(get_session)):
    user = authenticate_user(email, password, session)
    
    for key, value in to_update.model_dump().items():
        if key not in ["email", "registrationTimestamp"] and value is not None:
            if key == "password":
                value = hash_user_password(value)
            setattr(user, key, value)
    
    session.add(user)
    session.commit()

@app.get("/users/") 
async def get_users(session: Session = Depends(get_session), criteria: Criteria | None = None, value: str | None = None, params: Params = Depends()) -> list[User]:
    
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
    session.exec(delete(User))
    session.commit()