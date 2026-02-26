from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.schemas.auth import (
    RegisterRequest, MerchantRegisterRequest, LoginRequest,
    RefreshRequest, SendSmsRequest, UpdateProfileRequest, ChangePasswordRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-sms")
def send_sms(body: SendSmsRequest):
    auth_service.svc_send_sms(body.phone)
    return success({"message": "验证码已发送（演示固定：123456）"})


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    tokens = auth_service.svc_register(db, body.phone, body.password, body.sms_code)
    return success(tokens)


@router.post("/merchant-register")
def merchant_register(body: MerchantRegisterRequest, db: Session = Depends(get_db)):
    tokens = auth_service.svc_merchant_register(
        db, body.phone, body.password, body.sms_code,
        body.company_name, body.business_license,
    )
    return success(tokens)


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    tokens = auth_service.svc_login(db, body.phone, body.password)
    return success(tokens)


@router.post("/refresh")
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    result = auth_service.svc_refresh_token(db, body.refresh_token)
    return success(result)


@router.post("/logout")
def logout(current_user=Depends(get_current_user)):
    # TODO: token加黑名单（Redis），演示直接返回OK
    return success({"message": "已退出登录"})


@router.get("/profile")
def profile(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    data = auth_service.svc_get_profile(db, current_user.id)
    return success(data)


@router.put("/profile")
def update_profile(body: UpdateProfileRequest,
                   current_user=Depends(get_current_user),
                   db: Session = Depends(get_db)):
    data = auth_service.svc_update_profile(db, current_user.id, body.nickname, body.avatar)
    return success(data)


@router.post("/change-password")
def change_password(body: ChangePasswordRequest,
                    current_user=Depends(get_current_user),
                    db: Session = Depends(get_db)):
    auth_service.svc_change_password(db, current_user.id, body.old_password, body.new_password)
    return success({"message": "密码修改成功"})
