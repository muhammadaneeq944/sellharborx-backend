# backend/app/utils.py
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt
import os
from email.message import EmailMessage
import smtplib

# Load .env
from dotenv import load_dotenv
load_dotenv()

# ------------------------
# DB
# ------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "sellharborx")
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# ------------------------
# Security
# ------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ------------------------
# Email
# ------------------------
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", MAIL_USERNAME)

def _send_email_sync(subject: str, html_content: str, recipient: str, text_fallback: str = None):
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("Email credentials not configured.")
        return
    try:
        msg = EmailMessage()
        msg["From"] = MAIL_FROM
        msg["To"] = recipient
        msg["Subject"] = subject
        if text_fallback:
            msg.set_content(text_fallback)
            msg.add_alternative(html_content, subtype="html")
        else:
            msg.set_content("Please view in HTML client")
            msg.add_alternative(html_content, subtype="html")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

async def send_email(subject: str, html_content: str, recipient: str, text_fallback: str = None):
    await asyncio.to_thread(_send_email_sync, subject, html_content, recipient, text_fallback)
