from fastapi import APIRouter, HTTPException
from app.models import User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])

users_db: list[User] = []


@router.get("/")
async def list_users():
    return users_db


@router.post("/", status_code=201)
async def create_user(user: UserCreate):
    new_user = User(id=len(users_db) + 1, **user.model_dump())
    users_db.append(new_user)
    return new_user


@router.get("/{user_id}")
async def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")
