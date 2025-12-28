# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .forms.signup import signup_router
from .forms.admin import admin_router
from .forms.login import login_router
from .forms.meeting import router as meeting_router
from .forms.audit import router as audit_router
from .forms.contact import router as contact_router
from .forms.newsletter import router as newsletter_router
from .forms.package_form import router as package_form_router
from dotenv import load_dotenv
from app.database import db
from app.utils import get_password_hash

load_dotenv()

app = FastAPI(title="Sell Harbor X - Backend")

origins = [
    "https://sellharborx.com",
    "https://www.sellharborx.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(signup_router)
app.include_router(admin_router)
app.include_router(login_router)
app.include_router(meeting_router)
app.include_router(audit_router)
app.include_router(contact_router)
app.include_router(newsletter_router)
app.include_router(package_form_router)

@app.get("/")
def root():
    return {"message": "Backend running successfully!"}

@app.on_event("startup")
async def startup_setup():
    print("🚀 Running startup tasks...")

    try:
        await db.newsletters.create_index("email", unique=True)
        print("✔ Unique index added: newsletters(email)")
    except:
        pass

    try:
        await db.meetings.create_index([("email", 1), ("date", 1)], unique=True)
        print("✔ Unique index added: meetings(email + date)")
    except:
        pass

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    existing_admin = await db["admins"].find_one({"username": admin_username})
    if not existing_admin:
        hashed_pw = get_password_hash(admin_password)
        await db["admins"].insert_one({
            "username": admin_username,
            "password": hashed_pw,
            "role": "admin"
        })
        print(f"✔ Admin created: {admin_username}")

