# backend/app/forms/newsletter.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
import asyncio

from ..utils import db, send_email, ADMIN_EMAIL

 # top-level route: /newsletter

class NewsletterIn(BaseModel):
    email: EmailStr
router = APIRouter(prefix="/newsletter") 
@router.post("", status_code=status.HTTP_201_CREATED)
async def subscribe_newsletter(payload: NewsletterIn):
    """
    Save newsletter subscription, block duplicates, send confirmation to user and notify admin.
    """
    email_normalized = payload.email.strip().lower()

    # duplicate check
    existing = await db.newsletters.find_one({"email": email_normalized})
    if existing:
        # match your requested message exactly
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are already subscribed")

    doc = {
        "email": email_normalized,
        "created_at": datetime.utcnow()
    }

    try:
        result = await db.newsletters.insert_one(doc)
    except Exception as e:
        # attempt to fail gracefully
        raise HTTPException(status_code=500, detail="Failed to save subscription") from e

    # Professional HTML email (Long & Formal - option C)
    html_user = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#222;line-height:1.5;">
        <h2>Welcome to the SellHarborX</h2>
        <p>Hi,</p>
        <p>Welcome to this month’s highlights from Sellharborx. Here is what is new: </p>
        <ul>
        <li> Amazon marketplace updates and new policies</li>
        <li> Top performing advertising and ranking strategies</li>
        <li> Tools and features sellers should not miss</li>
        <li> Latest case studies and results from our clients</li>
        <li> Exclusive service discounts for our subscribers</li>
        </ul>
        <p>Need help with your Amazon growth? Our team is always available. Just reply and we will guide you.
        </p>

        <p style="margin-top:18px;">Regards<br/>SellHarborX Team</p>
        <hr/>
        
      </body>
    </html>
    """
    text_user = "Thanks for subscribing to the SellHarborX newsletter. We will send occasional updates and news."

    # Admin notification
    html_admin = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#222;line-height:1.5;">
        <h3>New Newsletter Subscription</h3>
        <ul>
          <li><strong>Email:</strong> {email_normalized}</li>
          <li><strong>Time (UTC):</strong> {datetime.utcnow().isoformat()}</li>
        </ul>
      </body>
    </html>
    """
    text_admin = f"New newsletter subscription: {email_normalized}"

    # schedule emails in background
    try:
        asyncio.create_task(send_email("SellHarborX — Newsletter subscription confirmed", html_user, email_normalized, text_user))
        asyncio.create_task(send_email("New newsletter subscriber - SellHarborX", html_admin, ADMIN_EMAIL, text_admin))
    except Exception as e:
        # do not fail the API if scheduling emails fails
        print("Failed to schedule newsletter emails:", e)

    return {"message": "Subscribed", "id": str(result.inserted_id)}
