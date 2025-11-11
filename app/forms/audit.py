# backend/app/forms/audit.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import asyncio

from ..utils import db, send_email, ADMIN_EMAIL

router = APIRouter()  # no prefix; main.py will include at top-level

class AuditIn(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    brandname: str
    producturl: str
    message: str

@router.post("/audit")
async def submit_audit(payload: AuditIn):
    """
    Save audit request to DB (collection: audits), send confirmation emails to user + admin.
    Prevent duplicate (same email + producturl) within 24 hours.
    """
    # Basic duplicate prevention: same email + producturl within 24 hours
    cutoff = datetime.utcnow() - timedelta(hours=24)
    dup = await db.audits.find_one({
        "email": payload.email,
        "producturl": payload.producturl,
        "created_at": { "$gte": cutoff }
    })
    if dup:
        raise HTTPException(status_code=409, detail="An audit request for this product was received recently. Please wait before requesting again.")

    doc = {
        "firstname": payload.firstname,
        "lastname": payload.lastname,
        "email": payload.email,
        "brandname": payload.brandname,
        "producturl": payload.producturl,
        "message": payload.message,
        "created_at": datetime.utcnow()
    }

    result = await db.audits.insert_one(doc)

    # Build user HTML email
    html_user = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#222;">
        <h2>Thanks {payload.firstname}! Your Free Amazon Audit Request is Confirmed</h2>
        <p>Hi {payload.firstname},</p>
        <p>Thank you for requesting a Free Amazon Account Audit from Sellharborx. Our experts are reviewing your store and analyzing opportunities to improve performance, ranking, and conversions.</p>
        <p><strong>Product URL:</strong> {payload.producturl}</p>
        <p>You will receive your detailed audit report within 24 to 48 hours. <br>If you have any quick questions, feel free to reply to this email. </p>
        <p style="margin-top:18px;">Regards<br/>SellHarborX Team</p>
      </body>
    </html>
    """
    text_user = f"Thanks {payload.firstname}, we received your audit request for {payload.brandname} ({payload.producturl}). Our team will contact you soon."

    # Build admin notification
    html_admin = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#222;">
        <h3>New Audit Request</h3>
        <ul>
          <li><strong>Name:</strong> {payload.firstname} {payload.lastname}</li>
          <li><strong>Email:</strong> {payload.email}</li>
          <li><strong>Brand:</strong> {payload.brandname}</li>
          <li><strong>Product URL:</strong> {payload.producturl}</li>
          <li><strong>Message:</strong> {payload.message}</li>
          <li><strong>Time (UTC):</strong> {datetime.utcnow().isoformat()}</li>
        </ul>
      </body>
    </html>
    """
    text_admin = f"New audit request: {payload.firstname} {payload.lastname} <{payload.email}> - {payload.brandname} - {payload.producturl}"

    # schedule email sending in background thread(s)
    try:
        asyncio.create_task(send_email("SellHarbor X — Audit request received", html_user, payload.email, text_user))
        asyncio.create_task(send_email("New audit request - SellHarbor X", html_admin, ADMIN_EMAIL, text_admin))
    except Exception as e:
        # don't break flow if email scheduling fails, just log
        print("Failed to schedule audit emails:", e)

    return {"message": "Audit request received", "id": str(result.inserted_id)}
