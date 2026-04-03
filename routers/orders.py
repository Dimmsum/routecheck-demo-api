from fastapi import APIRouter, Depends, HTTPException
from auth import require_auth
from models import OrderCreate
from database import supabase

router = APIRouter(prefix="/orders")


@router.get("")
def list_orders(token: str = Depends(require_auth)):
    res = supabase.table("orders").select("*").execute()
    return {"orders": res.data}


@router.post("", status_code=201)
def create_order(body: OrderCreate, token: str = Depends(require_auth)):
    data = {"status": "pending", **body.model_dump()}
    res = supabase.table("orders").insert(data).execute()
    return res.data[0]


@router.get("/{order_id}")
def get_order(order_id: int, token: str = Depends(require_auth)):
    res = supabase.table("orders").select("*").eq("id", order_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Order not found")
    return res.data[0]
