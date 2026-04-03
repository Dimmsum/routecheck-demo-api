from fastapi import APIRouter, Depends, HTTPException
from auth import require_auth
from models import ItemCreate, ItemUpdate

router = APIRouter(prefix="/items")

_items = {}
_next_id = 1


@router.get("")
def list_items(in_stock: bool = None):
    items = list(_items.values())
    if in_stock is not None:
        items = [i for i in items if i["in_stock"] == in_stock]
    return {"items": items}


@router.post("", status_code=201)
def create_item(body: ItemCreate, token: str = Depends(require_auth)):
    global _next_id
    item = {"id": _next_id, **body.model_dump()}
    _items[_next_id] = item
    _next_id += 1
    return item


@router.get("/{item_id}")
def get_item(item_id: int):
    item = _items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}")
def update_item(item_id: int, body: ItemUpdate, token: str = Depends(require_auth)):
    item = _items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = {**item, **{k: v for k, v in body.model_dump().items() if v is not None}}
    _items[item_id] = updated
    return updated


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, token: str = Depends(require_auth)):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
