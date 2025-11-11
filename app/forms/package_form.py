from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
import asyncio
from pymongo.errors import DuplicateKeyError

from ..database import db
from ..utils import send_email, ADMIN_EMAIL

router = APIRouter()

# ✅ Data model
class PackageForm(BaseModel):
    package: str
    price: str
    name: str
    email: EmailStr
    company: str
    url: str
    businessType: str
    notes: str | None = None


@router.post("/choose-package", status_code=status.HTTP_201_CREATED)
async def choose_package(payload: PackageForm):
    """Store package form data in MongoDB and send branded confirmation emails"""

    # 🧠 Prevent duplicates for same user + package
    existing = await db.packages.find_one({"email": payload.email, "package": payload.package})
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"You have already submitted a request for the {payload.package} package."
        )

    # 🗃️ Prepare DB document
    doc = {
        "package": payload.package,
        "price": payload.price,
        "name": payload.name,
        "email": payload.email,
        "company": payload.company,
        "url": payload.url,
        "businessType": payload.businessType,
        "notes": payload.notes or "",
        "created_at": datetime.utcnow()
    }

    try:
        result = await db.packages.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Duplicate package submission detected.")
    except Exception as e:
        print("❌ DB error:", e)
        raise HTTPException(status_code=500, detail="Database insertion failed.")

    # 📨 Professional Email Templates
    # ---- USER EMAIL ----
    html_user = f"""
    <html>
      <body style="font-family:'Poppins',Arial,sans-serif;background-color:#f8f9fa;padding:20px;color:#222;">
        <div style="max-width:600px;margin:auto;background:white;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.1);">
          <div style="background:#111;padding:20px;text-align:center;">
            <h2 style="color:#2ecc71;margin:0;">Sell Harbor X</h2>
            <p style="color:#ccc;margin:5px 0;">Thank you for your trust!</p>
          </div>
          <div style="padding:25px;">
            <h3 style="color:#111;">Hi {payload.name},</h3>
            <p>We’ve received your request for the <b>{payload.package}</b> package priced at <b>{payload.price}</b>.</p>
            <p>Our account specialists will contact you within <b>24 hours</b> to guide you through next steps and finalize your onboarding process.</p>
            <p style="margin-top:20px;">Meanwhile, you can explore our services and client success stories on our website.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:25px 0;">
            <p style="font-size:0.9em;color:#666;">Best regards,<br><b>The Sell Harbor X Team</b></p>
          </div>
          <div style="background:#2ecc71;color:white;text-align:center;padding:10px;font-size:13px;">
            <p style="margin:0;">© {datetime.utcnow().year} Sell Harbor X. All rights reserved.</p>
          </div>
        </div>
      </body>
    </html>
    """
    text_user = f"""
    Hi {payload.name},

    We’ve received your {payload.package} package request ({payload.price}) at Sell Harbor X.
    Our team will reach out within 24 hours to get you started.

    — The Sell Harbor X Team
    """

    # ---- ADMIN EMAIL ----
    html_admin = f"""
    <html>
      <body style="font-family:'Poppins',Arial,sans-serif;background-color:#f8f9fa;padding:20px;color:#111;">
        <div style="max-width:650px;margin:auto;background:white;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.1);">
          <div style="background:#111;padding:20px;text-align:center;">
            <h2 style="color:#2ecc71;margin:0;">New Package Request</h2>
          </div>
          <div style="padding:25px;">
            <p><b>New package form submission received.</b></p>
            <ul style="line-height:1.7;font-size:15px;color:#333;">
              <li><b>Name:</b> {payload.name}</li>
              <li><b>Email:</b> {payload.email}</li>
              <li><b>Product:</b> {payload.company}</li>
              <li><b>Package:</b> {payload.package}</li>
              <li><b>Price:</b> {payload.price}</li>
              <li><b>Business Type:</b> {payload.businessType}</li>
              <li><b>URL:</b> <a href="{payload.url}" style="color:#2ecc71;">{payload.url}</a></li>
              <li><b>Notes:</b> {payload.notes or '—'}</li>
              <li><b>Submitted At (UTC):</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</li>
            </ul>
          </div>
          <div style="background:#2ecc71;color:white;text-align:center;padding:10px;font-size:13px;">
            <p style="margin:0;">Sell Harbor X Admin Notification</p>
          </div>
        </div>
      </body>
    </html>
    """
    text_admin = (
        f"New package submission:\n"
        f"- Package: {payload.package}\n"
        f"- Price: {payload.price}\n"
        f"- Name: {payload.name}\n"
        f"- Email: {payload.email}\n"
        f"- Business: {payload.businessType}\n"
        f"- Product: {payload.company}\n"
        f"- URL: {payload.url}\n"
        f"- Notes: {payload.notes or '—'}\n"
    )

    # 🔄 Send emails asynchronously
    try:
        asyncio.create_task(send_email(
        "✅ Your Package Request — Sell Harbor X",
        html_user,
        payload.email,
        text_user
        ))
        
        asyncio.create_task(send_email(
        f"📦 New Package Form — {payload.package}",
        html_admin,
        ADMIN_EMAIL,
        text_admin
        ))
    except Exception as e:
        print("❌ Email sending failed:", e)

    return {
        "message": "Package request submitted successfully. A confirmation email has been sent.",
        "id": str(result.inserted_id)
    }
