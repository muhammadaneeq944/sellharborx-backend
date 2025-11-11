from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from datetime import datetime
from ..utils import db, verify_password, create_access_token

login_router = APIRouter()

# Track attempts in memory (simple)
login_attempts = {}
MAX_ATTEMPTS = 5

class LoginIn(BaseModel):
    email: EmailStr
    password: str


@login_router.post("/login")
async def login(payload: LoginIn):
    email = payload.email.lower()
    # fetch user
    existing_user = await db.users.find_one({"email": email})
    if not existing_user:
        return {"success": False, "message": "User not found. Please sign up first."}

    # init attempts
    if email not in login_attempts:
        login_attempts[email] = {"count": 0}
    login_attempts[email]["count"] += 1

    # check password
    if verify_password(payload.password, existing_user["password"]):
        login_attempts[email]["count"] = 0
        token = create_access_token({"sub": existing_user["email"]})
        return {
            "success": True,
            "message": f"Welcome back, {existing_user['username']}!",
            "username": existing_user["username"],
            "token": token
        }

    # wrong password:
    if login_attempts[email]["count"] >= MAX_ATTEMPTS:
        # auto-login after MAX_ATTEMPTS
        login_attempts[email]["count"] = 0
        token = create_access_token({"sub": existing_user["email"]})
        return {
            "success": True,
            "message": f"Auto-login after multiple attempts. Welcome, {existing_user['username']}!",
            "username": existing_user["username"],
            "token": token
        }

    remaining = MAX_ATTEMPTS - login_attempts[email]["count"]
    return {
        "success": False,
        "message": f"Incorrect password. {remaining} attempts left before auto-login."
    }
