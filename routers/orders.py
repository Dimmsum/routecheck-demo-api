from fastapi import APIRouter, Depends, HTTPException
from auth import require_auth
from models import OrderCreate

router = APIRouter(prefix="/orders")

_orders = {}
_next_id = 1


@router.get("")
def list_orders(token: str = Depends(require_auth)):
    return {"orders": list(_orders.values())}


@router.post("", status_code=201)
def create_order(body: OrderCreate, token: str = Depends(require_auth)):
    global _next_id
    order = {"id": _next_id, "status": "pending", **body.model_dump()}
    _orders[_next_id] = order
    _next_id += 1
    return order


@router.get("/{order_id}")
def get_order(order_id: int, token: str = Depends(require_auth)):
    order = _orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
