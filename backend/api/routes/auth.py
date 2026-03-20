"""Auth routes using Supabase Auth."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.db import supabase as db
from backend.api.deps import get_current_user

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""
    institution: str = ""
    research_focus: list[str] = []
    clinical_background: bool = False


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
async def signup(req: SignupRequest):
    try:
        client = db.get_client()
        result = client.auth.sign_up({"email": req.email, "password": req.password})
        if not result.user:
            raise HTTPException(status_code=400, detail="Signup failed")

        # Create user profile
        db.insert("user_profiles", {
            "id": result.user.id,
            "full_name": req.full_name,
            "institution": req.institution,
            "research_focus": req.research_focus,
            "clinical_background": req.clinical_background,
        }, service=True)

        return {"user_id": result.user.id, "session": result.session.access_token if result.session else None}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(req: LoginRequest):
    try:
        client = db.get_client()
        result = client.auth.sign_in_with_password({"email": req.email, "password": req.password})
        if not result.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "access_token": result.session.access_token,
            "user_id": result.user.id,
            "email": result.user.email,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    return {"success": True}


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    profiles = db.select("user_profiles", filters={"id": user["id"]}, service=True)
    return profiles[0] if profiles else user


@router.put("/profile")
async def update_profile(data: dict, user: dict = Depends(get_current_user)):
    allowed = {"full_name", "institution", "research_focus", "clinical_background"}
    update_data = {k: v for k, v in data.items() if k in allowed}
    if update_data:
        db.update("user_profiles", user["id"], update_data, service=True)
    return {"success": True}
