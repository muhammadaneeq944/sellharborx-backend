# # app/utils.py
# import os
# import asyncio
# import hashlib
# from datetime import datetime, timedelta
# from typing import Optional
# from email.message import EmailMessage
# from dotenv import load_dotenv

# from motor.motor_asyncio import AsyncIOMotorClient
# from passlib.context import CryptContext
# from jose import jwt

# # Load environment (local dev). Render will provide env vars in its dashboard.
# load_dotenv()

# # ------------------------
# # Database
# # ------------------------
# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# DB_NAME = os.getenv("DB_NAME", "sellharborx")
# client = AsyncIOMotorClient(MONGO_URI)
# db = client[DB_NAME]

# def get_collection(name: str):
#     return db[name]

# # ------------------------
# # Security / Auth
# # ------------------------
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
# ALGORITHM = os.getenv("ALGORITHM", "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# def _pre_hash(password: str) -> str:
#     return hashlib.sha256(password.encode("utf-8")).hexdigest()

# def get_password_hash(password: str) -> str:
#     pre = _pre_hash(password)
#     return pwd_context.hash(pre)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     pre = _pre_hash(plain_password)
#     return pwd_context.verify(pre, hashed_password)

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return token

# # ------------------------
# # Email (smtplib using SMTP server: SendGrid)
# # ------------------------
# MAIL_HOST = os.getenv("MAIL_HOST", "smtp.sendgrid.net")
# MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
# MAIL_USERNAME = os.getenv("MAIL_USERNAME", "apikey")   # must be 'apikey' for SendGrid
# MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")         # the SendGrid API Key
# MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
# ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", MAIL_FROM)

# def _send_email_sync(subject: str, html_content: str, recipient: str, text_fallback: Optional[str] = None):
#     """
#     Synchronous sending using smtplib (TLS). Works for SendGrid SMTP (smtp.sendgrid.net:587).
#     Runs in a thread via asyncio.to_thread when called from async code.
#     """
#     if not MAIL_USERNAME or not MAIL_PASSWORD:
#         print("⚠️ Mail credentials not set. Skipping send.")
#         return False

#     try:
#         msg = EmailMessage()
#         msg["From"] = MAIL_FROM
#         msg["To"] = recipient
#         msg["Subject"] = subject

#         if text_fallback:
#             msg.set_content(text_fallback)
#         # HTML part
#         msg.add_alternative(html_content, subtype="html")

#         # Connect to SMTP
#         import smtplib
#         with smtplib.SMTP(MAIL_HOST, MAIL_PORT, timeout=20) as server:
#             server.ehlo()
#             server.starttls()
#             server.ehlo()
#             server.login(MAIL_USERNAME, MAIL_PASSWORD)
#             server.send_message(msg)

#         print(f"✅ Email sent to {recipient} (subject: {subject})")
#         return True

#     except Exception as exc:
#         print(f"❌ Failed to send email to {recipient}: {exc}")
#         return False

# async def send_email(subject: str, html_content: str, recipient: str, text_fallback: Optional[str] = None):
#     """
#     Async wrapper - schedule synchronous send in a thread.
#     Returns True/False for success.
#     """
#     return await asyncio.to_thread(_send_email_sync, subject, html_content, recipient, text_fallback)









# app/utils.py
import os
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from email.message import EmailMessage
import requests
from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt

load_dotenv()

# ------------------------
# Database
# ------------------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "sellharborx")
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

def get_collection(name: str):
    return db[name]

# ------------------------
# Security / Auth
# ------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

def _pre_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_password_hash(password: str) -> str:
    pre = _pre_hash(password)
    return pwd_context.hash(pre)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pre = _pre_hash(plain_password)
    return pwd_context.verify(pre, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ------------------------
# Email (SendGrid API)
# ------------------------
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAIL_FROM = os.getenv("MAIL_FROM")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", MAIL_FROM)

async def send_email(subject: str, html_content: str, recipient: str, text_fallback: Optional[str] = " "):
    if not SENDGRID_API_KEY:
        print("⚠️ SendGrid API Key missing. Email skipped.")
        return False
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "personalizations": [{"to": [{"email": recipient}]}],
        "from": {"email": MAIL_FROM},
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": text_fallback},
            {"type": "text/html", "value": html_content}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"📨 Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Email sending failed → {e}")
        return False
