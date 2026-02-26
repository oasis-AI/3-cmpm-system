from pydantic import BaseModel, Field
from typing import Optional


class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    password: str = Field(..., min_length=6, max_length=20)
    sms_code: str = Field(..., min_length=4, max_length=6)


class MerchantRegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    password: str = Field(..., min_length=6, max_length=20)
    sms_code: str = Field(..., min_length=4, max_length=6)
    company_name: str = Field(..., min_length=2, max_length=100)
    business_license: str = Field(..., min_length=5, max_length=100)


class LoginRequest(BaseModel):
    phone: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class SendSmsRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    phone: str
    nickname: str
    avatar: Optional[str] = None
    role: str
    points_balance: int
    merchant_id: Optional[int] = None

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=20)
