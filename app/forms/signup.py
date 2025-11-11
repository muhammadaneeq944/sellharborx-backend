# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, EmailStr
# from ..utils import db, get_password_hash, send_email, ADMIN_EMAIL
# from datetime import datetime
# import asyncio

# signup_router = APIRouter()

# class SignupIn(BaseModel):
#     username: str
#     email: EmailStr
#     password: str

# @signup_router.post("/signup")
# async def signup(user: SignupIn):
#     existing = await db.users.find_one({"email": user.email})
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     if len(user.password.encode("utf-8")) > 72:
#         raise HTTPException(status_code=400, detail="Password too long")
    
#     hashed_pw = get_password_hash(user.password)
#     result = await db.users.insert_one({
#         "username": user.username,
#         "email": user.email,
#         "password": hashed_pw,
#         "created_at": datetime.utcnow()
#     })

#     html_user = f"<h2>Welcome, {user.username}</h2>"
#     text_user = f"Welcome {user.username}!"

#     html_admin = f"<p>New user: {user.username} - {user.email}</p>"
#     text_admin = f"New user registered: {user.username} - {user.email}"

#     asyncio.create_task(send_email("Welcome!", html_user, user.email, text_user))
#     asyncio.create_task(send_email("New user", html_admin, ADMIN_EMAIL, text_admin))

#     return {"message": "Signup successful", "user_id": str(result.inserted_id)}


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from ..utils import db, get_password_hash, send_email, ADMIN_EMAIL
from datetime import datetime
import asyncio

signup_router = APIRouter()

class SignupIn(BaseModel):
    username: str
    email: EmailStr
    password: str

@signup_router.post("/signup")
async def signup(user: SignupIn):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        # Instead of raising HTTPException, return a flag the frontend expects
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

    # Send welcome + admin notification emails asynchronously
    html_user = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <h2 style="color: #2d89ef;">Welcome to SellHarborX, {user.username}!</h2>
          <p>Dear {user.username},</p>
          <p>Thank you for joining Sellharborx. We are excited to help you accelerate your Amazon growth with advanced marketing and optimization solutions.</p>

          <p>You have unlocked access to professional tools and expert support for successful selling.</p>
         

          

          <p style="margin-top: 25px;">If you have any questions, our support team is always available to help.</p>

          <hr style="margin: 30px 0;"/>
          <p style="font-size: 0.9em; color: #555;">
            Regards<br>
            <strong>SellHarborX Team</strong><br>
            
          </p>
        </div>
      </body>
    </html>
      """
    text_user =  (
        f"Welcome to Sell Harbor X, {user.username}!\n\n"
        f"We’re excited to have you onboard. Our team will help you choose the best service package for your needs.\n"
        f"Feel free to reply to this email for assistance.\n\n"
        f"— The Sell Harbor X Team"
    )

    html_admin = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <h2 style="color: #2d89ef;">New User Registration Alert</h2>
          <p>Dear Admin,</p>
          <p>A new user has successfully signed up on the Sell Harbor X platform.</p>

          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Username:</strong></td>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;">{user.username}</td>
            </tr>
            <tr>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Email:</strong></td>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;">{user.email}</td>
            </tr>
            <tr>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Signup Time (UTC):</strong></td>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;">{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}</td>
            </tr>
          </table>

          <p style="margin-top: 20px;">Please ensure this user receives proper onboarding support.</p>

          <hr style="margin: 30px 0;"/>
          <p style="font-size: 0.9em; color: #555;">
            Regards,<br>
            <strong>Sell Harbor X System</strong>
          </p>
        </div>
      </body>
    </html>
    """
    text_admin = (
        f"New user registration:\n\n"
        f"Username: {user.username}\n"
        f"Email: {user.email}\n"
        f"Signup Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    asyncio.create_task(send_email("Welcome to Sell Harbor X!", html_user, user.email, text_user))
    asyncio.create_task(send_email("New User Registration", html_admin, ADMIN_EMAIL, text_admin))

    return {
        "success": True,
        "message": "Signup successful!",
        "user_id": str(result.inserted_id)
    }
