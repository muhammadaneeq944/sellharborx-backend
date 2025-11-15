from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from ..utils import db, get_password_hash, send_email, ADMIN_EMAIL
from datetime import datetime
import asyncio

signup_router = APIRouter(prefix="/signup", tags=["Signup"])   # FIX

class SignupIn(BaseModel):
    username: str
    email: EmailStr
    password: str

@signup_router.post("")
async def signup(user: SignupIn):

    existing = await db.users.find_one({"email": user.email})
    if existing:
        return {
            "alreadyExists": True,
            "message": "Email already registered. Please login."
        }

    if len(user.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password too long")

    hashed_pw = get_password_hash(user.password)
    result = await db.users.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_pw,
        "created_at": datetime.utcnow()
    })

    # EMAILS
    html_user = "<html>...</html>"  # keep your template
    html_admin = "<html>...</html>"

    asyncio.create_task(send_email("Welcome to Sell Harbor X!", html_user, user.email, ""))
    asyncio.create_task(send_email("New User Registration", html_admin, ADMIN_EMAIL, ""))

    return {
        "success": True,
        "message": "Signup successful!",
        "user_id": str(result.inserted_id)
    }
