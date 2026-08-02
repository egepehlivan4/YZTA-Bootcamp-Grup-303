"""
FloraGuard — Rol Bazlı Erişim Kontrolü (RBAC)
FastAPI dependency'leri olarak sunulur: `get_current_user` her korumalı endpoint'te
token'ı çözer; `require_role(...)` belirli rollerle sınırlı endpoint'ler için
kullanılır (ör. yalnızca ADVISOR/ADMIN başka çiftçinin geçmişini görebilir).
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.config import Settings, get_settings
from src.data.schemas import Role, TokenPayload
from src.security.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> TokenPayload:
    try:
        return decode_access_token(token, settings.jwt_secret_key, settings.jwt_algorithm)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_role(*allowed_roles: Role):
    """`Depends(require_role(Role.ADVISOR, Role.ADMIN))` şeklinde kullanılır."""

    def _checker(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için yetkiniz yok. Gerekli rol(ler): {[r.value for r in allowed_roles]}",
            )
        return current_user

    return _checker


# ---------------------------------------------------------------------------
# Kayıt görüntüleme/düzenleme politikası
#
# Görüntüleme: Çiftçi yalnızca kendi geçmişini görür; Danışman kendi geçmişini
# ve çiftçilerin geçmişini görür (başka danışman/admin'inkini göremez); Admin
# herkesi görür.
#
# Düzenleme/silme: Çiftçi hiçbir kaydı düzenleyemez/silemez (salt okunur);
# Danışman yalnızca çiftçi kayıtlarını düzenleyip silebilir; Admin hem çiftçi
# hem danışman kayıtlarını düzenleyip silebilir.
#
# `target_role`/`owner_role` None ise (farmer_id sistemde kayıtlı bir kullanıcıya
# ait değilse — ör. serbest metin girişi), çiftçi gibi ele alınır: bu kimlik bir
# gerçek çiftçiyi temsil ettiği varsayılır, danışman/admin erişimi engellenmez.
# ---------------------------------------------------------------------------

def can_view_farmer_history(current_user: TokenPayload, target_farmer_id: str, target_role: Role | None) -> bool:
    if current_user.role == Role.ADMIN:
        return True
    if current_user.sub == target_farmer_id:
        return True
    if current_user.role == Role.ADVISOR:
        return target_role in (None, Role.FARMER)
    return False  # Role.FARMER, kendisi değil


def can_modify_record(current_user: TokenPayload, owner_role: Role | None) -> bool:
    if current_user.role == Role.FARMER:
        return False
    if current_user.role == Role.ADVISOR:
        return owner_role in (None, Role.FARMER)
    if current_user.role == Role.ADMIN:
        return owner_role in (None, Role.FARMER, Role.ADVISOR)
    return False
