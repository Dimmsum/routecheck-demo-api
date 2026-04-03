from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gotrue.errors import AuthApiError
from database import supabase

router = APIRouter(prefix="/auth")


class SignUpRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup", status_code=201)
def signup(body: SignUpRequest):
    try:
        res = supabase.auth.sign_up({"email": body.email, "password": body.password})
        if res.session is None:
            raise HTTPException(status_code=400, detail="Email confirmation required — disable it in Supabase Auth settings")
        return {"access_token": res.session.access_token, "token_type": "bearer"}
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(body: LoginRequest):
    try:
        res = supabase.auth.sign_in_with_password({"email": body.email, "password": body.password})
        return {"access_token": res.session.access_token, "token_type": "bearer"}
    except AuthApiError as e:
        raise HTTPException(status_code=401, detail=str(e))
