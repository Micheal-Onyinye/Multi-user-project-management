from pydantic import BaseModel, Field, EmailStr
    email: EmailStr
    role: str = Field(..., example="member")


class OrganizationMemberResponse(BaseModel):
    id: int
    user_id: int
    role: str

    class Config:
        orm_mode = True
