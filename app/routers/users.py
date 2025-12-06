from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import defer
from sqlmodel import Session, delete, select
from datetime import datetime, timedelta
from fastapi_pagination.ext.sqlmodel import paginate
from app.pagination import ZeroBasedParams
from app.models.user import User
from app.models.consts import ZONE, Criteria
from app.database import get_session
from app.auth.utils import authenticate_user, hash_user_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model_exclude={"password"})
async def create_user(to_upload: User, session: Session = Depends(get_session)) -> User:
    """
    Upload a new user
    :param to_upload: User to upload
    :param session: Database session
    :return: Uploaded User
    """
    to_upload.password = hash_user_password(to_upload.password)
    to_upload.registrationTimestamp = datetime.now(ZONE)
    user = User(**to_upload.model_dump())
    
    if not user.roles:
        raise ValueError("User must have at least one role")
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{email}", response_model_exclude={"password"})
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


@router.put("/{email}", status_code=204)
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


@router.get("/", response_model_exclude_none=True)
async def get_users(session: Session = Depends(get_session),
                    criteria: Criteria | None = None, value: str | None = None,
                    params: ZeroBasedParams = Depends()) -> list[User]:
    """
    Get users based on criteria
    :param session: Database session
    :param criteria: Criteria to filter users
    :param value: Value for the criteria
    :param params: Pagination parameters
    :return: List of Users
    """
    if not criteria:
        query=select(User)

    elif not value and criteria != Criteria.REGISTERATION_TODAY:
        raise HTTPException(status_code=400, detail="Value is required for the specified criteria")

    elif criteria == Criteria.ROLE:
        query=select(User).where(User.roles.any(value))

    elif criteria == Criteria.EMAIL_DOMAIN:
        domain_pattern = f"%@{value}"
        query=select(User).where(User.email.like(domain_pattern))

    elif criteria == Criteria.REGISTERATION_TODAY:
        last_24_hours = datetime.now(tz=ZONE) - timedelta(hours=24)
        
        query=select(User).where(User.registrationTimestamp >= last_24_hours)
    else:
        raise HTTPException(status_code=400, detail="Invalid criteria")
    
    query = query.options(defer(User.password)).order_by(User.registrationTimestamp.desc())
    page = paginate(query=query, params=params, session=session)

    return page.items


@router.delete("/", status_code=204)
async def delete_all_users(session: Session = Depends(get_session)):
    """
    Delete all users
    :param session: Database session
    """
    session.exec(delete(User))
    session.commit()
