from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from fastapi import HTTPException, Request, status
from sqlalchemy import select

from app.core.config import settings
from app.db.models import UserORM
from app.db.session import SessionLocal
from app.schemas.models import AuthLoginRequest, AuthLoginResponse, UserProfile


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def _sign(payload: str) -> str:
    return hmac.new(settings.auth_token_secret.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).hexdigest()


def _issue_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.auth_token_ttl_seconds,
    }
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return f"{encoded_payload}.{_sign(encoded_payload)}"


def _verify_token(token: str) -> str:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态无效") from exc

    expected = _sign(encoded_payload)
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态无效")

    try:
        payload: dict[str, Any] = json.loads(_base64url_decode(encoded_payload))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态无效") from exc

    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期")

    user_id = str(payload.get("sub") or "")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态无效")
    return user_id


def _user_to_schema(row: UserORM) -> UserProfile:
    return UserProfile(id=row.id, openid=row.openid, nickname=row.nickname, avatarUrl=row.avatar_url)


def login_with_wechat(payload: AuthLoginRequest) -> AuthLoginResponse:
    code = payload.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="缺少微信登录 code")

    openid = f"local_{hashlib.sha256(code.encode('utf-8')).hexdigest()[:24]}"
    user_id = f"user_{hashlib.sha256(openid.encode('utf-8')).hexdigest()[:24]}"
    nickname = payload.nickname or "微信用户"
    avatar_url = payload.avatar_url or ""

    with SessionLocal() as session:
        row = session.scalar(select(UserORM).where(UserORM.openid == openid))
        if row is None:
            row = UserORM(id=user_id, openid=openid, nickname=nickname, avatar_url=avatar_url)
            session.add(row)
        else:
            row.nickname = nickname
            row.avatar_url = avatar_url
        session.commit()
        session.refresh(row)
        user = _user_to_schema(row)

    token = _issue_token(user.id)
    return AuthLoginResponse(token=token, accessToken=token, user=user, expiresIn=settings.auth_token_ttl_seconds)


def get_current_user_from_token(token: str) -> UserProfile:
    user_id = _verify_token(token)
    with SessionLocal() as session:
        row = session.get(UserORM, user_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
        return _user_to_schema(row)


def get_current_user(request: Request) -> UserProfile:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    return get_current_user_from_token(token)
