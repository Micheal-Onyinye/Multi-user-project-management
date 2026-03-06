from pydantic import BaseModel, EmailStr, Field

class InviteUserSchema(BaseModel):
    email: EmailStr
    role: str = Field(..., example="member")


class InvitationResponse(BaseModel):
    id: int
    email: str
    role: str
    status: str

    model_config = {
        "from_attributes": True
    }
