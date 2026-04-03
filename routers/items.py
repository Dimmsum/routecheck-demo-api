from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from auth import require_auth
from models import ItemCreate, ItemUpdate
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


@router.get("/{item_id}")
def get_item(item_id: int):
    res = supabase.table("items").select("*").eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return res.data[0]


@router.put("/{item_id}")
def update_item(item_id: int, body: ItemUpdate, token: str = Depends(require_auth)):
    res = supabase.table("items").select("id").eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    updated = supabase.table("items").update(updates).eq("id", item_id).execute()
    return updated.data[0]


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, token: str = Depends(require_auth)):
    res = supabase.table("items").select("id").eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")
    supabase.table("items").delete().eq("id", item_id).execute()
