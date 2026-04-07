from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from auth import require_auth
from models import ItemCreate
from database import supabase

router = APIRouter(prefix="/items")


@router.get("")
def list_items(in_stock: Optional[bool] = None):
    query = supabase.table("items").select("*")
    if in_stock is not None:
        query = query.eq("in_stock", in_stock)
    res = query.execute()
    return {"items": res.data}


@router.post("", status_code=201)
def create_item(body: ItemCreate, token: str = Depends(require_auth)):
    res = supabase.table("items").insert(body.model_dump()).execute()
    return res.data[0]
