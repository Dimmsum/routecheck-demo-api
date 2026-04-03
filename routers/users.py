from fastapi import APIRouter, Depends, HTTPException
from auth import require_auth
from models import UserCreate, UserUpdate
from database import supabase

router = APIRouter(prefix="/users")


@router.get("")
def list_users():
    res = supabase.table("users").select("*").execute()
    return {"users": res.data}


@router.post("", status_code=201)
def create_user(body: UserCreate, token: str = Depends(require_auth)):
    res = supabase.table("users").insert(body.model_dump()).execute()
    return res.data[0]


@router.get("/{user_id}")
def get_user(user_id: int):
    res = supabase.table("users").select("*").eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
    return res.data[0]


@router.put("/{user_id}")
def update_user(user_id: int, body: UserUpdate, token: str = Depends(require_auth)):
    res = supabase.table("users").select("id").eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    updated = supabase.table("users").update(updates).eq("id", user_id).execute()
    return updated.data[0]


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, token: str = Depends(require_auth)):
    res = supabase.table("users").select("id").eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
    supabase.table("users").delete().eq("id", user_id).execute()
