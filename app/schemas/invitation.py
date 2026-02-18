from pydantic import BaseModel, EmailStr, Field

class InviteUserSchema(BaseModel):
    email: EmailStr
    role: str = Field(..., example="member")


class InvitationResponse(BaseModel):
    id: int
    email: str
    role: str
    status: str

    class Config:
        orm_mode = True
