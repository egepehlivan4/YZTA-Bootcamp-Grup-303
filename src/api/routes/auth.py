"""FloraGuard — Kimlik Doğrulama Endpoint'i (JWT üretimi)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.config import Settings, get_settings
from src.data.schemas import Role, Token
from src.security.auth import authenticate_user, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    settings: Settings = Depends(get_settings),
) -> Token:
    """
    OAuth2 password flow. Demo kullanıcılar (bkz. `security/users_db.py`):
    ciftci1/ciftci123 (farmer), danisman1/danisman123 (advisor), admin1/admin123 (admin).
    """
    user = authenticate_user(settings.db_path, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = Role(user["role"])
    access_token = create_access_token(
        username=user["username"],
        role=role,
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.access_token_expire_minutes,
    )
    return Token(access_token=access_token, role=role)
