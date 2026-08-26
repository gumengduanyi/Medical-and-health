from fastapi import APIRouter, Depends

from app.schemas.models import AuthLoginRequest, AuthLoginResponse, UserProfile
from app.services.auth_service import get_current_user, login_with_wechat

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/wechat-login", response_model=AuthLoginResponse)
def wechat_login(payload: AuthLoginRequest):
    return login_with_wechat(payload)


@router.get("/me", response_model=UserProfile)
def me(user: UserProfile = Depends(get_current_user)):
    return user


@router.post("/logout")
def logout():
    return {"message": "已退出登录"}
