from pydantic import BaseModel
from datetime import datetime

class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    organization_id: int
    action: str
    description: str
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }
