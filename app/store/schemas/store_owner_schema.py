from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import date, datetime


class StoreOwnerBase(BaseModel):
    full_name: str = Field(..., max_length=100,
                           description="Full name of the store owner")
    dob: date
    gender_id: int
    email: EmailStr
    mobile: str = Field(..., max_length=15, pattern=r"^\+?\d{10,15}$")
    phone: Optional[str] = Field(
        None, max_length=15, pattern=r"^\+?\d{10,15}$")
    current_addr: str = Field(..., max_length=255)
    permanent_addr: str = Field(None, max_length=255)
    created_by: int
    updated_by: Optional[int] = None


class StoreOwnerResponse(StoreOwnerBase):
    id: int
    age: int
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True


class StoreOwnerGetRequest(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)
