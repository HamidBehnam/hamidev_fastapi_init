from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.users.models import User
from app.users.schemas import UserRead, UserCreate

users_router = APIRouter()


@users_router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@users_router.get("/", response_model=list[UserRead])
async def read_users(session: Session = Depends(get_session)):
    users = session.query(User).all()
    return users


@users_router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

