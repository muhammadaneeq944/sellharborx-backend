# # backend/app/utils.py
# import asyncio
# from datetime import datetime, timedelta
# from motor.motor_asyncio import AsyncIOMotorClient
# from passlib.context import CryptContext
# from jose import jwt
# import os
# from email.message import EmailMessage
# import smtplib
# import hashlib
# from dotenv import load_dotenv

# # ------------------------
# # Load environment variables
# # ------------------------
# load_dotenv()

# # ------------------------
# # Database Setup
# # ------------------------
# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# DB_NAME = os.getenv("DB_NAME", "sellharborx")

# # Create a single async MongoDB client (recommended pattern for FastAPI)
# client = AsyncIOMotorClient(MONGO_URI)
# db = client[DB_NAME]

# # ------------------------
# # Security / Authentication
# # ------------------------
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
# ALGORITHM = os.getenv("ALGORITHM", "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


# def _pre_hash(password: str) -> str:
#     """
#     Safely pre-hash long strings to avoid bcrypt's 72-byte limit.
#     SHA-256 reduces any input (secret, password, etc.) to 64 hex chars.
#     """
#     return hashlib.sha256(password.encode("utf-8")).hexdigest()


# def get_password_hash(password: str) -> str:
#     """
#     Hash a password using SHA256 pre-hash + bcrypt.
#     Prevents bcrypt errors for inputs >72 bytes.
#     """
#     pre = _pre_hash(password)
#     return pwd_context.hash(pre)


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Verify a password using SHA256 pre-hash + bcrypt.
#     """
#     pre = _pre_hash(plain_password)
#     return pwd_context.verify(pre, hashed_password)


# def create_access_token(data: dict, expires_delta: timedelta = None):
#     """
#     Create a JWT token with expiration time.
#     """
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# # ------------------------
# # Email Utility
# # ------------------------
# MAIL_USERNAME = os.getenv("MAIL_USERNAME")
# MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
# MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
# ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", MAIL_USERNAME)


# def _send_email_sync(subject: str, html_content: str, recipient: str, text_fallback: str = None):
#     """
#     Send an email synchronously via Gmail SMTP (TLS).
#     """
#     if not MAIL_USERNAME or not MAIL_PASSWORD:
#         print("⚠️ Email credentials not configured.")
#         return

#     try:
#         msg = EmailMessage()
#         msg["From"] = MAIL_FROM
#         msg["To"] = recipient
#         msg["Subject"] = subject

#         if text_fallback:
#             msg.set_content(text_fallback)
#         msg.add_alternative(html_content, subtype="html")

#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(MAIL_USERNAME, MAIL_PASSWORD)
#             server.send_message(msg)

#         print(f"✅ Email sent successfully to {recipient}")

#     except Exception as e:
#         print(f"❌ Failed to send email: {e}")


# async def send_email(subject: str, html_content: str, recipient: str, text_fallback: str = None):
#     """
#     Asynchronously send an email using a background thread.
#     """
#     await asyncio.to_thread(_send_email_sync, subject, html_content, recipient, text_fallback)




# backend/app/utils.py
import asyncio
import os
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL") or MAIL_USERNAME
MAIL_HOST = os.getenv("MAIL_HOST", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))  # default TLS port

def _send_email_sync(subject: str, html_content: str, recipient: str, text_fallback: str = None):
    """
    Send an email synchronously using SMTP.
    """
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("⚠️ Email credentials not set.")
        return

    try:
        msg = EmailMessage()
        msg["From"] = MAIL_FROM
        msg["To"] = recipient
        msg["Subject"] = subject

        if text_fallback:
            msg.set_content(text_fallback)
        msg.add_alternative(html_content, subtype="html")

        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent to {recipient}")

    except Exception as e:
        print(f"❌ Failed to send email to {recipient}: {e}")

async def send_email(subject: str, html_content: str, recipient: str, text_fallback: str = None):
    """
    Async wrapper to send email in background.
    """
    await asyncio.to_thread(_send_email_sync, subject, html_content, recipient, text_fallback)


