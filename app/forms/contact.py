# backend/app/forms/contact.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
import asyncio

from ..utils import db, send_email, ADMIN_EMAIL

router = APIRouter()  # top-level (no prefix)

class ContactIn(BaseModel):
    firstname: str
    email: EmailStr
    subject: str
    message: str

@router.post("/contact", status_code=status.HTTP_201_CREATED)
async def submit_contact(payload: ContactIn):
    """
    Save contact request to db.contacts and send confirmation emails:
    - confirmation to user
    - notification to admin (ADMIN_EMAIL from .env)
    """
    # Build DB doc
    doc = {
        "firstname": payload.firstname,
        "email": payload.email,
        "subject": payload.subject,
        "message": payload.message,
        "created_at": datetime.utcnow()
    }

    # Insert into DB (collection: contacts)
    try:
        result = await db.contacts.insert_one(doc)
    except Exception as e:
        # if DB error, return 500
        raise HTTPException(status_code=500, detail="Failed to save contact request") from e

    # Build email HTML/text for user
    html_user = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#222;">
        <h2>Thanks {payload.firstname} — we received your message</h2>
        <p>Hi {payload.firstname},</p>
        <p>Thank you for contacting Sell Harbor X regarding <strong>{payload.subject}</strong>.</p>
        <p>We received your message and our team will contact you soon to help you further.</p>
        <p style="margin-top:18px;">Regards,<br/>SellHarbor X Team</p>
      </body>
    </html>
    """
    text_user = f"Hi {payload.firstname},\n\nThanks for contacting SellHarbor X about '{payload.subject}'. Our team will contact you soon.\n\nRegards,\nSellHarbor X"

    # Build email for admin
    html_admin = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#222;">
        <h3>New Contact Request</h3>
        <ul>
          <li><strong>Name:</strong> {payload.firstname}</li>
          <li><strong>Email:</strong> {payload.email}</li>
          <li><strong>Subject:</strong> {payload.subject}</li>
          <li><strong>Message:</strong> {payload.message}</li>
          <li><strong>Time (UTC):</strong> {datetime.utcnow().isoformat()}</li>
        </ul>
      </body>
    </html>
    """
    text_admin = f"New contact: {payload.firstname} <{payload.email}> - {payload.subject}\n\n{payload.message}"

    # schedule emails in background (do not block)
    try:
        asyncio.create_task(send_email("SellHarbor X — We received your message", html_user, payload.email, text_user))
        asyncio.create_task(send_email("New contact request - SellHarbor X", html_admin, ADMIN_EMAIL, text_admin))
    except Exception as e:
        # do not fail the request if email scheduling fails; just log to stdout
        print("Failed to schedule contact emails:", e)

    return {"message": "Contact request received", "id": str(result.inserted_id)}
