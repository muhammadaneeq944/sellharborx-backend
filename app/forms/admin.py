from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from ..utils import db, verify_password, create_access_token, get_password_hash
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from fastapi import Header, HTTPException, Depends


SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

admin_router = APIRouter(prefix="/admin")

# ------------------------
# Pydantic models
# ------------------------
class AdminLoginIn(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    username: str
    email: str
    id: str

class UserUpdateIn(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

# ------------------------
# Auth helper
# ------------------------
from fastapi import Header, HTTPException, Depends

async def get_current_admin(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ")[1]

    # Verify the JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return username


# ------------------------
# Login
# ------------------------
@admin_router.post("/login", response_model=Token)
async def admin_login(form_data: AdminLoginIn):
    admin = await db.admins.find_one({"username": form_data.username})
    if not admin or not verify_password(form_data.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token({"sub": admin["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------------
# List users
# ------------------------
@admin_router.get("/users", response_model=list[UserOut])
async def list_users(current_admin: dict = Depends(get_current_admin)):
    users_cursor = db.users.find({}, {"password": 0})
    users = []
    async for u in users_cursor:
        users.append({
            "username": u.get("username"),
            "email": u.get("email"),
            "id": str(u.get("_id"))
        })
    return users

# ------------------------
# Delete user
# ------------------------
@admin_router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user id")

    result = await db.users.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)

# ------------------------
# Update user
# ------------------------
@admin_router.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: str, payload: UserUpdateIn, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user id")

    update_doc = {}
    if payload.username is not None:
        update_doc["username"] = payload.username
    if payload.email is not None:
        update_doc["email"] = payload.email
    if payload.password is not None:
        if len(payload.password.encode('utf-8')) > 72:
            raise HTTPException(status_code=400, detail="Password too long")
        update_doc["password"] = get_password_hash(payload.password)

    if not update_doc:
        raise HTTPException(status_code=400, detail="Nothing to update")

    result = await db.users.update_one({"_id": oid}, {"$set": update_doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    u = await db.users.find_one({"_id": oid}, {"password": 0})
    return {
        "username": u.get("username"),
        "email": u.get("email"),
        "id": str(u.get("_id"))
    }


# ------------------------
# List meetings (admin)
# ------------------------
@admin_router.get("/meetings")
async def list_meetings(current_admin: dict = Depends(get_current_admin)):
    """
    Return all meetings to admin.
    Each meeting returned with id (string), name, email, agenda, date, created_at.
    """
    meetings_cursor = db.meetings.find({})
    meetings = []
    async for m in meetings_cursor:
        meetings.append({
            "id": str(m.get("_id")),
            "name": m.get("name"),
            "email": m.get("email"),
            "agenda": m.get("agenda"),
            "date": m.get("date"),
            "created_at": m.get("created_at").isoformat() if m.get("created_at") else None
        })
    return meetings


# ------------------------
# Delete meeting?=
# ------------------------
@admin_router.delete("/meetings/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(meeting_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid meeting id")

    result = await db.meetings.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return Response(status_code=204)


@admin_router.get("/me")
async def admin_me(current_admin: dict = Depends(get_current_admin)):
    return {"username": current_admin.get("username")}


# ------------------------
# List audits
# ------------------------
@admin_router.get("/audits")
async def list_audits(current_admin: dict = Depends(get_current_admin)):
    audits_cursor = db.audits.find({})
    audits = []
    async for a in audits_cursor:
        audits.append({
            "id": str(a.get("_id")),
            "firstname": a.get("firstname"),
            "lastname": a.get("lastname"),
            "email": a.get("email"),
            "brandname": a.get("brandname"),
            "producturl": a.get("producturl"),
            "message": a.get("message"),
            "created_at": a.get("created_at").isoformat() if a.get("created_at") else None
        })
    return audits

# ------------------------
# Delete audit
# ------------------------
@admin_router.delete("/audits/{audit_id}", status_code=204)
async def delete_audit(audit_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(audit_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid audit id")
    result = await db.audits.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Audit not found")
    return Response(status_code=204)



# ------------------------
# List contacts
# ------------------------
@admin_router.get("/contacts")
async def list_contacts(current_admin: dict = Depends(get_current_admin)):
    contacts_cursor = db.contacts.find({})
    contacts = []
    async for c in contacts_cursor:
        contacts.append({
            "id": str(c.get("_id")),
            "firstname": c.get("firstname"),
            "email": c.get("email"),
            "subject": c.get("subject"),
            "message": c.get("message"),
            "created_at": c.get("created_at").isoformat() if c.get("created_at") else None
        })
    return contacts


# ------------------------
# Delete contact
# ------------------------
@admin_router.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(contact_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(contact_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid contact id")

    result = await db.contacts.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    return Response(status_code=204)


# ------------------------
# List newsletters
# ------------------------
@admin_router.get("/newsletters")
async def list_newsletters(current_admin: dict = Depends(get_current_admin)):
    cursor = db.newsletters.find({})
    out = []
    async for n in cursor:
        out.append({
            "id": str(n.get("_id")),
            "email": n.get("email"),
            "created_at": n.get("created_at").isoformat() if n.get("created_at") else None
        })
    return out


# ------------------------
# Delete newsletter
# ------------------------
@admin_router.delete("/newsletters/{nid}", status_code=204)
async def delete_newsletter(nid: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(nid)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")
    result = await db.newsletters.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(status_code=204)



# ------------------------
# List package requests
# ------------------------
@admin_router.get("/packages")
async def list_packages(current_admin: dict = Depends(get_current_admin)):
    cursor = db.packages.find({})
    packages = []
    async for p in cursor:
        packages.append({
            "id": str(p.get("_id")),
            "name": p.get("name"),
            "email": p.get("email"),
            "package": p.get("package"),
            "price": p.get("price"),
            "company": p.get("company"),
            "url": p.get("url"),
            "businessType": p.get("businessType"),
            "notes": p.get("notes"),
            "created_at": p.get("created_at").isoformat() if p.get("created_at") else None
        })
    return packages


# ------------------------
# Delete package request
# ------------------------
@admin_router.delete("/packages/{package_id}", status_code=204)
async def delete_package(package_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(package_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid package id")

    result = await db.packages.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Package not found")
    return Response(status_code=204)
