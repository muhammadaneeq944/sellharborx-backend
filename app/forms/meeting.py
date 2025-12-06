# # backend/app/forms/meeting.py
# from fastapi import APIRouter, HTTPException, status
# from pydantic import BaseModel, EmailStr
# from datetime import datetime
# import asyncio
# from pymongo.errors import DuplicateKeyError
# from ..database import db
# from ..utils import send_email, ADMIN_EMAIL

# router = APIRouter()

# class MeetingIn(BaseModel):
#     name: str
#     email: EmailStr
#     agenda: str
#     date: str   # YYYY-MM-DD


# @router.post("/book-meeting", status_code=status.HTTP_201_CREATED)
# async def book_meeting(payload: MeetingIn):
#     # ✅ Validate date
#     try:
#         datetime.strptime(payload.date, "%Y-%m-%d")
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid date format")

#     # ✅ Check for duplicate booking
#     existing = await db.meetings.find_one({"email": payload.email, "date": payload.date})
#     if existing:
#         raise HTTPException(status_code=409, detail="You already booked a meeting for this date")

#     # ✅ Insert new booking
#     doc = {
#         "name": payload.name,
#         "email": payload.email,
#         "agenda": payload.agenda,
#         "date": payload.date,
#         "created_at": datetime.utcnow(),
#     }

#     try:
#         result = await db.meetings.insert_one(doc)
#     except DuplicateKeyError:
#         raise HTTPException(status_code=409, detail="You already booked a meeting for this date")

#     # ✅ --- EMAILS (background tasks) ---
#     html_user = f"""
#     <html>
#        <body>
#           <h2>Strategy Call Successfully Booked</h2>
#           <p>Hi {payload.name},</p>
#           <p>Your strategy call with <strong>SellHarborX</strong> has been successfully scheduled. 
#           We are looking forward to discussing growth opportunities and building a powerful roadmap 
#           for your Amazon success.</p>
#           <p><strong>Date:</strong> {payload.date}<br>
#              <strong>Agenda:</strong> {payload.agenda}</p>
#           <p>If there is any change required in the meeting schedule from our side, we will adjust 
#           the time and notify you promptly.</p>
#           <p>We will also send you a reminder before the meeting time. In case you need to reschedule, 
#           simply reply to this email.</p>
#           <p style="margin-top:18px;">Regards,<br/>SellHarborX Team</p>
#        </body>
#     </html>
#     """

#     text_user = f"Your meeting is received for {payload.date}."

#     html_admin = f"""
#     <html><body>
#       <p><strong>New Meeting Booked</strong></p>
#       <ul>
#         <li>{payload.name}</li>
#         <li>{payload.email}</li>
#         <li>{payload.date}</li>
#         <li>{payload.agenda}</li>
#       </ul>
#     </body></html>
#     """

#     text_admin = f"New meeting: {payload.email} on {payload.date}"

#     try:
#         # Schedule both emails asynchronously (non-blocking)
#         asyncio.create_task(send_email("Meeting request received", html_user, payload.email, text_user))
#         asyncio.create_task(send_email("New Meeting Booked", html_admin, ADMIN_EMAIL, text_admin))
#     except Exception as e:
#         print("Email scheduling failed:", e)

#     # ✅ Return AFTER scheduling emails
#     return {"message": "Meeting booked", "booking_id": str(result.inserted_id)}




from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
import asyncio
from pymongo.errors import DuplicateKeyError

from ..database import db
from ..utils import send_email, ADMIN_EMAIL

router = APIRouter()


class MeetingIn(BaseModel):
    name: str
    email: EmailStr
    agenda: str
    date: str   # Format: YYYY-MM-DD


@router.post("/book-meeting", status_code=status.HTTP_201_CREATED)
async def book_meeting(payload: MeetingIn):

    # -----------------------------------------
    # ✅ Validate date format YYYY-MM-DD
    # -----------------------------------------
    try:
        datetime.strptime(payload.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # -----------------------------------------
    # ✅ Check for existing booking for same date + email
    # -----------------------------------------
    existing = await db.meetings.find_one({
        "email": payload.email,
        "date": payload.date
    })

    if existing:
        raise HTTPException(
            status_code=409,
            detail="You already booked a meeting for this date"
        )

    # -----------------------------------------
    # ✅ Insert meeting in DB
    # -----------------------------------------
    document = {
        "name": payload.name,
        "email": payload.email,
        "agenda": payload.agenda,
        "date": payload.date,
        "created_at": datetime.utcnow(),
    }

    try:
        result = await db.meetings.insert_one(document)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="You already booked a meeting for this date"
        )

    # -----------------------------------------
    # ✅ Prepare Email Templates
    # -----------------------------------------

    # User email
    html_user = f"""
    <html>
       <body>
          <h2>Strategy Call Successfully Booked</h2>
          <p>Hi {payload.name},</p>
          <p>Your strategy call with <strong>SellHarborX</strong> has been successfully scheduled.</p>
          <p><strong>Date:</strong> {payload.date}<br>
             <strong>Agenda:</strong> {payload.agenda}</p>
          <p>We will send you a reminder before the meeting. 
          To reschedule, you can reply to this email.</p>
          <p style="margin-top:18px;">Regards,<br/>SellHarborX Team</p>
       </body>
    </html>
    """

    text_user = f"Your meeting is confirmed for {payload.date}. Agenda: {payload.agenda}"

    # Admin email
    html_admin = f"""
    <html><body>
      <p><strong>New Meeting Booked</strong></p>
      <ul>
        <li>Name: {payload.name}</li>
        <li>Email: {payload.email}</li>
        <li>Date: {payload.date}</li>
        <li>Agenda: {payload.agenda}</li>
      </ul>
    </body></html>
    """

    text_admin = (
        f"New meeting booked:\n"
        f"Name: {payload.name}\n"
        f"Email: {payload.email}\n"
        f"Date: {payload.date}\n"
        f"Agenda: {payload.agenda}"
    )

    # -----------------------------------------
    # ✅ Send emails (non-blocking)
    # -----------------------------------------
    try:
        asyncio.create_task(
            send_email("Your Strategy Call is Booked", html_user, payload.email, text_user)
        )
        asyncio.create_task(
            send_email("New Meeting Booked", html_admin, ADMIN_EMAIL, text_admin)
        )
    except Exception as e:
        print("Email scheduling failed:", e)

    # -----------------------------------------
    # ✅ Final Response
    # -----------------------------------------
    return {
        "message": "Meeting booked successfully",
        "booking_id": str(result.inserted_id)
    }
