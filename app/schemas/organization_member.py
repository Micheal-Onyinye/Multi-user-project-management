from pydantic import BaseModel, Field, EmailStr

class AddMemberSchema(BaseModel):    
    email: EmailStr
    role: str = Field(..., example="member")


class OrganizationMemberResponse(BaseModel):
    id: int
    user_id: int
    role: str

    model_config = {
        "from_attributes": True
    }
