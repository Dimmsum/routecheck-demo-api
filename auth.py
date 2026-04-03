from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from gotrue.errors import AuthApiError
from database import supabase

bearer = HTTPBearer()


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        res = supabase.auth.get_user(credentials.credentials)
        return res.user.id
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
