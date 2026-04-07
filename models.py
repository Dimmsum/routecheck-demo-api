from pydantic import BaseModel
from typing import Optional


class ItemCreate(BaseModel):
    title: str
    description: str
    price: float
    in_stock: bool


class OrderCreate(BaseModel):
    item_id: int
    quantity: int
    shipping_address: str
