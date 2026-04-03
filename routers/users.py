from fastapi import APIRouter, Depends, HTTPException
from auth import require_auth
from models import UserCreate, UserUpdate

router = APIRouter(prefix="/users")

_users = {}
_next_id = 1


@router.get("")
def list_users():
    return {"users": list(_users.values())}


@router.post("", status_code=201)
def create_user(body: UserCreate, token: str = Depends(require_auth)):
    global _next_id
    user = {"id": _next_id, **body.model_dump()}
    _users[_next_id] = user
    _next_id += 1
    return user


@router.get("/{user_id}")
def get_user(user_id: int):
    user = _users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}")
def update_user(user_id: int, body: UserUpdate, token: str = Depends(require_auth)):
    user = _users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated = {**user, **{k: v for k, v in body.model_dump().items() if v is not None}}
    _users[user_id] = updated
    return updated


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, token: str = Depends(require_auth)):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    del _users[user_id]
